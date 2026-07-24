import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useLocation } from 'wouter';
import { useListGames, useListStrategies, useCreateExperiment } from '@workspace/api-client-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import { Skeleton } from '@/components/ui/skeleton';

const formSchema = z.object({
  gameId: z.coerce.number().min(1, "Please select a game"),
  player1StrategyId: z.coerce.number().min(1, "Please select a strategy"),
  player2StrategyId: z.coerce.number().min(1, "Please select a strategy"),
  numRounds: z.coerce.number().min(1).max(200),
  notes: z.string().optional(),
});

export default function NewExperiment() {
  const [, setLocation] = useLocation();
  const { toast } = useToast();
  
  const { data: games, isLoading: gamesLoading } = useListGames();
  const { data: strategies, isLoading: strategiesLoading } = useListStrategies();
  const createMutation = useCreateExperiment();

  // Try to parse gameId from query string (if navigated from Game Detail)
  const searchParams = new URLSearchParams(window.location.search);
  const initialGameId = searchParams.get('gameId') ? parseInt(searchParams.get('gameId')!) : 0;

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      gameId: initialGameId,
      player1StrategyId: 0,
      player2StrategyId: 0,
      numRounds: 10,
      notes: '',
    },
  });

  function onSubmit(values: z.infer<typeof formSchema>) {
    createMutation.mutate({ data: values }, {
      onSuccess: (res) => {
        toast({ title: "Experiment created", description: `EXP-${res.id.toString().padStart(4, '0')} initialized.` });
        setLocation(`/experiments/${res.id}`);
      },
      onError: (err) => {
        toast({ title: "Error", description: "Failed to create experiment", variant: "destructive" });
      }
    });
  }

  if (gamesLoading || strategiesLoading) {
    return <div className="space-y-4 max-w-2xl mx-auto mt-8"><Skeleton className="h-12 w-1/3" /><Skeleton className="h-96 w-full" /></div>;
  }

  return (
    <div className="max-w-2xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500 pt-8">
      <div>
        <h1 className="text-3xl font-serif font-bold tracking-tight">New Experiment</h1>
        <p className="text-muted-foreground mt-1">Configure parameters for a new empirical run.</p>
      </div>

      <Card>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)}>
            <CardHeader>
              <CardTitle>Configuration</CardTitle>
              <CardDescription>Select the game and player strategies.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              
              <FormField
                control={form.control}
                name="gameId"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Game Scenario</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value ? field.value.toString() : ""}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select a game..." />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {games?.map(game => (
                          <SelectItem key={game.id} value={game.id.toString()}>
                            {game.name} <span className="text-muted-foreground text-xs ml-2">({game.category.replace('_', ' ')})</span>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 p-4 bg-muted/30 border rounded-md">
                <FormField
                  control={form.control}
                  name="player1StrategyId"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Player 1 Strategy</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value ? field.value.toString() : ""}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Select strategy..." />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          {strategies?.map(s => (
                            <SelectItem key={s.id} value={s.id.toString()}>
                              {s.name} <span className="text-muted-foreground text-xs ml-2">({s.type})</span>
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="player2StrategyId"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Player 2 Strategy</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value ? field.value.toString() : ""}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Select strategy..." />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          {strategies?.map(s => (
                            <SelectItem key={s.id} value={s.id.toString()}>
                              {s.name} <span className="text-muted-foreground text-xs ml-2">({s.type})</span>
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <FormField
                control={form.control}
                name="numRounds"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Number of Rounds</FormLabel>
                    <FormControl>
                      <Input type="number" min={1} max={200} {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="notes"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Notes (Optional)</FormLabel>
                    <FormControl>
                      <Textarea placeholder="Hypothesis or conditions for this run..." {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

            </CardContent>
            <CardFooter className="flex justify-between border-t p-6">
              <Button type="button" variant="outline" onClick={() => setLocation('/experiments')}>
                Cancel
              </Button>
              <Button type="submit" disabled={createMutation.isPending}>
                {createMutation.isPending ? "Initializing..." : "Create Experiment"}
              </Button>
            </CardFooter>
          </form>
        </Form>
      </Card>
    </div>
  );
}
