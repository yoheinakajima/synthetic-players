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
} from "@workspace/api-zod";

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

  const body = UpdateClaimBody.safeParse(req.body);
  if (!body.success) {
    res.status(400).json({ error: body.error.message });
    return;
  }

  const updates: Partial<typeof claimsTable.$inferSelect> = {};
  if (body.data.title != null) updates.title = body.data.title;
  if (body.data.statement != null) updates.statement = body.data.statement;
  if (body.data.status != null) updates.status = body.data.status;
  if (body.data.evidenceSummary != null) updates.evidenceSummary = body.data.evidenceSummary;
  if (body.data.linkedAnalysisId !== undefined) updates.analysisId = body.data.linkedAnalysisId;

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
