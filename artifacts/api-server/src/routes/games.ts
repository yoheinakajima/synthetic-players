import { Router, type IRouter } from "express";
import { eq } from "drizzle-orm";
import { db, gamesTable } from "@workspace/db";
import {
  GetGameParams,
  GetGameResponse,
  ListGamesResponse,
} from "@workspace/api-zod";

const router: IRouter = Router();

function parseGameJson(game: typeof gamesTable.$inferSelect) {
  return {
    ...game,
    actionLabels: JSON.parse(game.actionLabels) as string[],
    payoffMatrix: game.payoffMatrix, // kept as JSON string per spec
    nashEquilibria: game.nashEquilibria, // kept as JSON string per spec
  };
}

router.get("/games", async (req, res): Promise<void> => {
  const games = await db.select().from(gamesTable).orderBy(gamesTable.id);
  res.json(ListGamesResponse.parse(games.map(parseGameJson)));
});

router.get("/games/:id", async (req, res): Promise<void> => {
  const params = GetGameParams.safeParse(req.params);
  if (!params.success) {
    res.status(400).json({ error: params.error.message });
    return;
  }

  const [game] = await db
    .select()
    .from(gamesTable)
    .where(eq(gamesTable.id, params.data.id));

  if (!game) {
    res.status(404).json({ error: "Game not found" });
    return;
  }

  res.json(GetGameResponse.parse(parseGameJson(game)));
});

export default router;
