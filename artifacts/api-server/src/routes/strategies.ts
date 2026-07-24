import { Router, type IRouter } from "express";
import { eq } from "drizzle-orm";
import { db, strategiesTable } from "@workspace/db";
import {
  GetStrategyParams,
  GetStrategyResponse,
  ListStrategiesResponse,
} from "@workspace/api-zod";

const router: IRouter = Router();

router.get("/strategies", async (_req, res): Promise<void> => {
  const strategies = await db
    .select()
    .from(strategiesTable)
    .orderBy(strategiesTable.id);
  res.json(ListStrategiesResponse.parse(strategies));
});

router.get("/strategies/:id", async (req, res): Promise<void> => {
  const params = GetStrategyParams.safeParse(req.params);
  if (!params.success) {
    res.status(400).json({ error: params.error.message });
    return;
  }

  const [strategy] = await db
    .select()
    .from(strategiesTable)
    .where(eq(strategiesTable.id, params.data.id));

  if (!strategy) {
    res.status(404).json({ error: "Strategy not found" });
    return;
  }

  res.json(GetStrategyResponse.parse(strategy));
});

export default router;
