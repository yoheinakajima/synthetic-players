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

import { eq } from "drizzle-orm";
import { db, experimentsTable, analysesTable, strategiesTable } from "@workspace/db";
import { flattenMetrics, type MetricsV2 } from "./metrics";

// ── Predicate types ────────────────────────────────────────────────────────

export interface PredicateScope {
  gameId?: number;
  player1StrategySlug?: string;
  player2StrategySlug?: string;
  /** Match player1/player2 slugs in either seat order. */
  eitherOrder?: boolean;
  /** At least one seat's strategy is in this list. */
  anyStrategySlugs?: string[];
  /** Both seats' strategies are in this list. */
  pairFromSlugs?: string[];
  batchLabel?: string;
  /** Resolves metric names ending in "Focus"/"Opponent" to the seat this strategy occupies. */
  focusStrategySlug?: string;
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

/** Invalidate the evidence cache (call after new experiments/analyses are written). */
export function invalidateEvidenceCache(): void {
  evidenceCache = null;
}

function matchesScope(row: EvidenceRow, scope: PredicateScope): boolean {
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
    const matching = evidence.filter((row) => matchesScope(row, scope));

    const values: number[] = [];
    const usedIds: number[] = [];
    for (const row of matching) {
      const key = resolveMetricKey(item.metric, row, scope);
      if (key == null) continue;
      const v = row.flat[key];
      if (typeof v === "number" && Number.isFinite(v)) {
        values.push(v);
        usedIds.push(row.experimentId);
      }
    }

    const stats = sampleStats(values);
    let verdict: Verdict;
    let note: string | undefined;

    if (stats.n < minExperiments || stats.mean == null) {
      verdict = "untested";
      note = `No matching evidence (need ≥ ${minExperiments} experiments with metric "${item.metric}", found ${stats.n}).`;
    } else if (stats.n === 1 || stats.sd === 0 || stats.sd == null) {
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
        stats.sd != null && stats.sd > 0 && stats.mean != null
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
