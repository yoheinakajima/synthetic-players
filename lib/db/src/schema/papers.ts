import { pgTable, text, serial, timestamp, integer } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod/v4";

export const papersTable = pgTable("papers", {
  id: serial("id").primaryKey(),
  title: text("title").notNull(),
  abstract: text("abstract"),
  status: text("status").notNull().default("draft"), // draft | generating | complete
  sections: text("sections"), // JSON array of { heading, content } objects
  claimsJson: text("claims_json"), // JSON array of claim IDs
  experimentsJson: text("experiments_json"), // JSON array of experiment IDs
  wordCount: integer("word_count"),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).notNull().defaultNow().$onUpdate(() => new Date()),
});

export const insertPaperSchema = createInsertSchema(papersTable).omit({ id: true, createdAt: true, updatedAt: true });
export type InsertPaper = z.infer<typeof insertPaperSchema>;
export type Paper = typeof papersTable.$inferSelect;
