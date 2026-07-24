import { useMemo, useState } from 'react';
import { useListExperiments } from '@workspace/api-client-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Link } from 'wouter';
import { formatDateTime } from '@/lib/format';
import { Microscope, Plus } from 'lucide-react';

const ALL = '__all__';
const SINGLES = '__singles__';

export default function Experiments() {
  const { data: experiments, isLoading } = useListExperiments();
  const [batchFilter, setBatchFilter] = useState<string>(ALL);

  const batchLabels = useMemo(() => {
    const labels = new Set<string>();
    experiments?.forEach(e => { if (e.batchLabel) labels.add(e.batchLabel); });
    return [...labels].sort();
  }, [experiments]);

  const filtered = useMemo(() => {
    if (!experiments) return experiments;
    if (batchFilter === ALL) return experiments;
    if (batchFilter === SINGLES) return experiments.filter(e => !e.batchLabel);
    return experiments.filter(e => e.batchLabel === batchFilter);
  }, [experiments, batchFilter]);

  const perRound = (v?: number | null) => (v == null ? '—' : v.toFixed(2));

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <h1 className="text-3xl font-serif font-bold tracking-tight">Experiments</h1>
          <p className="text-muted-foreground mt-1">Empirical runs matching strategies against canonical games. Seeded runs are exactly reproducible.</p>
        </div>
        <Link href="/experiments/new" className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground shadow hover:bg-primary/90 h-9 px-4 py-2 gap-2">
          <Plus className="w-4 h-4" />
          New Experiment
        </Link>
      </div>

      <Card>
        <CardHeader>
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2">
                <Microscope className="w-5 h-5 text-muted-foreground" />
                <CardTitle>Experiment Log</CardTitle>
              </div>
              <CardDescription className="mt-1.5">
                {filtered ? `${filtered.length} runs` : 'Comprehensive record of all experimental runs.'}
              </CardDescription>
            </div>
            <Select value={batchFilter} onValueChange={setBatchFilter}>
              <SelectTrigger className="w-full md:w-[320px] font-mono text-xs" data-testid="select-batch-filter">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value={ALL}>All experiments</SelectItem>
                <SelectItem value={SINGLES}>Single runs (no batch)</SelectItem>
                {batchLabels.map(label => (
                  <SelectItem key={label} value={label} className="font-mono text-xs">{label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-4">
              {[1, 2, 3, 4, 5].map(i => <Skeleton key={i} className="h-12 w-full" />)}
            </div>
          ) : (
            <div className="overflow-x-auto max-h-[70vh] overflow-y-auto border rounded-md">
              <table className="w-full text-sm font-mono text-left">
                <thead className="sticky top-0 bg-card z-10 shadow-sm">
                  <tr className="border-b text-muted-foreground">
                    <th className="p-3 font-medium">ID</th>
                    <th className="p-3 font-medium">Game</th>
                    <th className="p-3 font-medium">Matchup</th>
                    <th className="p-3 font-medium text-right">Rounds</th>
                    <th className="p-3 font-medium text-right">Seed</th>
                    <th className="p-3 font-medium">Batch</th>
                    <th className="p-3 font-medium">Status</th>
                    <th className="p-3 font-medium text-right">Payoff / Round</th>
                    <th className="p-3 font-medium text-right">Date</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered?.map(exp => (
                    <tr key={exp.id} className="border-b last:border-0 hover:bg-muted/50 transition-colors">
                      <td className="p-3">
                        <Link href={`/experiments/${exp.id}`} className="text-primary hover:underline font-bold">
                          EXP-{exp.id.toString().padStart(4, '0')}
                        </Link>
                      </td>
                      <td className="p-3">{exp.gameName}</td>
                      <td className="p-3 text-xs">{exp.player1StrategyName} vs {exp.player2StrategyName}</td>
                      <td className="p-3 text-right">{exp.numRounds}</td>
                      <td className="p-3 text-right text-muted-foreground text-xs">{exp.seed ?? '—'}</td>
                      <td className="p-3">
                        {exp.batchLabel ? (
                          <Badge variant="outline" className="text-[9px] font-mono max-w-[180px] truncate block">{exp.batchLabel}</Badge>
                        ) : <span className="text-muted-foreground/50 text-xs">—</span>}
                      </td>
                      <td className="p-3">
                        <Badge variant={
                          exp.status === 'completed' ? 'secondary' :
                          exp.status === 'failed' ? 'destructive' :
                          exp.status === 'running' ? 'default' : 'outline'
                        } className="text-[10px] uppercase">
                          {exp.status}
                        </Badge>
                      </td>
                      <td className="p-3 text-right text-xs">
                        {exp.status === 'completed'
                          ? `${perRound(exp.player1AvgPayoffPerRound)} / ${perRound(exp.player2AvgPayoffPerRound)}`
                          : '—'}
                      </td>
                      <td className="p-3 text-right text-muted-foreground text-xs">{formatDateTime(exp.createdAt)}</td>
                    </tr>
                  ))}
                  {filtered?.length === 0 && (
                    <tr>
                      <td colSpan={9} className="p-8 text-center text-muted-foreground font-sans">
                        No experiments found.
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
