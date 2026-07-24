import { useListExperiments } from '@workspace/api-client-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Link } from 'wouter';
import { formatDateTime, formatPercent } from '@/lib/format';
import { Microscope, Plus } from 'lucide-react';

export default function Experiments() {
  const { data: experiments, isLoading } = useListExperiments();

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <h1 className="text-3xl font-serif font-bold tracking-tight">Experiments</h1>
          <p className="text-muted-foreground mt-1">Empirical runs matching strategies against canonical games.</p>
        </div>
        <Link href="/experiments/new" className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground shadow hover:bg-primary/90 h-9 px-4 py-2 gap-2">
          <Plus className="w-4 h-4" />
          New Experiment
        </Link>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Microscope className="w-5 h-5 text-muted-foreground" />
            <CardTitle>Experiment Log</CardTitle>
          </div>
          <CardDescription>Comprehensive record of all experimental runs.</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-4">
              {[1, 2, 3, 4, 5].map(i => <Skeleton key={i} className="h-12 w-full" />)}
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm font-mono text-left">
                <thead>
                  <tr className="border-b text-muted-foreground">
                    <th className="pb-3 font-medium">ID</th>
                    <th className="pb-3 font-medium">Game</th>
                    <th className="pb-3 font-medium">P1 Strategy</th>
                    <th className="pb-3 font-medium">P2 Strategy</th>
                    <th className="pb-3 font-medium">Rounds</th>
                    <th className="pb-3 font-medium">Status</th>
                    <th className="pb-3 font-medium text-right">Coop Rate</th>
                    <th className="pb-3 font-medium text-right">Date</th>
                  </tr>
                </thead>
                <tbody>
                  {experiments?.map(exp => (
                    <tr key={exp.id} className="border-b last:border-0 hover:bg-muted/50 transition-colors">
                      <td className="py-3">
                        <Link href={`/experiments/${exp.id}`} className="text-primary hover:underline font-bold">
                          EXP-{exp.id.toString().padStart(4, '0')}
                        </Link>
                      </td>
                      <td className="py-3">{exp.gameName}</td>
                      <td className="py-3">{exp.player1StrategyName}</td>
                      <td className="py-3">{exp.player2StrategyName}</td>
                      <td className="py-3">{exp.numRounds}</td>
                      <td className="py-3">
                        <Badge variant={
                          exp.status === 'completed' ? 'secondary' : 
                          exp.status === 'failed' ? 'destructive' : 
                          exp.status === 'running' ? 'default' : 'outline'
                        } className="text-[10px] uppercase">
                          {exp.status}
                        </Badge>
                      </td>
                      <td className="py-3 text-right">
                        {exp.status === 'completed' ? formatPercent(exp.cooperationRate) : '—'}
                      </td>
                      <td className="py-3 text-right text-muted-foreground">{formatDateTime(exp.createdAt)}</td>
                    </tr>
                  ))}
                  {experiments?.length === 0 && (
                    <tr>
                      <td colSpan={8} className="py-8 text-center text-muted-foreground font-sans">
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
