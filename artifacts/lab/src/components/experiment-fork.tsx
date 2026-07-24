import { useState } from 'react';
import { useLocation } from 'wouter';
import {
  useForkExperiment,
  useListStrategies,
  useGetExperimentDiff,
  useGetExperimentTrace,
  getGetExperimentDiffQueryKey,
  getGetExperimentTraceQueryKey,
  getListStrategiesQueryKey,
  type ExperimentDetail as ExperimentDetailType,
} from '@workspace/api-client-react';
import {
  Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger,
} from '@/components/ui/dialog';
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from '@/components/ui/select';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Skeleton } from '@/components/ui/skeleton';
import { useToast } from '@/hooks/use-toast';
import { formatPercent, formatNumber } from '@/lib/format';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, ReferenceLine,
} from 'recharts';
import { GitBranch, ChevronDown, ScrollText, GitCompareArrows } from 'lucide-react';

// ── Fork dialog ─────────────────────────────────────────────────────────────

export function ForkDialog({ exp }: { exp: ExperimentDetailType }) {
  const [, navigate] = useLocation();
  const { toast } = useToast();
  const [open, setOpen] = useState(false);
  const [forkRound, setForkRound] = useState(Math.max(1, Math.floor(exp.numRounds / 2)));
  const [p1Swap, setP1Swap] = useState<string>('keep');
  const [p2Swap, setP2Swap] = useState<string>('keep');

  const { data: strategies } = useListStrategies({
    query: { enabled: open, queryKey: getListStrategiesQueryKey() },
  });
  const forkMutation = useForkExperiment();

  const handleFork = () => {
    forkMutation.mutate(
      {
        id: exp.id,
        data: {
          forkRound,
          player1StrategyId: p1Swap === 'keep' ? null : parseInt(p1Swap, 10),
          player2StrategyId: p2Swap === 'keep' ? null : parseInt(p2Swap, 10),
        },
      },
      {
        onSuccess: (fork) => {
          setOpen(false);
          toast({ title: 'Fork Created', description: `EXP-${fork.id} branched at round ${forkRound}.` });
          navigate(`/experiments/${fork.id}`);
        },
        onError: (err: any) =>
          toast({
            title: 'Fork Failed',
            description: err?.response?.data?.error ?? 'Engine error',
            variant: 'destructive',
          }),
      }
    );
  };

  const strategySelect = (
    value: string,
    onChange: (v: string) => void,
    keepLabel: string,
    testId: string
  ) => (
    <Select value={value} onValueChange={onChange}>
      <SelectTrigger data-testid={testId}>
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="keep">{keepLabel} (keep)</SelectItem>
        {strategies?.map((s) => (
          <SelectItem key={s.id} value={String(s.id)}>{s.name}</SelectItem>
        ))}
      </SelectContent>
    </Select>
  );

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" className="gap-2" data-testid="button-fork">
          <GitBranch className="w-4 h-4" />
          Fork
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Fork Experiment</DialogTitle>
          <DialogDescription>
            Branch a new experiment at round N. Rounds 1–N replay identically from the engine's
            event log; later rounds are freshly simulated, optionally with swapped strategies.
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4 py-2">
          <div className="space-y-2">
            <Label htmlFor="fork-round">Fork at round (1–{exp.numRounds})</Label>
            <Input
              id="fork-round"
              type="number"
              min={1}
              max={exp.numRounds}
              value={forkRound}
              onChange={(e) => setForkRound(Math.min(exp.numRounds, Math.max(1, parseInt(e.target.value || '1', 10))))}
              data-testid="input-fork-round"
            />
          </div>
          <div className="space-y-2">
            <Label>Player 1 strategy</Label>
            {strategySelect(p1Swap, setP1Swap, exp.player1Strategy?.name ?? 'Current', 'select-fork-p1')}
          </div>
          <div className="space-y-2">
            <Label>Player 2 strategy</Label>
            {strategySelect(p2Swap, setP2Swap, exp.player2Strategy?.name ?? 'Current', 'select-fork-p2')}
          </div>
        </div>
        <DialogFooter>
          <Button onClick={handleFork} disabled={forkMutation.isPending} data-testid="button-fork-confirm">
            {forkMutation.isPending ? 'Forking…' : `Fork at round ${forkRound}`}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

// ── Diff view (fork vs parent) ──────────────────────────────────────────────

export function DiffView({ experimentId }: { experimentId: number }) {
  const { data: diff, isLoading, error } = useGetExperimentDiff(experimentId, {
    query: { queryKey: getGetExperimentDiffQueryKey(experimentId), retry: false },
  });

  if (isLoading) return <Skeleton className="h-64 w-full" />;
  if (error || !diff) return null;

  let pSum1 = 0, pSum2 = 0, fSum1 = 0, fSum2 = 0;
  const maxLen = Math.max(diff.parentRounds.length, diff.forkRounds.length);
  const chartData = Array.from({ length: maxLen }, (_, i) => {
    const p = diff.parentRounds[i];
    const f = diff.forkRounds[i];
    if (p) { pSum1 += p.player1Payoff; pSum2 += p.player2Payoff; }
    if (f) { fSum1 += f.player1Payoff; fSum2 += f.player2Payoff; }
    return {
      round: i + 1,
      'Parent P1': p ? pSum1 : undefined,
      'Parent P2': p ? pSum2 : undefined,
      'Fork P1': f ? fSum1 : undefined,
      'Fork P2': f ? fSum2 : undefined,
    };
  });

  const statRow = (label: string, parent: string, fork: string) => (
    <div className="grid grid-cols-3 gap-2 text-sm py-1.5 border-b last:border-0">
      <span className="text-muted-foreground">{label}</span>
      <span className="font-mono text-right">{parent}</span>
      <span className="font-mono text-right">{fork}</span>
    </div>
  );

  return (
    <Card data-testid="card-diff">
      <CardHeader>
        <div className="flex items-center gap-2">
          <GitCompareArrows className="w-5 h-5 text-muted-foreground" />
          <CardTitle>Fork vs Parent</CardTitle>
        </div>
        <CardDescription>
          Branched from EXP-{diff.parentExperimentId} at round {diff.forkRound}.{' '}
          {diff.divergenceRound != null
            ? `First divergence at round ${diff.divergenceRound}.`
            : 'No action divergence — identical outcomes.'}{' '}
          Event log: {diff.sharedEvents} shared, {diff.parentOnlyEvents} parent-only, {diff.forkOnlyEvents} fork-only events;{' '}
          {diff.divergentObjects} divergent objects.
        </CardDescription>
      </CardHeader>
      <CardContent className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 h-80">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--border))" />
              <XAxis dataKey="round" tick={{ fontSize: 12 }} stroke="hsl(var(--muted-foreground))" />
              <YAxis tick={{ fontSize: 12 }} stroke="hsl(var(--muted-foreground))" />
              <Tooltip
                contentStyle={{ backgroundColor: 'hsl(var(--card))', borderColor: 'hsl(var(--border))', fontSize: '12px' }}
                itemStyle={{ fontFamily: 'var(--font-mono)' }}
              />
              <Legend iconType="circle" wrapperStyle={{ fontSize: '12px' }} />
              {diff.divergenceRound != null && (
                <ReferenceLine
                  x={diff.divergenceRound}
                  stroke="hsl(var(--destructive))"
                  strokeDasharray="4 4"
                  label={{ value: 'diverges', fontSize: 11, fill: 'hsl(var(--destructive))', position: 'top' }}
                />
              )}
              <Line type="stepAfter" dataKey="Parent P1" stroke="hsl(var(--chart-1))" strokeWidth={1.5} strokeDasharray="5 3" dot={false} />
              <Line type="stepAfter" dataKey="Parent P2" stroke="hsl(var(--chart-2))" strokeWidth={1.5} strokeDasharray="5 3" dot={false} />
              <Line type="stepAfter" dataKey="Fork P1" stroke="hsl(var(--chart-1))" strokeWidth={2.5} dot={false} />
              <Line type="stepAfter" dataKey="Fork P2" stroke="hsl(var(--chart-2))" strokeWidth={2.5} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div>
          <div className="grid grid-cols-3 gap-2 text-[10px] uppercase font-bold tracking-wider text-muted-foreground pb-2 border-b">
            <span>Metric</span>
            <span className="text-right">Parent</span>
            <span className="text-right">Fork</span>
          </div>
          {statRow('P1 Total', formatNumber(diff.parentSummary.player1TotalPayoff), formatNumber(diff.forkSummary.player1TotalPayoff))}
          {statRow('P2 Total', formatNumber(diff.parentSummary.player2TotalPayoff), formatNumber(diff.forkSummary.player2TotalPayoff))}
          {statRow('Cooperation', formatPercent(diff.parentSummary.cooperationRate), formatPercent(diff.forkSummary.cooperationRate))}
          {statRow('Nash Deviation', formatPercent(diff.parentSummary.nashDeviationScore), formatPercent(diff.forkSummary.nashDeviationScore))}
        </div>
      </CardContent>
    </Card>
  );
}

// ── Trace panel ─────────────────────────────────────────────────────────────

export function TracePanel({ experimentId }: { experimentId: number }) {
  const [open, setOpen] = useState(false);
  const { data: trace, isLoading } = useGetExperimentTrace(experimentId, {
    query: { enabled: open, queryKey: getGetExperimentTraceQueryKey(experimentId), retry: false },
  });

  return (
    <Card data-testid="card-trace">
      <Collapsible open={open} onOpenChange={setOpen}>
        <CollapsibleTrigger asChild>
          <CardHeader className="cursor-pointer select-none hover:bg-muted/30 transition-colors">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <ScrollText className="w-5 h-5 text-muted-foreground" />
                <CardTitle>Engine Trace</CardTitle>
              </div>
              <ChevronDown className={`w-4 h-4 text-muted-foreground transition-transform ${open ? 'rotate-180' : ''}`} />
            </div>
            <CardDescription>Per-round event history from the engine's append-only log.</CardDescription>
          </CardHeader>
        </CollapsibleTrigger>
        <CollapsibleContent>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-40 w-full" />
            ) : trace ? (
              <div className="max-h-96 overflow-y-auto border rounded-md divide-y font-mono text-xs">
                {trace.events
                  .filter((e) => e.type === 'round.played' || e.type === 'run.completed' || e.type === 'patch.applied' || e.type === 'object.created')
                  .map((e) => (
                    <div key={e.eventId} className="p-2.5 flex flex-col gap-1 hover:bg-muted/40">
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className="text-[9px]">{e.type}</Badge>
                        {e.roundNumber != null && <span className="text-muted-foreground">round {e.roundNumber}</span>}
                        <span className="text-muted-foreground/50 ml-auto">{e.eventId}</span>
                      </div>
                      {e.type === 'round.played' && (
                        <div className="grid gap-0.5 text-muted-foreground pl-1">
                          <span>
                            <span className="text-chart-1 font-bold">P1 [{e.strategy1Slug}]</span> → action {e.player1Action}: {e.player1Reasoning}
                          </span>
                          <span>
                            <span className="text-chart-2 font-bold">P2 [{e.strategy2Slug}]</span> → action {e.player2Action}: {e.player2Reasoning}
                          </span>
                        </div>
                      )}
                    </div>
                  ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground py-4 text-center">No trace available for this experiment.</p>
            )}
          </CardContent>
        </CollapsibleContent>
      </Collapsible>
    </Card>
  );
}
