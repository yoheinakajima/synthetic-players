import { Router, type IRouter } from "express";
import { eq, asc } from "drizzle-orm";
import { db, roundsTable } from "@workspace/db";
import { ListRoundsParams, ListRoundsResponse } from "@workspace/api-zod";

const router: IRouter = Router();

router.get("/experiments/:experimentId/rounds", async (req, res): Promise<void> => {
  const params = ListRoundsParams.safeParse(req.params);
  if (!params.success) {
    res.status(400).json({ error: params.error.message });
    return;
  }

  const rounds = await db
    .select()
    .from(roundsTable)
    .where(eq(roundsTable.experimentId, params.data.experimentId))
    .orderBy(asc(roundsTable.roundNumber));

  res.json(ListRoundsResponse.parse(rounds));
});

export default router;
