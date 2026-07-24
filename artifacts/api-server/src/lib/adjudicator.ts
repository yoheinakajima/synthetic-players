/**
 * Claim adjudicator — mechanically checks structured claim predicates against
 * experimental evidence and issues supported / refuted / inconclusive / untested
 * verdicts with effect sizes.
 *
 * A claim predicate is a conjunction (`all`) of items. Each item names a metric,
 * a comparison operator, and a threshold, plus a scope that selects which
 * experiments count as evidence. Verdict rules:
 *
 *   - Evidence with sampling variance (n ≥ 2, sd > 0): compare the 95% t-interval
 *     against the threshold. Supported only when the whole interval satisfies the
 *     comparison; refuted only when the whole interval violates it; otherwise
 *     inconclusive.
 *   - Deterministic evidence (n = 1, or sd = 0 across replicates): exact point
 *     comparison — supported or refuted, never inconclusive.
 *   - No matching evidence: untested.
 *
 * Claim verdict: refuted if ANY item refuted; else untested if any item lacks
 * evidence; else inconclusive if any item inconclusive; else supported.
 *
 * Effect size: one-sample Cohen's d = (mean − threshold) / sd where sd > 0;
 * for deterministic evidence the raw margin (mean − threshold) is reported instead.
 */

import { eq, isNotNull, inArray } from "drizzle-orm";
import {
  db,
  experimentsTable,
  analysesTable,
  strategiesTable,
  gamesTable,
  roundsTable,
} from "@workspace/db";
import { flattenMetrics, type MetricsV2 } from "./metrics";
import { computeForkComparison, flattenForkComparison } from "./fork-metrics";
import type { GameDef } from "./game-engine";

// ── Predicate types ────────────────────────────────────────────────────────

/**
 * Selects FORKS of the parents matched by the outer scope. When present, the
 * item is adjudicated on paired parent-vs-fork post-fork-window metrics (the
 * `postFork.*` namespace) — one value per (parent, fork) pair. Omitted
 * strategy slugs mean "same as the parent" (unswapped seat).
 */
export interface ForkScope {
  forkRound: number;
  /** Fork's P1 strategy slug; omitted = unswapped (same as parent P1). */
  player1StrategySlug?: string;
  /** Fork's P2 strategy slug; omitted = unswapped (same as parent P2). */
  player2StrategySlug?: string;
  /** Fork batch label (as assigned by fork-batch). */
  batchLabel?: string;
}

export interface PredicateScope {
  gameId?: number;
  /** Match by game slug (stable across databases, unlike numeric ids). */
  gameSlug?: string;
  player1StrategySlug?: string;
  player2StrategySlug?: string;
  /** Match player1/player2 slugs in either seat order. Not honored for fork items (seat identity matters for swaps). */
  eitherOrder?: boolean;
  /** At least one seat's strategy is in this list. */
  anyStrategySlugs?: string[];
  /** Both seats' strategies are in this list. */
  pairFromSlugs?: string[];
  batchLabel?: string;
  /** Pool evidence across several batch labels (row matches if its label is in the list). */
  batchLabels?: string[];
  /** Resolves metric names ending in "Focus"/"Opponent" to the seat this strategy occupies. */
  focusStrategySlug?: string;
  /** When set, this item runs on paired parent-vs-fork evidence instead of whole-run analyses. */
  fork?: ForkScope;
}

export interface PredicateItem {
  /** Metric key from the flattened v2 metrics map. May end in "Focus" or "Opponent" when scope.focusStrategySlug is set. */
  metric: string;
  op: ">" | ">=" | "<" | "<=" | "between" | "approx";
  threshold: number;
  thresholdHigh?: number; // for "between"
  tolerance?: number; // for "approx"
  scope?: PredicateScope; // overrides the claim-level scope for this item
  label?: string;

  // ── Phase 3 extensions (schema frozen before claim registration) ─────────
  /**
   * threshold      — metric in one scope vs a constant (default; original behavior)
   * diffScopes     — mean(scope A) − mean(scope B) vs threshold (Welch 95% CI unless evaluate:"point" or absolute)
   * ratioScopes    — mean(scope A) / mean(scope B) vs threshold (always point; see ratioEdge for zero denominators)
   * orderedScopes  — means across scopesOrdered must be non-decreasing (point; op/threshold ignored)
   * metricVsMetric — mean(metric) − mean(metricB) within one scope vs threshold (point)
   */
  kind?: "threshold" | "diffScopes" | "ratioScopes" | "orderedScopes" | "metricVsMetric";
  /**
   * experiment   — one value per experiment (Focus/Opponent suffix resolution; in self-play,
   *                Focus = mean of both seats so the supergame stays the independence cluster)
   * seatDecision — one value per (experiment, seat occupied by focusStrategySlug); metric key
   *                is given WITHOUT the P1/P2 suffix
   */
  aggregate?: "experiment" | "seatDecision";
  /** ci (default where variance exists) or point — pre-registered per item. */
  evaluate?: "ci" | "point";
  /** Comparator scope for diffScopes / ratioScopes (merged over the claim scope). */
  scopeB?: PredicateScope;
  /** Second metric for metricVsMetric. */
  metricB?: string;
  /** Ordered scopes for orderedScopes (first expected lowest). */
  scopesOrdered?: PredicateScope[];
  /** diffScopes: compare |meanA − meanB| instead of the signed difference (forces point evaluation). */
  absolute?: boolean;
  /** ratioScopes: how to adjudicate when the denominator mean is exactly 0. */
  ratioEdge?: { denomZero: { numerAtLeast: number } };
}

export interface ClaimPredicate {
  scope: PredicateScope;
  all: PredicateItem[];
  minExperiments?: number; // default 1
}

export type Verdict = "supported" | "refuted" | "inconclusive" | "untested";

export interface ItemAdjudication {
  label: string;
  metric: string;
  op: string;
  threshold: number;
  thresholdHigh?: number;
  tolerance?: number;
  n: number;
  mean: number | null;
  sd: number | null;
  ciLow: number | null;
  ciHigh: number | null;
  /** One-sample Cohen's d vs threshold (n ≥ 2, sd > 0 only). */
  effectSize: number | null;

  /** mean − threshold; the deterministic-evidence effect measure. */
  margin: number | null;
  verdict: Verdict;
  evidenceExperimentIds: number[];
  note?: string;
}

export interface AdjudicationRecord {
  verdict: Verdict;
  adjudicatedAt: string;
  items: ItemAdjudication[];
  note: string;
  /**
   * True when the claim was registered AFTER the earliest experiment used as
   * its evidence — a disclosed post-hoc claim (the v1/v2 backfill corpus).
   * Pre-registered studies (Phase 3) must show false. Computed from
   * timestamps at every adjudication; never hand-set.
   */
  postRegistered?: boolean;
  claimCreatedAt?: string | null;
  earliestEvidenceAt?: string | null;
}

// ── Statistics ─────────────────────────────────────────────────────────────

/** Two-sided 95% t critical values by degrees of freedom. */
/**
 * Below this sample standard deviation, replicates are treated as identical
 * (deterministic evidence): float accumulation across byte-identical runs can
 * leave sd ~1e-18, which would degenerate the t-CI and explode effect sizes.
 */
const SD_EPSILON = 1e-12;

const T_TABLE: Array<[number, number]> = [
  [1, 12.706], [2, 4.303], [3, 3.182], [4, 2.776], [5, 2.571], [6, 2.447],
  [7, 2.365], [8, 2.306], [9, 2.262], [10, 2.228], [11, 2.201], [12, 2.179],
  [13, 2.16], [14, 2.145], [15, 2.131], [16, 2.12], [17, 2.11], [18, 2.101],
  [19, 2.093], [20, 2.086], [25, 2.06], [30, 2.042], [40, 2.021], [60, 2.0],
  [120, 1.98],
];

function tCritical95(df: number): number {
  if (df <= 0) return NaN;
  for (const [d, t] of T_TABLE) if (df <= d) return t;
  return 1.96;
}

export interface SampleStats {
  n: number;
  mean: number | null;
  sd: number | null;
  ciLow: number | null;
  ciHigh: number | null;
}

export function sampleStats(values: number[]): SampleStats {
  const n = values.length;
  if (n === 0) return { n: 0, mean: null, sd: null, ciLow: null, ciHigh: null };
  const mean = values.reduce((s, v) => s + v, 0) / n;
  if (n === 1) return { n, mean, sd: null, ciLow: null, ciHigh: null };
  const variance = values.reduce((s, v) => s + (v - mean) ** 2, 0) / (n - 1);
  const sd = Math.sqrt(variance);
  const half = tCritical95(n - 1) * (sd / Math.sqrt(n));
  return { n, mean, sd, ciLow: mean - half, ciHigh: mean + half };
}

export interface WelchResult {
  diff: number;
  ciLow: number;
  ciHigh: number;
  df: number;
}

/**
 * Welch two-sample 95% CI for mean(A) − mean(B) (unequal variances,
 * Welch–Satterthwaite df). Valid even when ONE side has zero variance (the
 * CI then comes entirely from the other side's sampling error). Returns null
 * when either side has n < 2 or BOTH sides are (near-)deterministic — those
 * cases must fall back to an exact point comparison.
 */
export function welch95(a: SampleStats, b: SampleStats): WelchResult | null {
  if (a.n < 2 || b.n < 2 || a.mean == null || b.mean == null) return null;
  const sdA = a.sd ?? 0;
  const sdB = b.sd ?? 0;
  if (sdA < SD_EPSILON && sdB < SD_EPSILON) return null;
  const vA = (sdA * sdA) / a.n;
  const vB = (sdB * sdB) / b.n;
  const se = Math.sqrt(vA + vB);
  const dfDenom =
    (vA > 0 ? (vA * vA) / (a.n - 1) : 0) + (vB > 0 ? (vB * vB) / (b.n - 1) : 0);
  const df = dfDenom > 0 ? ((vA + vB) * (vA + vB)) / dfDenom : a.n + b.n - 2;
  const t = tCritical95(Math.max(1, Math.floor(df)));
  const diff = a.mean - b.mean;
  return { diff, ciLow: diff - t * se, ciHigh: diff + t * se, df };
}

// ── Evidence selection ─────────────────────────────────────────────────────

interface EvidenceRow {
  experimentId: number;
  createdAt: string | null;
  gameId: number;
  gameSlug: string;
  p1Slug: string;
  p2Slug: string;
  batchLabel: string | null;
  flat: Record<string, number>;
}

let evidenceCache: EvidenceRow[] | null = null;

/** Load all completed experiments with v2 analyses, joined with strategy slugs. */
async function loadEvidence(): Promise<EvidenceRow[]> {
  if (evidenceCache) return evidenceCache;

  const experiments = await db
    .select()
    .from(experimentsTable)
    .where(eq(experimentsTable.status, "completed"));
  const analyses = await db.select().from(analysesTable);
  const strategies = await db.select().from(strategiesTable);
  const games = await db.select().from(gamesTable);

  const stratSlug = new Map(strategies.map((s) => [s.id, s.slug]));
  const gameSlugById = new Map(games.map((g) => [g.id, g.slug]));
  const analysisByExp = new Map(analyses.map((a) => [a.experimentId, a]));

  const rows: EvidenceRow[] = [];
  for (const exp of experiments) {
    // Fork-lineage experiments are exploratory, never evidence: a fork's
    // history is a hybrid (parent prefix + post-fork suffix, possibly with a
    // swapped strategy), so its whole-run metrics are not a clean sample of
    // the labeled matchup.
    if (exp.parentExperimentId != null) continue;
    const analysis = analysisByExp.get(exp.id);
    if (!analysis || analysis.analysisVersion < 2 || !analysis.metricsJson) continue;
    let flat: Record<string, number>;
    try {
      flat = flattenMetrics(JSON.parse(analysis.metricsJson) as MetricsV2);
    } catch {
      continue;
    }
    rows.push({
      experimentId: exp.id,
      createdAt: exp.createdAt ? new Date(exp.createdAt).toISOString() : null,
      gameId: exp.gameId,
      gameSlug: gameSlugById.get(exp.gameId) ?? "unknown",
      p1Slug: stratSlug.get(exp.player1StrategyId) ?? "unknown",
      p2Slug: stratSlug.get(exp.player2StrategyId) ?? "unknown",
      batchLabel: exp.batchLabel,
      flat,
    });
  }
  evidenceCache = rows;
  return rows;
}

// ── Fork-pair evidence ─────────────────────────────────────────────────────

interface ForkEvidenceRow {
  forkExperimentId: number;
  parentExperimentId: number;
  gameId: number;
  gameSlug: string;
  parentP1Slug: string;
  parentP2Slug: string;
  forkP1Slug: string;
  forkP2Slug: string;
  parentBatchLabel: string | null;
  forkBatchLabel: string | null;
  forkRound: number;
  flat: Record<string, number>;
}

let forkEvidenceCache: ForkEvidenceRow[] | null = null;

/**
 * Load all completed fork experiments paired with their parents, with
 * post-fork-window metrics computed from stored rounds. Forks stay excluded
 * from the whole-run pool; this paired pool is the ONLY way they enter
 * adjudication.
 */
async function loadForkEvidence(): Promise<ForkEvidenceRow[]> {
  if (forkEvidenceCache) return forkEvidenceCache;

  const forks = await db
    .select()
    .from(experimentsTable)
    .where(isNotNull(experimentsTable.parentExperimentId));

  const usable = forks.filter(
    (f) => f.status === "completed" && f.forkRound != null && f.parentExperimentId != null
  );
  if (usable.length === 0) {
    forkEvidenceCache = [];
    return forkEvidenceCache;
  }

  const parentIds = [...new Set(usable.map((f) => f.parentExperimentId!))];
  const parents = await db
    .select()
    .from(experimentsTable)
    .where(inArray(experimentsTable.id, parentIds));
  const parentById = new Map(parents.map((p) => [p.id, p]));

  const games = await db.select().from(gamesTable);
  const gameById = new Map(
    games.map((g) => [
      g.id,
      {
        id: g.id,
        slug: g.slug,
        numActions: g.numActions,
        actionLabels: JSON.parse(g.actionLabels) as string[],
        payoffMatrix: JSON.parse(g.payoffMatrix) as number[][][],
        nashEquilibria: JSON.parse(g.nashEquilibria) as number[][],
        category: g.category,
      } as GameDef & { category: string },
    ])
  );

  const strategies = await db.select().from(strategiesTable);
  const stratSlug = new Map(strategies.map((s) => [s.id, s.slug]));

  const allExpIds = [...new Set([...usable.map((f) => f.id), ...parentIds])];
  const allRounds = await db
    .select()
    .from(roundsTable)
    .where(inArray(roundsTable.experimentId, allExpIds));
  const roundsByExp = new Map<number, typeof allRounds>();
  for (const r of allRounds) {
    const list = roundsByExp.get(r.experimentId) ?? [];
    list.push(r);
    roundsByExp.set(r.experimentId, list);
  }

  const rows: ForkEvidenceRow[] = [];
  for (const fork of usable) {
    const parent = parentById.get(fork.parentExperimentId!);
    if (!parent || parent.status !== "completed") continue;
    // A fork of a fork would pair against a hybrid baseline; only first-order
    // forks (parent is a non-fork) are evidence-grade.
    if (parent.parentExperimentId != null) continue;
    const gameDef = gameById.get(fork.gameId);
    const parentRounds = roundsByExp.get(parent.id);
    const forkRounds = roundsByExp.get(fork.id);
    if (!gameDef || !parentRounds?.length || !forkRounds?.length) continue;
    try {
      const cmp = computeForkComparison(gameDef, parentRounds, forkRounds, fork.forkRound!);
      rows.push({
        forkExperimentId: fork.id,
        parentExperimentId: parent.id,
        gameId: fork.gameId,
        gameSlug: gameDef.slug,
        parentP1Slug: stratSlug.get(parent.player1StrategyId) ?? "unknown",
        parentP2Slug: stratSlug.get(parent.player2StrategyId) ?? "unknown",
        forkP1Slug: stratSlug.get(fork.player1StrategyId) ?? "unknown",
        forkP2Slug: stratSlug.get(fork.player2StrategyId) ?? "unknown",
        parentBatchLabel: parent.batchLabel,
        forkBatchLabel: fork.batchLabel,
        forkRound: fork.forkRound!,
        flat: flattenForkComparison(cmp),
      });
    } catch {
      continue; // malformed pair (e.g. missing window) is never silently scored
    }
  }
  forkEvidenceCache = rows;
  return rows;
}

function matchesForkScope(row: ForkEvidenceRow, scope: PredicateScope): boolean {
  const fork = scope.fork!;
  // Outer scope selects the PARENT (matchup, game, parent batch).
  if (
    !matchesScope(
      {
        gameId: row.gameId,
        gameSlug: row.gameSlug,
        p1Slug: row.parentP1Slug,
        p2Slug: row.parentP2Slug,
        batchLabel: row.parentBatchLabel,
      },
      { ...scope, fork: undefined, eitherOrder: false }
    )
  ) {
    return false;
  }
  if (row.forkRound !== fork.forkRound) return false;
  const wantP1 = fork.player1StrategySlug ?? row.parentP1Slug;
  const wantP2 = fork.player2StrategySlug ?? row.parentP2Slug;
  if (row.forkP1Slug !== wantP1 || row.forkP2Slug !== wantP2) return false;
  if (fork.batchLabel != null && row.forkBatchLabel !== fork.batchLabel) return false;
  return true;
}

/** Among matching forks, keep the newest per parent so a re-forked pair is not double-counted. */
function dedupeForksPerParent(rows: ForkEvidenceRow[]): ForkEvidenceRow[] {
  const byParent = new Map<number, ForkEvidenceRow>();
  for (const row of rows) {
    const prev = byParent.get(row.parentExperimentId);
    if (!prev || row.forkExperimentId > prev.forkExperimentId) {
      byParent.set(row.parentExperimentId, row);
    }
  }
  return [...byParent.values()];
}

/** Invalidate the evidence caches (call after new experiments/analyses/forks are written). */
export function invalidateEvidenceCache(): void {
  evidenceCache = null;
  forkEvidenceCache = null;
}

interface MatchableRow {
  gameId: number;
  gameSlug: string;
  p1Slug: string;
  p2Slug: string;
  batchLabel: string | null;
}

function matchesScope(row: MatchableRow, scope: PredicateScope): boolean {
  if (scope.gameId != null && row.gameId !== scope.gameId) return false;
  if (scope.gameSlug != null && row.gameSlug !== scope.gameSlug) return false;
  if (scope.batchLabel != null && row.batchLabel !== scope.batchLabel) return false;
  if (scope.batchLabels != null && scope.batchLabels.length > 0) {
    if (row.batchLabel == null || !scope.batchLabels.includes(row.batchLabel)) return false;
  }

  if (scope.player1StrategySlug != null || scope.player2StrategySlug != null) {
    const direct =
      (scope.player1StrategySlug == null || row.p1Slug === scope.player1StrategySlug) &&
      (scope.player2StrategySlug == null || row.p2Slug === scope.player2StrategySlug);
    const swapped =
      (scope.player1StrategySlug == null || row.p2Slug === scope.player1StrategySlug) &&
      (scope.player2StrategySlug == null || row.p1Slug === scope.player2StrategySlug);
    if (!(direct || (scope.eitherOrder === true && swapped))) return false;
  }

  if (scope.anyStrategySlugs != null && scope.anyStrategySlugs.length > 0) {
    if (!scope.anyStrategySlugs.includes(row.p1Slug) && !scope.anyStrategySlugs.includes(row.p2Slug)) {
      return false;
    }
  }

  if (scope.pairFromSlugs != null && scope.pairFromSlugs.length > 0) {
    if (!scope.pairFromSlugs.includes(row.p1Slug) || !scope.pairFromSlugs.includes(row.p2Slug)) {
      return false;
    }
  }

  return true;
}

/**
 * Resolve an experiment-level metric value, honoring Focus/Opponent suffixes.
 * In SELF-PLAY (both seats are the focus strategy) a Focus metric is the mean
 * of both seats' values — the supergame remains the independence cluster and
 * both sampled decisions inform the estimate. Opponent metrics are likewise
 * the mean in self-play (each seat's opponent is the other seat).
 */
function resolveExperimentValue(
  metric: string,
  row: EvidenceRow,
  scope: PredicateScope
): number | null {
  const isFocus = metric.endsWith("Focus");
  const isOpp = metric.endsWith("Opponent");
  if (!isFocus && !isOpp) {
    const v = row.flat[metric];
    return typeof v === "number" && Number.isFinite(v) ? v : null;
  }
  const focus = scope.focusStrategySlug;
  if (!focus) return null;
  const base = isFocus ? metric.slice(0, -"Focus".length) : metric.slice(0, -"Opponent".length);
  const p1Is = row.p1Slug === focus;
  const p2Is = row.p2Slug === focus;
  if (p1Is && p2Is) {
    const v1 = row.flat[`${base}P1`];
    const v2 = row.flat[`${base}P2`];
    const ok1 = typeof v1 === "number" && Number.isFinite(v1);
    const ok2 = typeof v2 === "number" && Number.isFinite(v2);
    if (ok1 && ok2) return (v1 + v2) / 2;
    return null; // partial self-play data is not silently halved
  }
  if (!p1Is && !p2Is) return null;
  const focusSeat: 1 | 2 = p1Is ? 1 : 2;
  const seat = isFocus ? focusSeat : focusSeat === 1 ? 2 : 1;
  const v = row.flat[`${base}P${seat}`];
  return typeof v === "number" && Number.isFinite(v) ? v : null;
}

/**
 * Collect one value per evidence unit for a scope. aggregate="experiment"
 * yields one value per experiment; "seatDecision" yields one value per
 * (experiment, focus-occupied seat) — the metric key is given WITHOUT the
 * P1/P2 suffix and focusStrategySlug is required.
 */
function gatherScopeValues(
  evidence: EvidenceRow[],
  scope: PredicateScope,
  metric: string,
  aggregate: "experiment" | "seatDecision"
): { values: number[]; ids: number[] } {
  const values: number[] = [];
  const ids: number[] = [];
  for (const row of evidence) {
    if (!matchesScope(row, scope)) continue;
    if (aggregate === "seatDecision") {
      const focus = scope.focusStrategySlug;
      if (!focus) continue;
      let any = false;
      if (row.p1Slug === focus) {
        const v = row.flat[`${metric}P1`];
        if (typeof v === "number" && Number.isFinite(v)) {
          values.push(v);
          any = true;
        }
      }
      if (row.p2Slug === focus) {
        const v = row.flat[`${metric}P2`];
        if (typeof v === "number" && Number.isFinite(v)) {
          values.push(v);
          any = true;
        }
      }
      if (any) ids.push(row.experimentId);
    } else {
      const v = resolveExperimentValue(metric, row, scope);
      if (v != null) {
        values.push(v);
        ids.push(row.experimentId);
      }
    }
  }
  return { values, ids };
}

// ── Verdict logic ──────────────────────────────────────────────────────────

function pointVerdict(item: PredicateItem, mean: number): Verdict {
  const eps = 1e-9;
  switch (item.op) {
    case ">":
      return mean > item.threshold ? "supported" : "refuted";
    case ">=":
      return mean >= item.threshold - eps ? "supported" : "refuted";
    case "<":
      return mean < item.threshold ? "supported" : "refuted";
    case "<=":
      return mean <= item.threshold + eps ? "supported" : "refuted";
    case "between":
      return mean >= item.threshold - eps && mean <= (item.thresholdHigh ?? item.threshold) + eps
        ? "supported"
        : "refuted";
    case "approx": {
      const tol = item.tolerance ?? 1e-6;
      return Math.abs(mean - item.threshold) <= tol ? "supported" : "refuted";
    }
  }
}

function intervalVerdict(item: PredicateItem, ciLow: number, ciHigh: number): Verdict {
  switch (item.op) {
    case ">":
      if (ciLow > item.threshold) return "supported";
      if (ciHigh < item.threshold) return "refuted";
      return "inconclusive";
    case ">=":
      if (ciLow >= item.threshold) return "supported";
      if (ciHigh < item.threshold) return "refuted";
      return "inconclusive";
    case "<":
      if (ciHigh < item.threshold) return "supported";
      if (ciLow > item.threshold) return "refuted";
      return "inconclusive";
    case "<=":
      if (ciHigh <= item.threshold) return "supported";
      if (ciLow > item.threshold) return "refuted";
      return "inconclusive";
    case "between": {
      const hi = item.thresholdHigh ?? item.threshold;
      if (ciLow >= item.threshold && ciHigh <= hi) return "supported";
      if (ciHigh < item.threshold || ciLow > hi) return "refuted";
      return "inconclusive";
    }
    case "approx": {
      const tol = item.tolerance ?? 1e-6;
      const lo = item.threshold - tol;
      const hi = item.threshold + tol;
      if (ciLow >= lo && ciHigh <= hi) return "supported";
      if (ciHigh < lo || ciLow > hi) return "refuted";
      return "inconclusive";
    }
  }
}

// ── Main adjudication ──────────────────────────────────────────────────────

const fmtN = (v: number | null | undefined): string => (v == null ? "n/a" : v.toFixed(4));

/** Pooled-SD Cohen's d for a two-sample difference (null when degenerate). */
function pooledEffectSize(a: SampleStats, b: SampleStats): number | null {
  if (a.n < 2 || b.n < 2 || a.mean == null || b.mean == null) return null;
  const sdA = a.sd ?? 0;
  const sdB = b.sd ?? 0;
  const pooledVar =
    ((a.n - 1) * sdA * sdA + (b.n - 1) * sdB * sdB) / (a.n + b.n - 2);
  if (pooledVar < SD_EPSILON * SD_EPSILON) return null;
  return (a.mean - b.mean) / Math.sqrt(pooledVar);
}

/** Adjudicate one predicate item (all kinds). */
async function adjudicateItem(
  item: PredicateItem,
  predicate: ClaimPredicate,
  evidence: EvidenceRow[],
  minExperiments: number
): Promise<ItemAdjudication> {
  const kind = item.kind ?? "threshold";
  const aggregate = item.aggregate ?? "experiment";
  const scope = { ...predicate.scope, ...(item.scope ?? {}) };

  let n = 0;
  let mean: number | null = null;
  let sd: number | null = null;
  let ciLow: number | null = null;
  let ciHigh: number | null = null;
  let effectSize: number | null = null;
  let margin: number | null = null;
  let verdict: Verdict = "untested";
  let note: string | undefined;
  let usedIds: number[] = [];

  const sideSummary = (a: SampleStats, b: SampleStats): string =>
    `A(n=${a.n}, mean=${fmtN(a.mean)}, sd=${fmtN(a.sd)}) vs B(n=${b.n}, mean=${fmtN(b.mean)}, sd=${fmtN(b.sd)})`;

  if (scope.fork != null) {
    // Paired parent-vs-fork evidence over the shared post-fork window.
    // Fork items support only the original threshold semantics.
    const values: number[] = [];
    const forkEvidence = await loadForkEvidence();
    const matching = dedupeForksPerParent(
      forkEvidence.filter((row) => matchesForkScope(row, scope))
    );
    for (const row of matching) {
      const v = row.flat[item.metric];
      if (typeof v === "number" && Number.isFinite(v)) {
        values.push(v);
        usedIds.push(row.forkExperimentId);
      }
    }
    const stats = sampleStats(values);
    n = stats.n;
    mean = stats.mean;
    sd = stats.sd;
    ciLow = stats.ciLow;
    ciHigh = stats.ciHigh;
    if (stats.n < minExperiments || stats.mean == null) {
      verdict = "untested";
      note = `No matching evidence (need ≥ ${minExperiments} parent-fork pairs with metric "${item.metric}", found ${stats.n}).`;
    } else if (stats.n === 1 || stats.sd == null || stats.sd < SD_EPSILON) {
      verdict = pointVerdict(item, stats.mean);
      note =
        stats.n === 1
          ? "Single experiment — exact point comparison (deterministic evidence)."
          : `${stats.n} replicates, zero variance — exact point comparison.`;
    } else {
      verdict = intervalVerdict(item, stats.ciLow!, stats.ciHigh!);
    }
    if (stats.sd != null && stats.sd >= SD_EPSILON && stats.mean != null) {
      effectSize = (stats.mean - item.threshold) / stats.sd;
    }
    margin = stats.mean != null ? stats.mean - item.threshold : null;
  } else if (kind === "threshold") {
    const g = gatherScopeValues(evidence, scope, item.metric, aggregate);
    usedIds = g.ids;
    const stats = sampleStats(g.values);
    n = stats.n;
    mean = stats.mean;
    sd = stats.sd;
    ciLow = stats.ciLow;
    ciHigh = stats.ciHigh;
    if (stats.n < minExperiments || stats.mean == null) {
      verdict = "untested";
      note = `No matching evidence (need ≥ ${minExperiments} ${aggregate === "seatDecision" ? "seat-decisions" : "experiments"} with metric "${item.metric}", found ${stats.n}).`;
    } else if (stats.n === 1 || stats.sd == null || stats.sd < SD_EPSILON) {
      // Near-zero sd (float accumulation residue across identical replicates)
      // must take the exact path too, or the t-CI degenerates and the effect
      // size explodes to astronomical nonsense.
      verdict = pointVerdict(item, stats.mean);
      note =
        stats.n === 1
          ? "Single experiment — exact point comparison (deterministic evidence)."
          : `${stats.n} replicates, zero variance — exact point comparison.`;
    } else if ((item.evaluate ?? "ci") === "point") {
      verdict = pointVerdict(item, stats.mean);
      note = "Point evaluation (pre-registered as a distribution-shape check, not a CI test).";
    } else {
      verdict = intervalVerdict(item, stats.ciLow!, stats.ciHigh!);
    }
    if (stats.sd != null && stats.sd >= SD_EPSILON && stats.mean != null) {
      effectSize = (stats.mean - item.threshold) / stats.sd;
    }
    margin = stats.mean != null ? stats.mean - item.threshold : null;
  } else if (kind === "diffScopes") {
    const scopeB = { ...predicate.scope, ...(item.scopeB ?? {}) };
    const a = gatherScopeValues(evidence, scope, item.metric, aggregate);
    const b = gatherScopeValues(evidence, scopeB, item.metric, aggregate);
    usedIds = [...a.ids, ...b.ids];
    const sA = sampleStats(a.values);
    const sB = sampleStats(b.values);
    n = sA.n + sB.n;
    if (sA.n < minExperiments || sB.n < minExperiments || sA.mean == null || sB.mean == null) {
      verdict = "untested";
      note = `Both scopes need ≥ ${minExperiments} values for "${item.metric}" (found A=${sA.n}, B=${sB.n}).`;
    } else {
      const rawDiff = sA.mean - sB.mean;
      const value = item.absolute ? Math.abs(rawDiff) : rawDiff;
      mean = value;
      margin = value - item.threshold;
      effectSize = pooledEffectSize(sA, sB);
      const w = item.absolute ? null : welch95(sA, sB);
      if (item.absolute || (item.evaluate ?? "ci") === "point" || w == null) {
        verdict = pointVerdict(item, value);
        const why = item.absolute
          ? "absolute difference — point evaluation"
          : (item.evaluate ?? "ci") === "point"
            ? "point evaluation (pre-registered)"
            : "degenerate variance on both sides — exact point comparison";
        note = `${sideSummary(sA, sB)} — ${why}.`;
      } else {
        ciLow = w.ciLow;
        ciHigh = w.ciHigh;
        verdict = intervalVerdict(item, w.ciLow, w.ciHigh);
        note = `${sideSummary(sA, sB)}; Welch df=${w.df.toFixed(1)}.`;
      }
    }
  } else if (kind === "ratioScopes") {
    const scopeB = { ...predicate.scope, ...(item.scopeB ?? {}) };
    const a = gatherScopeValues(evidence, scope, item.metric, aggregate);
    const b = gatherScopeValues(evidence, scopeB, item.metric, aggregate);
    usedIds = [...a.ids, ...b.ids];
    const sA = sampleStats(a.values);
    const sB = sampleStats(b.values);
    n = sA.n + sB.n;
    if (sA.n < minExperiments || sB.n < minExperiments || sA.mean == null || sB.mean == null) {
      verdict = "untested";
      note = `Both scopes need ≥ ${minExperiments} values for "${item.metric}" (found A=${sA.n}, B=${sB.n}).`;
    } else if (Math.abs(sB.mean) < 1e-12) {
      if (item.ratioEdge?.denomZero != null) {
        const cut = item.ratioEdge.denomZero.numerAtLeast;
        verdict = sA.mean >= cut - 1e-9 ? "supported" : "inconclusive";
        note = `${sideSummary(sA, sB)} — denominator mean is 0; pre-registered edge rule: supported iff numerator mean ≥ ${cut}.`;
      } else {
        verdict = "inconclusive";
        note = `${sideSummary(sA, sB)} — denominator mean is 0 and no edge rule was pre-registered.`;
      }
    } else {
      const ratio = sA.mean / sB.mean;
      mean = ratio;
      margin = ratio - item.threshold;
      verdict = pointVerdict(item, ratio);
      note = `${sideSummary(sA, sB)} — ratio of means, point evaluation.`;
    }
  } else if (kind === "orderedScopes") {
    const scopesList = item.scopesOrdered ?? [];
    if (scopesList.length < 2) {
      verdict = "untested";
      note = "orderedScopes requires ≥ 2 scopes in scopesOrdered.";
    } else {
      const sides = scopesList.map((s) =>
        gatherScopeValues(evidence, { ...predicate.scope, ...s }, item.metric, aggregate)
      );
      const stats = sides.map((g) => sampleStats(g.values));
      usedIds = sides.flatMap((g) => g.ids);
      n = stats.reduce((acc, s) => acc + s.n, 0);
      const short = stats.findIndex((s) => s.n < minExperiments || s.mean == null);
      if (short >= 0) {
        verdict = "untested";
        note = `Scope ${short + 1}/${scopesList.length} has ${stats[short].n} values for "${item.metric}" (need ≥ ${minExperiments} each).`;
      } else {
        const means = stats.map((s) => s.mean!);
        let ok = true;
        for (let i = 0; i + 1 < means.length; i++) {
          if (!(means[i] <= means[i + 1] + 1e-9)) ok = false;
        }
        verdict = ok ? "supported" : "refuted";
        note = `Ordered means (point evaluation): ${means.map((m) => m.toFixed(4)).join(" ≤ ")} — ${ok ? "non-decreasing" : "ordering violated"}. Per-scope n: ${stats.map((s) => s.n).join(", ")}.`;
      }
    }
  } else if (kind === "metricVsMetric") {
    if (!item.metricB) {
      verdict = "untested";
      note = "metricVsMetric requires metricB.";
    } else {
      const a = gatherScopeValues(evidence, scope, item.metric, aggregate);
      const b = gatherScopeValues(evidence, scope, item.metricB, aggregate);
      usedIds = a.ids;
      const sA = sampleStats(a.values);
      const sB = sampleStats(b.values);
      n = sA.n;
      if (sA.n < minExperiments || sB.n < minExperiments || sA.mean == null || sB.mean == null) {
        verdict = "untested";
        note = `Need ≥ ${minExperiments} values for both "${item.metric}" (${sA.n}) and "${item.metricB}" (${sB.n}).`;
      } else {
        const value = sA.mean - sB.mean;
        mean = value;
        margin = value - item.threshold;
        verdict = pointVerdict(item, value);
        note = `${item.metric}(mean=${fmtN(sA.mean)}, n=${sA.n}) vs ${item.metricB}(mean=${fmtN(sB.mean)}, n=${sB.n}) — difference of means, point evaluation.`;
      }
    }
  } else {
    verdict = "untested";
    note = `Unknown item kind "${String(kind)}".`;
  }

  return {
    label: item.label ?? item.metric,
    metric: item.metric,
    op: item.op,
    threshold: item.threshold,
    thresholdHigh: item.thresholdHigh,
    tolerance: item.tolerance,
    n,
    mean,
    sd,
    ciLow,
    ciHigh,
    effectSize,
    margin,
    verdict,
    evidenceExperimentIds: usedIds,
    note,
  };
}

export async function adjudicatePredicate(
  predicate: ClaimPredicate,
  claimCreatedAt?: Date | string | null
): Promise<AdjudicationRecord> {
  const evidence = await loadEvidence();
  const minExperiments = predicate.minExperiments ?? 1;
  const items: ItemAdjudication[] = [];

  for (const item of predicate.all) {
    items.push(await adjudicateItem(item, predicate, evidence, minExperiments));
  }

  // Post-registration audit (disclosed, never hand-set): compare the claim's
  // registration time against the earliest experiment its items actually
  // cited as evidence. ISO-8601 UTC strings compare lexicographically.
  const createdById = new Map(evidence.map((r) => [r.experimentId, r.createdAt]));
  let earliestEvidenceAt: string | null = null;
  for (const item of items) {
    for (const id of item.evidenceExperimentIds) {
      const c = createdById.get(id);
      if (c != null && (earliestEvidenceAt == null || c < earliestEvidenceAt))
        earliestEvidenceAt = c;
    }
  }
  const claimIso = claimCreatedAt != null ? new Date(claimCreatedAt).toISOString() : null;
  const postRegistered =
    claimIso != null && earliestEvidenceAt != null ? claimIso > earliestEvidenceAt : undefined;

  let verdict: Verdict;
  if (items.some((i) => i.verdict === "refuted")) verdict = "refuted";
  else if (items.some((i) => i.verdict === "untested")) verdict = "untested";
  else if (items.some((i) => i.verdict === "inconclusive")) verdict = "inconclusive";
  else verdict = "supported";

  const parts = items.map(
    (i) =>
      `${i.label}: ${i.verdict}` +
      (i.mean != null
        ? ` (mean ${i.mean.toFixed(4)}${i.ciLow != null ? `, 95% CI [${i.ciLow.toFixed(4)}, ${i.ciHigh!.toFixed(4)}]` : ""}, n=${i.n}${i.effectSize != null ? `, d=${i.effectSize.toFixed(2)}` : i.margin != null ? `, margin=${i.margin.toFixed(4)}` : ""})`
        : "")
  );

  return {
    verdict,
    adjudicatedAt: new Date().toISOString(),
    items,
    note:
      parts.join(" | ") +
      (postRegistered === true
        ? " | POST-REGISTERED: claim was created after the earliest evidence experiment (disclosed post-hoc claim)."
        : ""),
    postRegistered,
    claimCreatedAt: claimIso,
    earliestEvidenceAt,
  };
}
