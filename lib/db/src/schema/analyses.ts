import { pgTable, text, serial, timestamp, integer, real } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod/v4";

export const analysesTable = pgTable("analyses", {
  id: serial("id").primaryKey(),
  experimentId: integer("experiment_id").notNull().unique(),
  nashEquilibriumRate: real("nash_equilibrium_rate").notNull(),
  player1CooperationRate: real("player1_cooperation_rate").notNull(),
  player2CooperationRate: real("player2_cooperation_rate").notNull(),
  player1AvgPayoff: real("player1_avg_payoff").notNull(),
  player2AvgPayoff: real("player2_avg_payoff").notNull(),
  theoreticalPlayer1Payoff: real("theoretical_player1_payoff").notNull(),
  theoreticalPlayer2Payoff: real("theoretical_player2_payoff").notNull(),
  player1PayoffDeviation: real("player1_payoff_deviation").notNull(),
  player2PayoffDeviation: real("player2_payoff_deviation").notNull(),
  mutualCooperationRate: real("mutual_cooperation_rate").notNull(),
  mutualDefectionRate: real("mutual_defection_rate").notNull(),
  mixedOutcomeRate: real("mixed_outcome_rate").notNull(),
  roundByRoundJson: text("round_by_round_json"),
  analysisVersion: integer("analysis_version").notNull().default(1),
  metricsJson: text("metrics_json"), // v2 per-game-class metrics (JSON-encoded)
  summary: text("summary").notNull(),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
});

export const insertAnalysisSchema = createInsertSchema(analysesTable).omit({ id: true, createdAt: true });
export type InsertAnalysis = z.infer<typeof insertAnalysisSchema>;
export type Analysis = typeof analysesTable.$inferSelect;
