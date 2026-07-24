import { useState } from 'react';
import { useListClaims, useCreateClaim, useUpdateClaim, useListGames, getListClaimsQueryKey } from '@workspace/api-client-react';
import { useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useToast } from '@/hooks/use-toast';
import { Dna, Plus } from 'lucide-react';
import { formatDateTime } from '@/lib/format';

const claimSchema = z.object({
  title: z.string().min(1, "Title required"),
  statement: z.string().min(1, "Statement required"),
  gameId: z.coerce.number().min(1, "Game required"),
  evidenceSummary: z.string().optional(),
});

export default function Claims() {
  const { data: claims, isLoading } = useListClaims();
  const { data: games } = useListGames();
  const createMutation = useCreateClaim();
  const updateMutation = useUpdateClaim();
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
    },
  });

  const onSubmit = (values: z.infer<typeof claimSchema>) => {
    createMutation.mutate({ data: values }, {
      onSuccess: () => {
        toast({ title: "Claim formulated" });
        setIsDialogOpen(false);
        form.reset();
        queryClient.invalidateQueries({ queryKey: getListClaimsQueryKey() });
      },
      onError: () => toast({ title: "Failed to formulate claim", variant: "destructive" })
    });
  };

  const updateStatus = (id: number, status: 'hypothesis' | 'supported' | 'refuted' | 'inconclusive') => {
    updateMutation.mutate({ id, data: { status } }, {
      onSuccess: () => {
        toast({ title: "Status updated" });
        queryClient.invalidateQueries({ queryKey: getListClaimsQueryKey() });
      }
    });
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <h1 className="text-3xl font-serif font-bold tracking-tight">Research Claims</h1>
          <p className="text-muted-foreground mt-1">Testable propositions tracking experimental evidence.</p>
        </div>
        
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button className="gap-2">
              <Plus className="w-4 h-4" /> Formulate Claim
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-xl">
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

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {isLoading ? (
          Array.from({ length: 6 }).map((_, i) => <Skeleton key={i} className="h-48 w-full" />)
        ) : (
          claims?.map(claim => (
            <Card key={claim.id} className="flex flex-col">
              <CardHeader className="pb-3 border-b border-border/50">
                <div className="flex justify-between items-start gap-2">
                  <CardTitle className="text-base leading-tight">{claim.title}</CardTitle>
                  <Select value={claim.status} onValueChange={(val: any) => updateStatus(claim.id, val)}>
                    <SelectTrigger className={`h-6 text-[10px] uppercase w-[110px] ${
                      claim.status === 'supported' ? 'text-primary border-primary' : 
                      claim.status === 'refuted' ? 'text-destructive border-destructive' : 'text-muted-foreground'
                    }`}>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="hypothesis">HYPOTHESIS</SelectItem>
                      <SelectItem value="supported">SUPPORTED</SelectItem>
                      <SelectItem value="refuted">REFUTED</SelectItem>
                      <SelectItem value="inconclusive">INCONCLUSIVE</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="mt-2 flex items-center gap-2">
                  <Badge variant="secondary" className="text-[10px] font-mono">{claim.gameName}</Badge>
                </div>
              </CardHeader>
              <CardContent className="pt-4 flex-1">
                <p className="text-sm font-serif italic text-foreground mb-4">"{claim.statement}"</p>
                {claim.evidenceSummary && (
                  <div className="p-3 bg-muted/30 rounded border text-xs text-muted-foreground leading-relaxed">
                    <strong className="text-foreground font-sans text-[10px] uppercase tracking-wider block mb-1">Evidence:</strong>
                    {claim.evidenceSummary}
                  </div>
                )}
              </CardContent>
              <CardFooter className="pt-0 text-[10px] text-muted-foreground font-mono">
                Updated {formatDateTime(claim.updatedAt || claim.createdAt)}
              </CardFooter>
            </Card>
          ))
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
