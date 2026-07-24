import { 
  useGetDashboardStats, 
  useGetRecentActivity, 
  useGetStrategyLeaderboard, 
  useGetGameSummaries 
} from '@workspace/api-client-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';
import { Link } from 'wouter';
import { formatPercent, formatNumber, formatDateTime } from '@/lib/format';
import { LineChart, Line, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { Activity, TestTubes, FileText, Target, Trophy } from 'lucide-react';

export default function Dashboard() {
  const { data: stats, isLoading: statsLoading } = useGetDashboardStats();
  const { data: activity, isLoading: activityLoading } = useGetRecentActivity({ limit: 5 });
  const { data: leaderboard, isLoading: leaderboardLoading } = useGetStrategyLeaderboard();
  const { data: games, isLoading: gamesLoading } = useGetGameSummaries();

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <h1 className="text-3xl font-serif font-bold tracking-tight">Lab Dashboard</h1>
          <p className="text-muted-foreground mt-1">Overview of ongoing game theory research and empirical data.</p>
        </div>
        <div className="flex gap-2">
          <Link href="/experiments/new" className="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground shadow hover:bg-primary/90 h-9 px-4 py-2">
            New Experiment
          </Link>
        </div>
      </div>

      {/* Key Stats Panel */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Total Experiments" value={stats?.totalExperiments} icon={TestTubes} isLoading={statsLoading} />
        <StatCard title="Games Covered" value={stats?.gamesCovered} icon={Target} isLoading={statsLoading} />
        <StatCard title="Claims Generated" value={stats?.claimsGenerated} icon={Activity} isLoading={statsLoading} />
        <StatCard title="Papers Published" value={stats?.papersGenerated} icon={FileText} isLoading={statsLoading} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Leaderboard */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Trophy className="w-5 h-5 text-muted-foreground" />
              <CardTitle>Strategy Leaderboard</CardTitle>
            </div>
            <CardDescription>Top performing strategies across all completed experiments.</CardDescription>
          </CardHeader>
          <CardContent>
            {leaderboardLoading ? (
              <div className="space-y-4">
                {[1,2,3,4].map(i => <Skeleton key={i} className="h-12 w-full" />)}
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm font-mono text-left">
                  <thead>
                    <tr className="border-b text-muted-foreground">
                      <th className="pb-3 font-medium">Rank</th>
                      <th className="pb-3 font-medium">Strategy</th>
                      <th className="pb-3 font-medium">Type</th>
                      <th className="pb-3 font-medium text-right">Avg Payoff</th>
                      <th className="pb-3 font-medium text-right">Coop Rate</th>
                    </tr>
                  </thead>
                  <tbody>
                    {leaderboard?.map((row) => (
                      <tr key={row.strategyId} className="border-b last:border-0 hover:bg-muted/50 transition-colors">
                        <td className="py-3">#{row.rank}</td>
                        <td className="py-3 font-medium text-foreground">{row.strategyName}</td>
                        <td className="py-3">
                          <Badge variant="outline" className="font-sans text-xs font-normal">
                            {row.strategyType.replace('_', ' ')}
                          </Badge>
                        </td>
                        <td className="py-3 text-right">{formatNumber(row.avgPayoff)}</td>
                        <td className="py-3 text-right">{formatPercent(row.cooperationRate)}</td>
                      </tr>
                    ))}
                    {(!leaderboard || leaderboard.length === 0) && (
                      <tr>
                        <td colSpan={5} className="py-8 text-center text-muted-foreground font-sans">
                          No data available. Run experiments to populate leaderboard.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recent Activity Feed */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>Latest events in the lab</CardDescription>
          </CardHeader>
          <CardContent>
            {activityLoading ? (
              <div className="space-y-4">
                {[1,2,3,4].map(i => <Skeleton key={i} className="h-10 w-full" />)}
              </div>
            ) : (
              <div className="space-y-6">
                {activity?.map((item) => (
                  <div key={item.id} className="flex gap-4 relative">
                    <div className="w-2 h-2 rounded-full bg-primary mt-1.5 shrink-0" />
                    <div className="flex-1 space-y-1">
                      <p className="text-sm font-medium leading-none">{item.title}</p>
                      <p className="text-xs text-muted-foreground">{item.description}</p>
                      <p className="text-[10px] text-muted-foreground font-mono mt-1">
                        {formatDateTime(item.timestamp)}
                      </p>
                    </div>
                  </div>
                ))}
                {(!activity || activity.length === 0) && (
                  <p className="text-sm text-muted-foreground text-center py-4">No recent activity.</p>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Game Coverage */}
      <div>
        <h2 className="text-xl font-serif font-semibold mb-4">Game Coverage</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {gamesLoading ? (
             [1,2,3,4].map(i => <Skeleton key={i} className="h-32 w-full" />)
          ) : (
            games?.map(game => (
              <Link key={game.gameId} href={`/games/${game.gameId}`}>
                <Card className="hover:border-primary/50 transition-colors cursor-pointer group h-full">
                  <CardHeader className="p-4 pb-2">
                    <div className="flex justify-between items-start">
                      <CardTitle className="text-base group-hover:text-primary transition-colors">
                        {game.gameName}
                      </CardTitle>
                      <Badge variant="secondary" className="text-[10px]">{game.category.replace('_', ' ')}</Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="p-4 pt-0">
                    <div className="flex items-end justify-between mt-4">
                      <div className="space-y-1">
                        <p className="text-2xl font-mono tracking-tight">{game.experimentsRun}</p>
                        <p className="text-[10px] text-muted-foreground uppercase font-semibold">Experiments</p>
                      </div>
                      <div className="w-16 h-8">
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={[{ value: game.avgCooperationRate || 0 }, { value: 1 - (game.avgCooperationRate || 0) }]}>
                            <Bar dataKey="value" fill="hsl(var(--primary))" radius={[2, 2, 0, 0]} />
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

function StatCard({ title, value, icon: Icon, isLoading }: any) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
        <Icon className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <Skeleton className="h-8 w-20" />
        ) : (
          <div className="text-2xl font-bold font-mono">{value ?? '0'}</div>
        )}
      </CardContent>
    </Card>
  );
}
