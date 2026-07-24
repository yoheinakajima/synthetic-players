import { useListGames } from '@workspace/api-client-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Link } from 'wouter';

export default function Games() {
  const { data: games, isLoading } = useListGames();

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div>
        <h1 className="text-3xl font-serif font-bold tracking-tight">Game Catalog</h1>
        <p className="text-muted-foreground mt-1">Library of canonical game theory scenarios.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {isLoading ? (
          Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-64 w-full" />
          ))
        ) : (
          games?.map((game) => (
            <Link key={game.id} href={`/games/${game.id}`}>
              <Card className="hover:border-primary/50 transition-colors cursor-pointer h-full flex flex-col group">
                <CardHeader>
                  <div className="flex justify-between items-start gap-4">
                    <CardTitle className="text-lg group-hover:text-primary transition-colors">
                      {game.name}
                    </CardTitle>
                    <Badge variant="outline" className="shrink-0 uppercase text-[10px] tracking-wider">
                      {game.category.replace('_', ' ')}
                    </Badge>
                  </div>
                  <CardDescription className="line-clamp-2">
                    {game.description}
                  </CardDescription>
                </CardHeader>
                <CardContent className="flex-1 flex flex-col justify-end">
                  <div className="mt-4 p-4 bg-muted/50 rounded-md border">
                    <p className="text-[10px] uppercase font-bold text-muted-foreground mb-2 tracking-wider">
                      Payoff Matrix Preview
                    </p>
                    <MatrixPreview matrixJson={game.payoffMatrix} actionLabels={game.actionLabels} />
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))
        )}
      </div>
    </div>
  );
}

function MatrixPreview({ matrixJson, actionLabels }: { matrixJson: string, actionLabels: string[] }) {
  try {
    const matrix = JSON.parse(matrixJson);
    return (
      <table className="w-full text-xs font-mono text-center">
        <tbody>
          {matrix.slice(0, 2).map((row: any[], i: number) => (
            <tr key={i}>
              {row.slice(0, 2).map((cell: number[], j: number) => (
                <td key={j} className="p-1 border bg-card text-foreground whitespace-nowrap">
                  {cell[0]}, {cell[1]}
                </td>
              ))}
              {row.length > 2 && <td className="p-1 text-muted-foreground">...</td>}
            </tr>
          ))}
          {matrix.length > 2 && (
            <tr><td colSpan={2} className="p-1 text-muted-foreground text-center">...</td></tr>
          )}
        </tbody>
      </table>
    );
  } catch (e) {
    return <span className="text-xs text-destructive">Invalid matrix data</span>;
  }
}
