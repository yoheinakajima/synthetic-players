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
  player1StrategySlug?: string;
  player2StrategySlug?: string;
  /** Match player1/player2 slugs in either seat order. Not honored for fork items (seat identity matters for swaps). */
  eitherOrder?: boolean;
  /** At least one seat's strategy is in this list. */
  anyStrategySlugs?: string[];
  /** Both seats' strategies are in this list. */
  pairFromSlugs?: string[];
  batchLabel?: string;
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

// ── Evidence selection ─────────────────────────────────────────────────────

interface EvidenceRow {
  experimentId: number;
  gameId: number;
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

  const stratSlug = new Map(strategies.map((s) => [s.id, s.slug]));
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
      gameId: exp.gameId,
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
  p1Slug: string;
  p2Slug: string;
  batchLabel: string | null;
}

function matchesScope(row: MatchableRow, scope: PredicateScope): boolean {
  if (scope.gameId != null && row.gameId !== scope.gameId) return false;
  if (scope.batchLabel != null && row.batchLabel !== scope.batchLabel) return false;

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

/** Resolve a metric name that may carry a Focus/Opponent suffix to a concrete P1/P2 key. */
function resolveMetricKey(metric: string, row: EvidenceRow, scope: PredicateScope): string | null {
  const focus = scope.focusStrategySlug;
  if (metric.endsWith("Focus") || metric.endsWith("Opponent")) {
    if (!focus) return null;
    let focusSeat: 1 | 2;
    if (row.p1Slug === focus) focusSeat = 1;
    else if (row.p2Slug === focus) focusSeat = 2;
    else return null;
    if (metric.endsWith("Focus")) {
      return metric.slice(0, -"Focus".length) + (focusSeat === 1 ? "P1" : "P2");
    }
    return metric.slice(0, -"Opponent".length) + (focusSeat === 1 ? "P2" : "P1");
  }
  return metric;
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

export async function adjudicatePredicate(predicate: ClaimPredicate): Promise<AdjudicationRecord> {
  const evidence = await loadEvidence();
  const minExperiments = predicate.minExperiments ?? 1;
  const items: ItemAdjudication[] = [];

  for (const item of predicate.all) {
    const scope = { ...predicate.scope, ...(item.scope ?? {}) };

    const values: number[] = [];
    const usedIds: number[] = [];
    if (scope.fork != null) {
      // Paired parent-vs-fork evidence over the shared post-fork window.
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
    } else {
      const matching = evidence.filter((row) => matchesScope(row, scope));
      for (const row of matching) {
        const key = resolveMetricKey(item.metric, row, scope);
        if (key == null) continue;
        const v = row.flat[key];
        if (typeof v === "number" && Number.isFinite(v)) {
          values.push(v);
          usedIds.push(row.experimentId);
        }
      }
    }

    const stats = sampleStats(values);
    let verdict: Verdict;
    let note: string | undefined;

    if (stats.n < minExperiments || stats.mean == null) {
      verdict = "untested";
      note = `No matching evidence (need ≥ ${minExperiments} ${scope.fork != null ? "parent-fork pairs" : "experiments"} with metric "${item.metric}", found ${stats.n}).`;
    } else if (stats.n === 1 || stats.sd == null || stats.sd < SD_EPSILON) {
      // Near-zero sd (float accumulation residue across identical replicates)
      // must take the exact path too, or the t-CI degenerates and the effect
      // size explodes to astronomical nonsense.
      verdict = pointVerdict(item, stats.mean);
      note =
        stats.n === 1
          ? "Single experiment — exact point comparison (deterministic evidence)."
          : `${stats.n} replicates, zero variance — exact point comparison.`;
    } else {
      verdict = intervalVerdict(item, stats.ciLow!, stats.ciHigh!);
    }

    items.push({
      label: item.label ?? item.metric,
      metric: item.metric,
      op: item.op,
      threshold: item.threshold,
      thresholdHigh: item.thresholdHigh,
      tolerance: item.tolerance,
      n: stats.n,
      mean: stats.mean,
      sd: stats.sd,
      ciLow: stats.ciLow,
      ciHigh: stats.ciHigh,
      effectSize:
        stats.sd != null && stats.sd >= SD_EPSILON && stats.mean != null
          ? (stats.mean - item.threshold) / stats.sd
          : null,
      margin: stats.mean != null ? stats.mean - item.threshold : null,
      verdict,
      evidenceExperimentIds: usedIds,
      note,
    });
  }

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
    note: parts.join(" | "),
  };
}
