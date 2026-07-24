import { useParams } from 'wouter';
import { useGetPaper, getGetPaperQueryKey } from '@workspace/api-client-react';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { formatDateTime } from '@/lib/format';
import { FileText } from 'lucide-react';

export default function PaperDetail() {
  const { id } = useParams();
  const paperId = parseInt(id || '0', 10);

  const { data: paper, isLoading } = useGetPaper(paperId, {
    query: { enabled: !!paperId, queryKey: getGetPaperQueryKey(paperId) }
  });

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto space-y-8 mt-12">
        <Skeleton className="h-12 w-3/4" />
        <Skeleton className="h-6 w-1/4" />
        <Skeleton className="h-48 w-full" />
      </div>
    );
  }

  if (!paper) return <div className="text-center mt-12 text-muted-foreground">Paper not found</div>;

  let sections: { heading: string; content: string }[] = [];
  try {
    if (paper.sections) sections = JSON.parse(paper.sections);
  } catch (e) {}

  let claims: number[] = [];
  try {
    if (paper.claimsJson) claims = JSON.parse(paper.claimsJson);
  } catch (e) {}

  let experiments: number[] = [];
  try {
    if (paper.experimentsJson) experiments = JSON.parse(paper.experimentsJson);
  } catch (e) {}

  return (
    <article className="max-w-4xl mx-auto py-12 px-4 md:px-8 bg-card shadow-sm border mt-8 mb-24 rounded-lg animate-in fade-in duration-700">
      <header className="mb-16 text-center">
        <div className="flex justify-center mb-6">
          <Badge variant={paper.status === 'complete' ? 'outline' : 'secondary'} className="uppercase tracking-widest text-[10px]">
            {paper.status}
          </Badge>
        </div>
        <h1 className="text-4xl md:text-5xl font-serif font-bold tracking-tight text-foreground leading-tight mb-6">
          {paper.title}
        </h1>
        <div className="flex items-center justify-center gap-4 text-sm font-mono text-muted-foreground">
          <span>Game Theory Research Lab</span>
          <span>•</span>
          <span>{formatDateTime(paper.createdAt)}</span>
          {paper.wordCount && (
            <>
              <span>•</span>
              <span>{paper.wordCount.toLocaleString()} words</span>
            </>
          )}
        </div>
      </header>

      {paper.abstract && (
        <section className="mb-12">
          <h2 className="text-sm font-mono uppercase tracking-widest text-muted-foreground mb-4 text-center">Abstract</h2>
          <p className="text-lg leading-relaxed text-foreground font-serif italic text-justify px-8">
            {paper.abstract}
          </p>
        </section>
      )}

      <div className="w-full h-px bg-border my-12" />

      <div className="prose prose-stone prose-lg max-w-none dark:prose-invert prose-headings:font-serif prose-h2:text-2xl prose-h2:font-bold prose-h2:border-b prose-h2:pb-2">
        {sections.map((section, idx) => (
          <section key={idx} className="mb-10">
            <h2 className="mt-0">{section.heading}</h2>
            <div className="whitespace-pre-wrap text-foreground/90 font-sans leading-relaxed">
              {section.content}
            </div>
          </section>
        ))}

        {sections.length === 0 && paper.status === 'complete' && (
          <p className="text-muted-foreground text-center italic">Document body empty.</p>
        )}
        
        {paper.status !== 'complete' && (
          <div className="flex flex-col items-center justify-center py-16 text-muted-foreground space-y-4">
            <FileText className="w-8 h-8 animate-pulse" />
            <p className="font-mono text-sm uppercase tracking-widest">Generation in progress...</p>
          </div>
        )}
      </div>

      {(claims.length > 0 || experiments.length > 0) && (
        <footer className="mt-16 pt-8 border-t">
          <h3 className="text-sm font-mono uppercase tracking-widest text-muted-foreground mb-4">Methodology & Evidence</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm font-mono">
            {claims.length > 0 && (
              <div className="p-4 bg-muted/30 rounded border">
                <strong className="block text-foreground mb-2">Supporting Claims</strong>
                <ul className="list-disc list-inside text-muted-foreground pl-2 space-y-1">
                  {claims.map(cId => <li key={cId}>Claim #{cId}</li>)}
                </ul>
              </div>
            )}
            {experiments.length > 0 && (
              <div className="p-4 bg-muted/30 rounded border">
                <strong className="block text-foreground mb-2">Empirical Baselines</strong>
                <ul className="list-disc list-inside text-muted-foreground pl-2 space-y-1">
                  {experiments.map(eId => <li key={eId}>EXP-{eId.toString().padStart(4, '0')}</li>)}
                </ul>
              </div>
            )}
          </div>
        </footer>
      )}
    </article>
  );
}
