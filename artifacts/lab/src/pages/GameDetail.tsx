import { useParams, Link } from 'wouter';
import { 
  useGetGame, 
  useListExperiments, 
  useListClaims, 
  getGetGameQueryKey 
} from '@workspace/api-client-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { formatDateTime, formatPercent, formatNumber } from '@/lib/format';

export default function GameDetail() {
  const { id } = useParams();
  const gameId = parseInt(id || '0', 10);

  const { data: game, isLoading: gameLoading } = useGetGame(gameId, { 
    query: { enabled: !!gameId, queryKey: getGetGameQueryKey(gameId) } 
  });
  const { data: experiments, isLoading: expLoading } = useListExperiments({ gameId });
  const { data: claims, isLoading: claimsLoading } = useListClaims({ gameId });

  if (gameLoading) {
    return <div className="space-y-4"><Skeleton className="h-12 w-1/3" /><Skeleton className="h-64 w-full" /></div>;
  }

  if (!game) return <div>Game not found</div>;

  let matrix = [];
  let nash = [];
  try { matrix = JSON.parse(game.payoffMatrix); } catch (e) {}
  try { nash = JSON.parse(game.nashEquilibria); } catch (e) {}

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex justify-between items-start gap-4">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <Badge className="uppercase tracking-widest text-[10px]">{game.category.replace('_', ' ')}</Badge>
            {game.theoreticalCooperationRate !== null && (
              <span className="text-xs text-muted-foreground font-mono">
                Theoretical Coop: {formatPercent(game.theoreticalCooperationRate)}
              </span>
            )}
          </div>
          <h1 className="text-4xl font-serif font-bold tracking-tight">{game.name}</h1>
          <p className="text-muted-foreground mt-4 max-w-3xl text-lg leading-relaxed">{game.description}</p>
        </div>
        <Link href={`/experiments/new?gameId=${game.id}`} className="inline-flex items-center justify-center rounded-md text-sm font-medium bg-primary text-primary-foreground h-10 px-4 py-2 hover:bg-primary/90">
          Run Experiment
        </Link>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Payoff Matrix */}
        <Card>
          <CardHeader>
            <CardTitle>Payoff Matrix</CardTitle>
            <CardDescription>Normal form representation (Row P1, Col P2)</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm font-mono border-collapse">
                <thead>
                  <tr>
                    <th className="p-2 border-b border-r"></th>
                    {game.actionLabels.map(label => (
                      <th key={label} className="p-2 border-b text-center bg-muted/30">{label}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {matrix.map((row: any[], i: number) => (
                    <tr key={i}>
                      <th className="p-2 border-r text-right bg-muted/30 whitespace-nowrap">
                        {game.actionLabels[i]}
                      </th>
                      {row.map((cell: number[], j: number) => {
                        const isNash = nash.some((n: any[]) => n[0] === i && n[1] === j);
                        return (
                          <td key={j} className={`p-4 border text-center relative ${isNash ? 'bg-primary/5 font-bold' : ''}`}>
                            {isNash && <div className="absolute top-1 left-1 text-[8px] text-primary uppercase">Nash</div>}
                            <span className="text-primary">{cell[0]}</span>
                            <span className="text-muted-foreground mx-1">,</span>
                            <span className="text-accent">{cell[1]}</span>
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {game.nashDescription && (
              <div className="mt-6 p-4 bg-muted/50 rounded-md border text-sm text-muted-foreground">
                <strong className="text-foreground">Analysis:</strong> {game.nashDescription}
              </div>
            )}
          </CardContent>
        </Card>

        <div className="space-y-8">
          {/* Claims */}
          <Card>
            <CardHeader>
              <CardTitle>Research Claims</CardTitle>
            </CardHeader>
            <CardContent>
              {claimsLoading ? <Skeleton className="h-24 w-full" /> : (
                <div className="space-y-4">
                  {claims?.length === 0 && <p className="text-sm text-muted-foreground">No claims formulated yet.</p>}
                  {claims?.map(claim => (
                    <div key={claim.id} className="p-3 border rounded-md">
                      <div className="flex items-center gap-2 mb-1">
                        <Badge variant={claim.status === 'supported' ? 'default' : claim.status === 'refuted' ? 'destructive' : 'outline'} className="text-[10px] uppercase">
                          {claim.status}
                        </Badge>
                        <span className="text-xs font-medium">{claim.title}</span>
                      </div>
                      <p className="text-sm text-muted-foreground">{claim.statement}</p>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Experiments Table */}
      <Card>
        <CardHeader>
          <CardTitle>Experiments</CardTitle>
          <CardDescription>Empirical runs for this game</CardDescription>
        </CardHeader>
        <CardContent>
          {expLoading ? <Skeleton className="h-32 w-full" /> : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm font-mono text-left">
                <thead>
                  <tr className="border-b text-muted-foreground">
                    <th className="pb-3 font-medium">ID</th>
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
                        <Link href={`/experiments/${exp.id}`} className="text-primary hover:underline">
                          EXP-{exp.id.toString().padStart(4, '0')}
                        </Link>
                      </td>
                      <td className="py-3">{exp.player1StrategyName}</td>
                      <td className="py-3">{exp.player2StrategyName}</td>
                      <td className="py-3">{exp.numRounds}</td>
                      <td className="py-3">
                        <Badge variant={exp.status === 'completed' ? 'secondary' : 'outline'} className="text-[10px] uppercase">
                          {exp.status}
                        </Badge>
                      </td>
                      <td className="py-3 text-right">{formatPercent(exp.cooperationRate)}</td>
                      <td className="py-3 text-right text-muted-foreground">{formatDateTime(exp.createdAt)}</td>
                    </tr>
                  ))}
                  {experiments?.length === 0 && (
                    <tr>
                      <td colSpan={7} className="py-8 text-center text-muted-foreground font-sans">
                        No experiments run for this game.
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
