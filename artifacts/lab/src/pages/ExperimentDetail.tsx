import { useParams } from 'wouter';
import { 
  useGetExperiment, 
  useListRounds, 
  useRunExperiment, 
  useGetAnalysis, 
  useCreateAnalysis,
  getGetExperimentQueryKey,
  getListRoundsQueryKey,
  getGetAnalysisQueryKey
} from '@workspace/api-client-react';
import { useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { useToast } from '@/hooks/use-toast';
import { formatPercent, formatNumber } from '@/lib/format';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { Play, BrainCircuit, Activity } from 'lucide-react';

interface MetricEntry { label: string; value: string; big?: boolean }

/**
 * Class-aware analysis panel entries. Zero-sum games get exploitability and
 * distribution tests — never cooperation rates (undefined there). The legacy
 * per-round "Nash Eq. Rate" is only shown for games with pure equilibria.
 */
function metricEntries(
  metricsJson: string | null | undefined,
  nashEquilibriumRate: number,
  mutualCooperationRate: number,
  p1Deviation: number,
  p2Deviation: number,
): MetricEntry[] {
  const pct = (v: number | null | undefined) => (v == null ? 'n/a' : `${(v * 100).toFixed(1)}%`);
  const num = (v: number | null | undefined, d = 3) => (v == null ? 'n/a' : v.toFixed(d));

  let m: any = null;
  if (metricsJson) {
    try { m = JSON.parse(metricsJson); } catch { m = null; }
  }

  if (!m) {
    // Legacy v1 analysis fallback
    return [
      { label: 'Nash Eq. Rate', value: pct(nashEquilibriumRate), big: true },
      { label: 'Mutual Coop', value: pct(mutualCooperationRate), big: true },
      { label: 'P1 Deviation', value: pct(p1Deviation) },
      { label: 'P2 Deviation', value: pct(p2Deviation) },
    ];
  }

  if (m.gameClass === 'zero_sum') {
    return [
      { label: 'Tracker Exploitability P1', value: num(m.conditionalExploitabilityP1), big: true },
      { label: 'Tracker Exploitability P2', value: num(m.conditionalExploitabilityP2), big: true },
      { label: 'Marginal Exploit. P1', value: num(m.marginalExploitabilityP1) },
      { label: 'Marginal Exploit. P2', value: num(m.marginalExploitabilityP2) },
      { label: 'G-test vs Nash (p)', value: num(m.gTestPValue) },
      { label: 'Pure Eq. Rate', value: m.eqOutcomeRate == null ? 'n/a (mixed eq.)' : pct(m.eqOutcomeRate) },
    ];
  }

  if (m.gameClass === 'coordination') {
    return [
      { label: 'Equilibrium Outcomes', value: pct(m.eqOutcomeRate), big: true },
      { label: 'Coordination Rate', value: pct(m.coordinationRate), big: true },
      { label: 'Welfare Ratio', value: num(m.welfareRatio) },
      { label: 'Mutual "Cooperate"', value: pct(m.mutualCooperationRate) },
    ];
  }

  // social_dilemma
  return [
    { label: 'Welfare Ratio', value: num(m.welfareRatio), big: true },
    { label: 'Mutual Cooperation', value: pct(m.mutualCooperationRate), big: true },
    { label: 'Coop Rate P1', value: pct(m.actionCooperationRateP1) },
    { label: 'Coop Rate P2', value: pct(m.actionCooperationRateP2) },
    { label: 'Pure Eq. Outcomes', value: pct(m.eqOutcomeRate) },
    { label: 'Joint Payoff / Round', value: num(m.jointPayoffPerRound, 2) },
  ];
}

export default function ExperimentDetail() {
  const { id } = useParams();
  const experimentId = parseInt(id || '0', 10);
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const { data: exp, isLoading: expLoading } = useGetExperiment(experimentId, { 
    query: { enabled: !!experimentId, queryKey: getGetExperimentQueryKey(experimentId) } 
  });
  const { data: rounds, isLoading: roundsLoading } = useListRounds(experimentId, {
    query: { enabled: !!experimentId, queryKey: getListRoundsQueryKey(experimentId) }
  });
  const { data: analysis, isLoading: analysisLoading } = useGetAnalysis(experimentId, {
    query: { enabled: exp?.status === 'completed', queryKey: getGetAnalysisQueryKey(experimentId), retry: false }
  });

  const runMutation = useRunExperiment();
  const analyzeMutation = useCreateAnalysis();

  const handleRun = () => {
    runMutation.mutate({ id: experimentId }, {
      onSuccess: () => {
        toast({ title: "Experiment Complete" });
        queryClient.invalidateQueries({ queryKey: getGetExperimentQueryKey(experimentId) });
        queryClient.invalidateQueries({ queryKey: getListRoundsQueryKey(experimentId) });
      },
      onError: () => toast({ title: "Run Failed", variant: "destructive" })
    });
  };

  const handleAnalyze = () => {
    analyzeMutation.mutate({ experimentId }, {
      onSuccess: () => {
        toast({ title: "Analysis Complete" });
        queryClient.invalidateQueries({ queryKey: getGetAnalysisQueryKey(experimentId) });
      },
      onError: () => toast({ title: "Analysis Failed", variant: "destructive" })
    });
  };

  if (expLoading) {
    return <div className="space-y-4"><Skeleton className="h-12 w-1/3" /><Skeleton className="h-64 w-full" /></div>;
  }
  if (!exp) return <div>Experiment not found</div>;

  // Chart data computation
  let chartData: any[] = [];
  if (rounds && rounds.length > 0) {
    let p1Sum = 0;
    let p2Sum = 0;
    chartData = rounds.map(r => {
      p1Sum += r.player1Payoff;
      p2Sum += r.player2Payoff;
      return {
        round: r.roundNumber,
        P1: p1Sum,
        P2: p2Sum,
      };
    });
  }

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex justify-between items-start gap-4">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <Badge variant="outline" className="font-mono">EXP-{exp.id.toString().padStart(4, '0')}</Badge>
            <Badge variant={
              exp.status === 'completed' ? 'secondary' : 
              exp.status === 'failed' ? 'destructive' : 
              exp.status === 'running' ? 'default' : 'outline'
            } className="uppercase text-[10px]">
              {exp.status}
            </Badge>
          </div>
          <h1 className="text-3xl font-serif font-bold tracking-tight">
            {exp.game?.name}
          </h1>
          <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mt-2 text-sm text-muted-foreground font-mono">
            <span>P1: {exp.player1Strategy?.name}</span>
            <span>vs</span>
            <span>P2: {exp.player2Strategy?.name}</span>
            <span className="text-muted-foreground/50">|</span>
            <span>{exp.numRounds} Rounds</span>
            <span className="text-muted-foreground/50">|</span>
            <span data-testid="text-seed">Seed: {exp.seed ?? 'unseeded (v1 legacy)'}</span>
            {exp.batchLabel && (
              <Badge variant="outline" className="text-[9px] font-mono">{exp.batchLabel}</Badge>
            )}
          </div>
        </div>
        <div className="flex gap-2">
          {exp.status === 'pending' && (
            <Button onClick={handleRun} disabled={runMutation.isPending} className="gap-2">
              <Play className="w-4 h-4" />
              {runMutation.isPending ? "Running..." : "Execute Run"}
            </Button>
          )}
          {exp.status === 'completed' && !analysis && (
            <Button onClick={handleAnalyze} disabled={analyzeMutation.isPending} className="gap-2 bg-primary">
              <BrainCircuit className="w-4 h-4" />
              {analyzeMutation.isPending ? "Analyzing..." : "Generate Analysis"}
            </Button>
          )}
        </div>
      </div>

      {exp.notes && (
        <div className="p-4 bg-muted/30 border rounded-md text-sm text-muted-foreground">
          <strong className="text-foreground">Notes:</strong> {exp.notes}
        </div>
      )}

      {exp.status === 'completed' && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="pt-5">
              <p className="text-[10px] uppercase text-muted-foreground font-bold tracking-wider mb-1">P1 Payoff / Round</p>
              <p className="text-2xl font-mono" data-testid="text-p1-avg">{exp.player1AvgPayoffPerRound?.toFixed(2) ?? '—'}</p>
              <p className="text-[11px] text-muted-foreground font-mono mt-1">total {exp.player1TotalPayoff?.toFixed(1) ?? '—'} over {exp.numRounds} rounds</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-5">
              <p className="text-[10px] uppercase text-muted-foreground font-bold tracking-wider mb-1">P2 Payoff / Round</p>
              <p className="text-2xl font-mono" data-testid="text-p2-avg">{exp.player2AvgPayoffPerRound?.toFixed(2) ?? '—'}</p>
              <p className="text-[11px] text-muted-foreground font-mono mt-1">total {exp.player2TotalPayoff?.toFixed(1) ?? '—'} over {exp.numRounds} rounds</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-5">
              <p className="text-[10px] uppercase text-muted-foreground font-bold tracking-wider mb-1">Joint / Round</p>
              <p className="text-2xl font-mono">
                {exp.player1AvgPayoffPerRound != null && exp.player2AvgPayoffPerRound != null
                  ? (exp.player1AvgPayoffPerRound + exp.player2AvgPayoffPerRound).toFixed(2)
                  : '—'}
              </p>
              <p className="text-[11px] text-muted-foreground font-mono mt-1">sum of both players</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-5">
              <p className="text-[10px] uppercase text-muted-foreground font-bold tracking-wider mb-1">Reproducibility</p>
              <p className="text-2xl font-mono">{exp.seed != null ? 'seeded' : 'legacy'}</p>
              <p className="text-[11px] text-muted-foreground font-mono mt-1">{exp.seed != null ? `re-run with seed ${exp.seed} for identical rounds` : 'pre-seeding v1 run'}</p>
            </CardContent>
          </Card>
        </div>
      )}

      {exp.status === 'completed' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Chart */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>Cumulative Payoffs</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-80 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--border))" />
                    <XAxis dataKey="round" tick={{fontSize: 12}} stroke="hsl(var(--muted-foreground))" />
                    <YAxis tick={{fontSize: 12}} stroke="hsl(var(--muted-foreground))" />
                    <Tooltip 
                      contentStyle={{ backgroundColor: 'hsl(var(--card))', borderColor: 'hsl(var(--border))', fontSize: '12px' }}
                      itemStyle={{ fontFamily: 'var(--font-mono)' }}
                    />
                    <Legend iconType="circle" wrapperStyle={{ fontSize: '12px' }} />
                    <Line type="stepAfter" dataKey="P1" stroke="hsl(var(--chart-1))" strokeWidth={2} dot={false} />
                    <Line type="stepAfter" dataKey="P2" stroke="hsl(var(--chart-2))" strokeWidth={2} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          {/* Analysis Panel */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Activity className="w-5 h-5 text-muted-foreground" />
                <CardTitle>Analysis</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              {analysisLoading ? <Skeleton className="h-48 w-full" /> : analysis ? (
                <div className="space-y-6">
                  <div className="grid grid-cols-2 gap-4">
                    {metricEntries(analysis.metricsJson, analysis.nashEquilibriumRate, analysis.mutualCooperationRate, analysis.player1PayoffDeviation, analysis.player2PayoffDeviation).map((entry) => (
                      <div key={entry.label}>
                        <p className="text-[10px] uppercase text-muted-foreground font-bold tracking-wider mb-1">{entry.label}</p>
                        <p className={entry.big ? "text-2xl font-mono" : "text-lg font-mono text-muted-foreground"}>{entry.value}</p>
                      </div>
                    ))}
                  </div>
                  <div className="pt-4 border-t text-sm text-muted-foreground leading-relaxed">
                    {analysis.summary}
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground text-sm">
                  No statistical analysis generated yet.
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* Rounds Table */}
      <Card>
        <CardHeader>
          <CardTitle>Round Log</CardTitle>
          <CardDescription>Action and payoff sequence.</CardDescription>
        </CardHeader>
        <CardContent>
          {roundsLoading ? <Skeleton className="h-32 w-full" /> : (
            <div className="overflow-x-auto h-96 overflow-y-auto border rounded-md relative">
              <table className="w-full text-sm font-mono text-left">
                <thead className="sticky top-0 bg-card z-10 shadow-sm">
                  <tr className="border-b text-muted-foreground">
                    <th className="p-3 font-medium">Round</th>
                    <th className="p-3 font-medium">P1 Action</th>
                    <th className="p-3 font-medium">P2 Action</th>
                    <th className="p-3 font-medium text-right">P1 Payoff</th>
                    <th className="p-3 font-medium text-right">P2 Payoff</th>
                    <th className="p-3 font-medium text-center">Nash</th>
                  </tr>
                </thead>
                <tbody>
                  {rounds?.map(r => (
                    <tr key={r.id} className={`border-b last:border-0 transition-colors ${r.isNashOutcome ? 'bg-primary/5' : 'hover:bg-muted/50'}`}>
                      <td className="p-3 text-muted-foreground">{r.roundNumber}</td>
                      <td className="p-3 font-bold text-chart-1">{exp?.game?.actionLabels[r.player1Action] || r.player1Action}</td>
                      <td className="p-3 font-bold text-chart-2">{exp?.game?.actionLabels[r.player2Action] || r.player2Action}</td>
                      <td className="p-3 text-right">{r.player1Payoff}</td>
                      <td className="p-3 text-right">{r.player2Payoff}</td>
                      <td className="p-3 text-center">
                        {r.isNashOutcome && <Badge variant="outline" className="text-[8px] bg-background">NASH</Badge>}
                      </td>
                    </tr>
                  ))}
                  {(!rounds || rounds.length === 0) && (
                    <tr>
                      <td colSpan={6} className="p-8 text-center text-muted-foreground font-sans">
                        No rounds recorded.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
