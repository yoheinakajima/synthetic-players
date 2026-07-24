import { useState } from 'react';
import { useListClaims, useCreateClaim, useAdjudicateAllClaims, useListGames, getListClaimsQueryKey } from '@workspace/api-client-react';
import { useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage, FormDescription } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useToast } from '@/hooks/use-toast';
import { Dna, Plus, Scale } from 'lucide-react';
import { formatDateTime } from '@/lib/format';

const claimSchema = z.object({
  title: z.string().min(1, "Title required"),
  statement: z.string().min(1, "Statement required"),
  gameId: z.coerce.number().min(1, "Game required"),
  evidenceSummary: z.string().optional(),
  predicateJson: z.string().optional().refine(
    (v) => { if (!v) return true; try { JSON.parse(v); return true; } catch { return false; } },
    "Must be valid JSON"
  ),
});

interface AdjItem {
  label: string;
  metric: string;
  op: string;
  threshold: number;
  n: number;
  mean: number | null;
  sd: number | null;
  ciLow: number | null;
  ciHigh: number | null;
  effectSize: number | null;
  margin: number | null;
  verdict: string;
  note?: string;
}

interface AdjRecord {
  verdict: string;
  adjudicatedAt: string;
  items: AdjItem[];
  note: string;
}

function parseAdjudication(json?: string | null): AdjRecord | null {
  if (!json) return null;
  try { return JSON.parse(json) as AdjRecord; } catch { return null; }
}

const verdictBadgeClass: Record<string, string> = {
  supported: 'bg-primary/10 text-primary border-primary/40',
  refuted: 'bg-destructive/10 text-destructive border-destructive/40',
  inconclusive: 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/40',
  untested: 'bg-muted text-muted-foreground border-border',
  hypothesis: 'bg-muted text-muted-foreground border-border',
};

const verdictTextClass: Record<string, string> = {
  supported: 'text-primary',
  refuted: 'text-destructive',
  inconclusive: 'text-amber-600 dark:text-amber-400',
  untested: 'text-muted-foreground',
};

export default function Claims() {
  const { data: claims, isLoading } = useListClaims();
  const { data: games } = useListGames();
  const createMutation = useCreateClaim();
  const adjudicateAllMutation = useAdjudicateAllClaims();
  const queryClient = useQueryClient();
  const { toast } = useToast();
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  const form = useForm<z.infer<typeof claimSchema>>({
    resolver: zodResolver(claimSchema),
    defaultValues: {
      title: '',
      statement: '',
      gameId: 0,
      evidenceSummary: '',
      predicateJson: '',
    },
  });

  const onSubmit = (values: z.infer<typeof claimSchema>) => {
    const data = { ...values, predicateJson: values.predicateJson || undefined };
    createMutation.mutate({ data }, {
      onSuccess: () => {
        toast({ title: "Claim formulated" });
        setIsDialogOpen(false);
        form.reset();
        queryClient.invalidateQueries({ queryKey: getListClaimsQueryKey() });
      },
      onError: () => toast({ title: "Failed to formulate claim", variant: "destructive" })
    });
  };

  const handleAdjudicateAll = () => {
    adjudicateAllMutation.mutate(undefined, {
      onSuccess: (results) => {
        const counts = results.reduce<Record<string, number>>((acc, r) => {
          acc[r.status] = (acc[r.status] ?? 0) + 1;
          return acc;
        }, {});
        toast({
          title: "Adjudication complete",
          description: Object.entries(counts).map(([k, v]) => `${v} ${k}`).join(', '),
        });
        queryClient.invalidateQueries({ queryKey: getListClaimsQueryKey() });
      },
      onError: () => toast({ title: "Adjudication failed", variant: "destructive" })
    });
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <h1 className="text-3xl font-serif font-bold tracking-tight">Research Claims</h1>
          <p className="text-muted-foreground mt-1">
            Machine-checkable propositions, mechanically adjudicated against experimental evidence.
          </p>
        </div>

        <div className="flex gap-2">
          <Button
            variant="outline"
            className="gap-2"
            onClick={handleAdjudicateAll}
            disabled={adjudicateAllMutation.isPending}
            data-testid="button-adjudicate-all"
          >
            <Scale className="w-4 h-4" />
            {adjudicateAllMutation.isPending ? "Adjudicating..." : "Adjudicate All"}
          </Button>

          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button className="gap-2">
                <Plus className="w-4 h-4" /> Formulate Claim
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-xl max-h-[85vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>New Research Claim</DialogTitle>
              </DialogHeader>
              <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 pt-4">
                  <FormField control={form.control} name="title" render={({ field }) => (
                    <FormItem>
                      <FormLabel>Short Title</FormLabel>
                      <FormControl><Input placeholder="e.g. Defection Dominance" {...field} /></FormControl>
                      <FormMessage />
                    </FormItem>
                  )} />
                  <FormField control={form.control} name="gameId" render={({ field }) => (
                    <FormItem>
                      <FormLabel>Target Game</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value ? field.value.toString() : ""}>
                        <FormControl><SelectTrigger><SelectValue placeholder="Select a game..." /></SelectTrigger></FormControl>
                        <SelectContent>
                          {games?.map(game => <SelectItem key={game.id} value={game.id.toString()}>{game.name}</SelectItem>)}
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )} />
                  <FormField control={form.control} name="statement" render={({ field }) => (
                    <FormItem>
                      <FormLabel>Proposition Statement</FormLabel>
                      <FormControl><Textarea placeholder="The formal claim..." {...field} /></FormControl>
                      <FormMessage />
                    </FormItem>
                  )} />
                  <FormField control={form.control} name="predicateJson" render={({ field }) => (
                    <FormItem>
                      <FormLabel>Structured Predicate (JSON, optional)</FormLabel>
                      <FormControl><Textarea className="font-mono text-xs" rows={5} placeholder='{"scope": {"gameId": 1}, "all": [{"metric": "welfareRatio", "op": ">=", "threshold": 0.9}]}' {...field} /></FormControl>
                      <FormDescription className="text-xs">Without a predicate the claim can never be adjudicated beyond "untested".</FormDescription>
                      <FormMessage />
                    </FormItem>
                  )} />
                  <FormField control={form.control} name="evidenceSummary" render={({ field }) => (
                    <FormItem>
                      <FormLabel>Evidence Summary (Optional)</FormLabel>
                      <FormControl><Textarea placeholder="Current empirical evidence..." {...field} /></FormControl>
                      <FormMessage />
                    </FormItem>
                  )} />
                  <div className="flex justify-end pt-4">
                    <Button type="submit" disabled={createMutation.isPending}>Save Claim</Button>
                  </div>
                </form>
              </Form>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {isLoading ? (
          Array.from({ length: 6 }).map((_, i) => <Skeleton key={i} className="h-48 w-full" />)
        ) : (
          claims?.map(claim => {
            const record = parseAdjudication(claim.adjudicationJson);
            return (
              <Card key={claim.id} className="flex flex-col" data-testid={`card-claim-${claim.id}`}>
                <CardHeader className="pb-3 border-b border-border/50">
                  <div className="flex justify-between items-start gap-2">
                    <CardTitle className="text-base leading-tight">{claim.title}</CardTitle>
                    <Badge
                      variant="outline"
                      className={`text-[10px] uppercase shrink-0 ${verdictBadgeClass[claim.status] ?? ''}`}
                      data-testid={`badge-status-${claim.id}`}
                    >
                      {claim.status}
                    </Badge>
                  </div>
                  <div className="mt-2 flex items-center gap-2">
                    <Badge variant="secondary" className="text-[10px] font-mono">{claim.gameName}</Badge>
                    {!claim.predicateJson && (
                      <Badge variant="outline" className="text-[10px] font-mono text-muted-foreground">no predicate</Badge>
                    )}
                  </div>
                </CardHeader>
                <CardContent className="pt-4 flex-1 space-y-3">
                  <p className="text-sm font-serif italic text-foreground">"{claim.statement}"</p>

                  {record && (
                    <div className="space-y-2">
                      {record.items.map((it, i) => (
                        <div key={i} className="p-2.5 rounded border bg-muted/20 text-xs space-y-1">
                          <div className="flex items-center justify-between gap-2">
                            <span className={`font-bold uppercase text-[10px] tracking-wider ${verdictTextClass[it.verdict] ?? ''}`}>
                              {it.verdict}
                            </span>
                            <span className="font-mono text-[10px] text-muted-foreground">n={it.n}</span>
                          </div>
                          <p className="text-muted-foreground leading-snug">{it.label}</p>
                          {it.mean != null && (
                            <p className="font-mono text-[10px] text-foreground/80">
                              observed {it.mean.toFixed(3)}
                              {it.ciLow != null && it.ciHigh != null && ` · CI [${it.ciLow.toFixed(3)}, ${it.ciHigh.toFixed(3)}]`}
                              {' · target '}{it.op} {it.threshold}
                              {it.effectSize != null
                                ? ` · d=${it.effectSize.toFixed(2)}`
                                : it.margin != null ? ` · margin=${it.margin.toFixed(3)}` : ''}
                            </p>
                          )}
                          {it.note && <p className="text-[10px] text-muted-foreground/70">{it.note}</p>}
                        </div>
                      ))}
                    </div>
                  )}

                  {claim.evidenceSummary && !record && (
                    <div className="p-3 bg-muted/30 rounded border text-xs text-muted-foreground leading-relaxed">
                      <strong className="text-foreground font-sans text-[10px] uppercase tracking-wider block mb-1">Evidence:</strong>
                      {claim.evidenceSummary}
                    </div>
                  )}
                </CardContent>
                <CardFooter className="pt-0 text-[10px] text-muted-foreground font-mono">
                  {claim.adjudicatedAt
                    ? <>Adjudicated {formatDateTime(claim.adjudicatedAt)}</>
                    : <>Updated {formatDateTime(claim.updatedAt || claim.createdAt)}</>}
                </CardFooter>
              </Card>
            );
          })
        )}
        {claims?.length === 0 && (
          <div className="col-span-full py-12 text-center text-muted-foreground">
            <Dna className="w-8 h-8 mx-auto mb-3 opacity-20" />
            <p>No claims have been formulated yet.</p>
          </div>
        )}
      </div>
    </div>
  );
}
