import { pgTable, text, serial, timestamp, integer } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod/v4";

export const claimsTable = pgTable("claims", {
  id: serial("id").primaryKey(),
  title: text("title").notNull(),
  statement: text("statement").notNull(),
  gameId: integer("game_id").notNull(),
  strategyId: integer("strategy_id"),
  analysisId: integer("analysis_id"),
  status: text("status").notNull().default("hypothesis"), // hypothesis | supported | refuted | inconclusive | untested
  evidenceSummary: text("evidence_summary"),
  predicateJson: text("predicate_json"), // structured, machine-checkable predicate
  adjudicationJson: text("adjudication_json"), // latest adjudication record (evidence, stats, verdict)
  adjudicatedAt: timestamp("adjudicated_at", { withTimezone: true }),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).notNull().defaultNow().$onUpdate(() => new Date()),
});

export const insertClaimSchema = createInsertSchema(claimsTable).omit({ id: true, createdAt: true, updatedAt: true });
export type InsertClaim = z.infer<typeof insertClaimSchema>;
export type Claim = typeof claimsTable.$inferSelect;
