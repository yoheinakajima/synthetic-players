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
            {exp.game?.name || exp.gameName}
          </h1>
          <div className="flex items-center gap-4 mt-2 text-sm text-muted-foreground font-mono">
            <span>P1: {exp.player1Strategy?.name || exp.player1StrategyName}</span>
            <span>vs</span>
            <span>P2: {exp.player2Strategy?.name || exp.player2StrategyName}</span>
            <span className="text-muted-foreground/50">|</span>
            <span>{exp.numRounds} Rounds</span>
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
                    <div>
                      <p className="text-[10px] uppercase text-muted-foreground font-bold tracking-wider mb-1">Nash Eq. Rate</p>
                      <p className="text-2xl font-mono">{formatPercent(analysis.nashEquilibriumRate)}</p>
                    </div>
                    <div>
                      <p className="text-[10px] uppercase text-muted-foreground font-bold tracking-wider mb-1">Mutual Coop</p>
                      <p className="text-2xl font-mono">{formatPercent(analysis.mutualCooperationRate)}</p>
                    </div>
                    <div>
                      <p className="text-[10px] uppercase text-muted-foreground font-bold tracking-wider mb-1">P1 Deviation</p>
                      <p className="text-lg font-mono text-muted-foreground">{formatPercent(analysis.player1PayoffDeviation)}</p>
                    </div>
                    <div>
                      <p className="text-[10px] uppercase text-muted-foreground font-bold tracking-wider mb-1">P2 Deviation</p>
                      <p className="text-lg font-mono text-muted-foreground">{formatPercent(analysis.player2PayoffDeviation)}</p>
                    </div>
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
