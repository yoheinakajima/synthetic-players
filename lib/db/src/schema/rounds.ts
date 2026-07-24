import { pgTable, text, serial, timestamp, integer, real, boolean } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod/v4";

export const roundsTable = pgTable("rounds", {
  id: serial("id").primaryKey(),
  experimentId: integer("experiment_id").notNull(),
  roundNumber: integer("round_number").notNull(),
  player1Action: integer("player1_action").notNull(),
  player2Action: integer("player2_action").notNull(),
  player1Payoff: real("player1_payoff").notNull(),
  player2Payoff: real("player2_payoff").notNull(),
  player1Reasoning: text("player1_reasoning"),
  player2Reasoning: text("player2_reasoning"),
  isNashOutcome: boolean("is_nash_outcome").notNull().default(false),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
});

export const insertRoundSchema = createInsertSchema(roundsTable).omit({ id: true, createdAt: true });
export type InsertRound = z.infer<typeof insertRoundSchema>;
export type Round = typeof roundsTable.$inferSelect;
