import { useState } from 'react';
import { useListPapers, useGeneratePaper, getListPapersQueryKey } from '@workspace/api-client-react';
import { useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { useToast } from '@/hooks/use-toast';
import { Link } from 'wouter';
import { FileText, Plus } from 'lucide-react';
import { formatDateTime } from '@/lib/format';
import { PRE_PUBLICATION, DRAFT_BANNER } from '@/lib/publicationStatus';

const paperSchema = z.object({
  title: z.string().min(1, "Title required"),
  abstract: z.string().optional(),
});

export default function Papers() {
  const { data: papers, isLoading } = useListPapers();
  const generateMutation = useGeneratePaper();
  const queryClient = useQueryClient();
  const { toast } = useToast();
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  const form = useForm<z.infer<typeof paperSchema>>({
    resolver: zodResolver(paperSchema),
    defaultValues: { title: '', abstract: '' },
  });

  const onSubmit = (values: z.infer<typeof paperSchema>) => {
    generateMutation.mutate({ data: values }, {
      onSuccess: () => {
        toast({ title: "Paper generation started" });
        setIsDialogOpen(false);
        form.reset();
        queryClient.invalidateQueries({ queryKey: getListPapersQueryKey() });
      },
      onError: () => toast({ title: "Failed to generate paper", variant: "destructive" })
    });
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      {PRE_PUBLICATION && (
        <div className="border border-amber-500/50 bg-amber-500/10 text-amber-700 dark:text-amber-400 rounded px-4 py-2 font-mono text-xs uppercase tracking-widest text-center" data-testid="banner-draft-status">
          {DRAFT_BANNER}
        </div>
      )}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <h1 className="text-3xl font-serif font-bold tracking-tight">Research Papers</h1>
          <p className="text-muted-foreground mt-1">Automatically compiled publications from lab evidence.</p>
        </div>
        
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button className="gap-2 bg-primary">
              <Plus className="w-4 h-4" /> Generate Paper
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Generate New Publication</DialogTitle>
            </DialogHeader>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 pt-4">
                <FormField control={form.control} name="title" render={({ field }) => (
                  <FormItem>
                    <FormLabel>Paper Title</FormLabel>
                    <FormControl><Input placeholder="e.g. Empirical Limits of Cooperation" {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )} />
                <FormField control={form.control} name="abstract" render={({ field }) => (
                  <FormItem>
                    <FormLabel>Abstract Overview (Optional)</FormLabel>
                    <FormControl><Textarea placeholder="Focus the generation on..." {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )} />
                <div className="flex justify-end pt-4">
                  <Button type="submit" disabled={generateMutation.isPending}>
                    {generateMutation.isPending ? "Generating..." : "Generate"}
                  </Button>
                </div>
              </form>
            </Form>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-muted-foreground" />
            <CardTitle>Publications</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-4">
              {[1, 2, 3].map(i => <Skeleton key={i} className="h-16 w-full" />)}
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead>
                  <tr className="border-b text-muted-foreground font-mono">
                    <th className="pb-3 font-medium">Title</th>
                    <th className="pb-3 font-medium">Status</th>
                    <th className="pb-3 font-medium text-right">Words</th>
                    <th className="pb-3 font-medium text-right">Date</th>
                  </tr>
                </thead>
                <tbody>
                  {papers?.map(paper => (
                    <tr key={paper.id} className="border-b last:border-0 hover:bg-muted/50 transition-colors">
                      <td className="py-4 font-serif font-medium text-base">
                        <Link href={`/papers/${paper.id}`} className="hover:text-primary transition-colors">
                          {paper.title}
                        </Link>
                      </td>
                      <td className="py-4">
                        <Badge variant={paper.status === 'complete' ? 'default' : 'outline'} className="uppercase text-[10px]">
                          {paper.status}
                        </Badge>
                      </td>
                      <td className="py-4 text-right font-mono text-muted-foreground">
                        {paper.wordCount ? paper.wordCount.toLocaleString() : '—'}
                      </td>
                      <td className="py-4 text-right font-mono text-muted-foreground">
                        {formatDateTime(paper.createdAt)}
                      </td>
                    </tr>
                  ))}
                  {papers?.length === 0 && (
                    <tr>
                      <td colSpan={4} className="py-8 text-center text-muted-foreground">
                        No papers published yet.
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
