import express, { type Express } from "express";
import cors from "cors";
import pinoHttp from "pino-http";
import router from "./routes";
import { logger } from "./lib/logger";
import { seedIfEmpty, ensureAiStrategies } from "./lib/seed";
import { backfillClaimPredicates } from "./lib/claim-predicates";

const app: Express = express();

app.use(
  pinoHttp({
    logger,
    serializers: {
      req(req) {
        return {
          id: req.id,
          method: req.method,
          url: req.url?.split("?")[0],
        };
      },
      res(res) {
        return {
          statusCode: res.statusCode,
        };
      },
    },
  }),
);
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.use("/api", router);

// Seed reference data on startup (idempotent)
seedIfEmpty()
  .then(() => ensureAiStrategies())
  .then(() => backfillClaimPredicates())
  .catch((err) => {
  logger.error({ err }, "Seed failed");
});

export default app;
