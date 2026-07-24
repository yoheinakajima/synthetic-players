import { Router, type IRouter } from "express";
import { eq, and } from "drizzle-orm";
import { db, claimsTable, gamesTable, strategiesTable } from "@workspace/db";
import {
  ListClaimsQueryParams,
  ListClaimsResponse,
  CreateClaimBody,
  CreateClaimResponse,
  GetClaimParams,
  GetClaimResponse,
  UpdateClaimParams,
  UpdateClaimBody,
  UpdateClaimResponse,
  DeleteClaimParams,
  AdjudicateClaimParams,
  AdjudicateClaimResponse,
  AdjudicateAllClaimsResponse,
} from "@workspace/api-zod";
import {
  adjudicatePredicate,
  invalidateEvidenceCache,
  type ClaimPredicate,
} from "../lib/adjudicator";
import { logger } from "../lib/logger";

const router: IRouter = Router();

async function enrichClaim(claim: typeof claimsTable.$inferSelect) {
  const [game] = await db
    .select({ name: gamesTable.name })
    .from(gamesTable)
    .where(eq(gamesTable.id, claim.gameId));

  let strategyName: string | null = null;
  if (claim.strategyId != null) {
    const [strat] = await db
      .select({ name: strategiesTable.name })
      .from(strategiesTable)
      .where(eq(strategiesTable.id, claim.strategyId));
    strategyName = strat?.name ?? null;
  }

  return {
    ...claim,
    gameName: game?.name ?? null,
    strategyName,
  };
}

router.get("/claims", async (req, res): Promise<void> => {
  const query = ListClaimsQueryParams.safeParse(req.query);
  if (!query.success) {
    res.status(400).json({ error: query.error.message });
    return;
  }

  const conditions = [];
  if (query.data.gameId != null) {
    conditions.push(eq(claimsTable.gameId, query.data.gameId));
  }
  if (query.data.status != null) {
    conditions.push(eq(claimsTable.status, query.data.status));
  }

  const claims = await db
    .select()
    .from(claimsTable)
    .where(conditions.length > 0 ? and(...conditions) : undefined)
    .orderBy(claimsTable.createdAt);

  const enriched = await Promise.all(claims.map(enrichClaim));
  res.json(ListClaimsResponse.parse(enriched));
});

router.post("/claims", async (req, res): Promise<void> => {
  const parsed = CreateClaimBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: parsed.error.message });
    return;
  }

  const [claim] = await db
    .insert(claimsTable)
    .values({
      title: parsed.data.title,
      statement: parsed.data.statement,
      gameId: parsed.data.gameId,
      strategyId: parsed.data.strategyId ?? null,
      analysisId: parsed.data.analysisId ?? null,
      evidenceSummary: parsed.data.evidenceSummary ?? null,
      predicateJson: parsed.data.predicateJson ?? null,
      status: "hypothesis",
    })
    .returning();

  const enriched = await enrichClaim(claim);
  res.status(201).json(CreateClaimResponse.parse(enriched));
});

router.get("/claims/:id", async (req, res): Promise<void> => {
  const params = GetClaimParams.safeParse(req.params);
  if (!params.success) {
    res.status(400).json({ error: params.error.message });
    return;
  }

  const [claim] = await db
    .select()
    .from(claimsTable)
    .where(eq(claimsTable.id, params.data.id));

  if (!claim) {
    res.status(404).json({ error: "Claim not found" });
    return;
  }

  const enriched = await enrichClaim(claim);
  res.json(GetClaimResponse.parse(enriched));
});

router.patch("/claims/:id", async (req, res): Promise<void> => {
  const params = UpdateClaimParams.safeParse(req.params);
  if (!params.success) {
    res.status(400).json({ error: params.error.message });
    return;
  }

  // Honesty invariant: verdicts are machine-assigned. A claim's status can
  // only change via the adjudication endpoints, never by direct edit.
  if (req.body && typeof req.body === "object" && "status" in req.body) {
    res.status(400).json({
      error:
        "Claim status is machine-assigned by adjudication. Use POST /claims/{id}/adjudicate or POST /claims/adjudicate-all.",
    });
    return;
  }

  const body = UpdateClaimBody.safeParse(req.body);
  if (!body.success) {
    res.status(400).json({ error: body.error.message });
    return;
  }

  // HARKing guard: once a claim has been adjudicated against evidence its
  // predicate is immutable. Re-thresholding after seeing data would let a
  // refuted claim be quietly re-scoped into support — register a new claim
  // instead. (Prose fields stay editable; verdicts are recomputed from the
  // locked predicate only.)
  if (body.data.predicateJson != null) {
    const [existing] = await db
      .select()
      .from(claimsTable)
      .where(eq(claimsTable.id, params.data.id));
    if (!existing) {
      res.status(404).json({ error: "Claim not found" });
      return;
    }
    if (existing.adjudicationJson != null) {
      res.status(409).json({
        error:
          "Predicate is locked: this claim has already been adjudicated against evidence. " +
          "Changing a predicate after seeing data is HARKing — register a new claim instead.",
      });
      return;
    }
  }

  const updates: Partial<typeof claimsTable.$inferSelect> = {};
  if (body.data.title != null) updates.title = body.data.title;
  if (body.data.statement != null) updates.statement = body.data.statement;
  if (body.data.evidenceSummary != null) updates.evidenceSummary = body.data.evidenceSummary;
  if (body.data.linkedAnalysisId !== undefined) updates.analysisId = body.data.linkedAnalysisId;
  if (body.data.predicateJson != null) updates.predicateJson = body.data.predicateJson;

  const [claim] = await db
    .update(claimsTable)
    .set(updates)
    .where(eq(claimsTable.id, params.data.id))
    .returning();

  if (!claim) {
    res.status(404).json({ error: "Claim not found" });
    return;
  }

  const enriched = await enrichClaim(claim);
  res.json(UpdateClaimResponse.parse(enriched));
});

/**
 * Adjudicate every claim that has a structured predicate. Claims without a
 * predicate are marked untested — a claim we can't mechanically check is a
 * claim we don't get to call supported.
 */
router.post("/claims/adjudicate-all", async (_req, res): Promise<void> => {
  invalidateEvidenceCache();
  const claims = await db.select().from(claimsTable).orderBy(claimsTable.id);

  const results = [];
  for (const claim of claims) {
    if (!claim.predicateJson) {
      await db
        .update(claimsTable)
        .set({ status: "untested", adjudicatedAt: new Date() })
        .where(eq(claimsTable.id, claim.id));
      results.push({
        claimId: claim.id,
        title: claim.title,
        status: "untested" as const,
        note: "No structured predicate defined — cannot be mechanically checked.",
      });
      continue;
    }

    try {
      const predicate = JSON.parse(claim.predicateJson) as ClaimPredicate;
      const record = await adjudicatePredicate(predicate, claim.createdAt);
      await db
        .update(claimsTable)
        .set({
          status: record.verdict,
          adjudicationJson: JSON.stringify(record),
          adjudicatedAt: new Date(),
        })
        .where(eq(claimsTable.id, claim.id));
      results.push({
        claimId: claim.id,
        title: claim.title,
        status: record.verdict,
        note: record.note,
      });
      logger.info(`Adjudicated claim #${claim.id} "${claim.title}": ${record.verdict}`);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unknown error";
      // Persist the failure as untested — a claim whose predicate can't be
      // evaluated must not keep a stale supported/refuted verdict in the DB.
      await db
        .update(claimsTable)
        .set({
          status: "untested",
          adjudicationJson: JSON.stringify({
            verdict: "untested",
            adjudicatedAt: new Date().toISOString(),
            items: [],
            note: `Adjudication error: ${message}`,
          }),
          adjudicatedAt: new Date(),
        })
        .where(eq(claimsTable.id, claim.id));
      results.push({
        claimId: claim.id,
        title: claim.title,
        status: "untested" as const,
        note: `Adjudication error: ${message}`,
      });
    }
  }

  res.json(AdjudicateAllClaimsResponse.parse(results));
});

router.post("/claims/:id/adjudicate", async (req, res): Promise<void> => {
  const params = AdjudicateClaimParams.safeParse(req.params);
  if (!params.success) {
    res.status(400).json({ error: params.error.message });
    return;
  }

  const [claim] = await db.select().from(claimsTable).where(eq(claimsTable.id, params.data.id));
  if (!claim) {
    res.status(404).json({ error: "Claim not found" });
    return;
  }
  if (!claim.predicateJson) {
    res.status(400).json({ error: "Claim has no structured predicate to adjudicate" });
    return;
  }

  invalidateEvidenceCache();
  const predicate = JSON.parse(claim.predicateJson) as ClaimPredicate;
  const record = await adjudicatePredicate(predicate, claim.createdAt);

  const [updated] = await db
    .update(claimsTable)
    .set({
      status: record.verdict,
      adjudicationJson: JSON.stringify(record),
      adjudicatedAt: new Date(),
    })
    .where(eq(claimsTable.id, claim.id))
    .returning();

  logger.info(`Adjudicated claim #${claim.id} "${claim.title}": ${record.verdict}`);

  const enriched = await enrichClaim(updated);
  res.json(AdjudicateClaimResponse.parse(enriched));
});

router.delete("/claims/:id", async (req, res): Promise<void> => {
  const params = DeleteClaimParams.safeParse(req.params);
  if (!params.success) {
    res.status(400).json({ error: params.error.message });
    return;
  }

  const [deleted] = await db
    .delete(claimsTable)
    .where(eq(claimsTable.id, params.data.id))
    .returning();

  if (!deleted) {
    res.status(404).json({ error: "Claim not found" });
    return;
  }

  res.sendStatus(204);
});

export default router;
