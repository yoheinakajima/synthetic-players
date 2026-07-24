import { Router, type IRouter } from "express";
import healthRouter from "./health";
import gamesRouter from "./games";
import strategiesRouter from "./strategies";
import experimentsRouter from "./experiments";
import roundsRouter from "./rounds";
import analysesRouter from "./analyses";
import claimsRouter from "./claims";
import papersRouter from "./papers";
import dashboardRouter from "./dashboard";

const router: IRouter = Router();

router.use(healthRouter);
router.use(gamesRouter);
router.use(strategiesRouter);
router.use(experimentsRouter);
router.use(roundsRouter);
router.use(analysesRouter);
router.use(claimsRouter);
router.use(papersRouter);
router.use(dashboardRouter);

export default router;
