import { pgTable, text, serial, timestamp, integer, real } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod/v4";

export const gamesTable = pgTable("games", {
  id: serial("id").primaryKey(),
  slug: text("slug").notNull().unique(),
  name: text("name").notNull(),
  description: text("description").notNull(),
  numActions: integer("num_actions").notNull(),
  actionLabels: text("action_labels").notNull(), // JSON array
  payoffMatrix: text("payoff_matrix").notNull(), // JSON 3D array [p1][p2] = [p1payoff, p2payoff]
  nashEquilibria: text("nash_equilibria").notNull(), // JSON array of [p1action, p2action]
  nashDescription: text("nash_description"),
  theoreticalCooperationRate: real("theoretical_cooperation_rate"),
  category: text("category").notNull(), // coordination | social_dilemma | zero_sum | bargaining
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
});

export const insertGameSchema = createInsertSchema(gamesTable).omit({ id: true, createdAt: true });
export type InsertGame = z.infer<typeof insertGameSchema>;
export type Game = typeof gamesTable.$inferSelect;
