import { pgTable, text, serial, timestamp, integer, real } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod/v4";

export const experimentsTable = pgTable("experiments", {
  id: serial("id").primaryKey(),
  gameId: integer("game_id").notNull(),
  player1StrategyId: integer("player1_strategy_id").notNull(),
  player2StrategyId: integer("player2_strategy_id").notNull(),
  numRounds: integer("num_rounds").notNull(),
  seed: integer("seed"), // RNG seed for reproducibility; null for legacy unseeded runs
  batchLabel: text("batch_label"), // groups multi-seed replicate runs of the same matchup
  engineRunId: text("engine_run_id"), // ActiveGraph engine run id; null until first run
  parentExperimentId: integer("parent_experiment_id"), // fork lineage: parent experiment
  forkRound: integer("fork_round"), // fork lineage: round N at which this fork branched
  status: text("status").notNull().default("pending"), // pending | running | completed | failed
  player1TotalPayoff: real("player1_total_payoff"),
  player2TotalPayoff: real("player2_total_payoff"),
  cooperationRate: real("cooperation_rate"),
  nashDeviationScore: real("nash_deviation_score"),
  notes: text("notes"),
  errorMessage: text("error_message"),
  completedAt: timestamp("completed_at", { withTimezone: true }),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
});

export const insertExperimentSchema = createInsertSchema(experimentsTable).omit({ id: true, createdAt: true, status: true, player1TotalPayoff: true, player2TotalPayoff: true, cooperationRate: true, nashDeviationScore: true, completedAt: true, errorMessage: true });
export type InsertExperiment = z.infer<typeof insertExperimentSchema>;
export type Experiment = typeof experimentsTable.$inferSelect;
