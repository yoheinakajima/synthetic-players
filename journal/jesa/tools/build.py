#!/usr/bin/env python3
"""Build journal source/PDFs using existing Pandoc and cache-only Tectonic."""
from pathlib import Path
import hashlib,json,re,subprocess,shutil,zipfile
J=Path(__file__).resolve().parents[1]
header=J/'layout.tex'
header.write_text(r"""\documentclass[11pt]{article}
\usepackage[margin=1in]{geometry}
\usepackage{fontspec}
\setmainfont{Times New Roman}
\setsansfont{Arial}
\setmonofont{Menlo}
\usepackage{amsmath,amssymb,graphicx,booktabs}
\usepackage[unicode,hidelinks]{hyperref}
\usepackage{xurl}
\urlstyle{same}
\setlength{\emergencystretch}{5em}
\setlength{\parindent}{0pt}
\setlength{\parskip}{6pt plus 2pt}
\setcounter{secnumdepth}{-1}
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\newcommand{\pandocbounded}[1]{#1}
\pagestyle{plain}
\begin{document}
""")
records=[]
for name in ('manuscript','supplement','data-instructions'):
    # Core cached TeX packages suffice: render long supplementary tables as
    # labeled rows; retain the main criterion table as a three-column table.
    md=(J/(name+'.md')).read_text()
    md=re.sub(r'!\[[^\]]*\]', '![]', md)
    md=re.sub(r'`([^`\n]+)`',lambda m:(r'\nolinkurl{'+m[1]+'}') if len(m[1])>=35 else m[0],md)
    def table(m):
        lines=m[0].strip().splitlines();head=[v.strip() for v in lines[0].strip('|').split('|')]
        rows=[[v.strip() for v in line.strip('|').split('|')] for line in lines[2:]]
        if name=='manuscript':
            body='\\begin{tabular}{p{.17\\linewidth}p{.37\\linewidth}p{.35\\linewidth}}\\toprule\n'
            body+=' & '.join(head)+r' \\ \midrule'+'\n'
            body+='\n'.join(' & '.join(v.replace('%',r'\%').replace('_',r'\_') for v in row)+r' \\' for row in rows)
            return body+'\n'+r'\bottomrule\end{tabular}'+'\n'
        return '\n\n'.join('; '.join('**'+h+':** '+v for h,v in zip(head,row)) for row in rows)+'\n'
    md=re.sub(r'(?m)^\|[^\n]+\n\|[ :|\-]+\n(?:\|[^\n]+\n)+',table,md)
    # Wrap shell example verbatim at a safe line width using source line breaks.
    latex=subprocess.check_output(['pandoc','--from=markdown+autolink_bare_uris+tex_math_dollars+tex_math_single_backslash+raw_tex','--to=latex','--syntax-highlighting=none','--top-level-division=section'],input=md,text=True,cwd=J)
    latex=re.sub(r'\\includegraphics(?:\[[^\]]*\])?\{',r'\\includegraphics[width=.95\\linewidth]{',latex)
    refspace='0.5pt' if name=='manuscript' else '3pt'
    refleading=r'\setlength{\baselineskip}{11pt}' if name=='manuscript' else ''
    latex=latex.replace(r'\subsection{References}',r'\begingroup\small\setlength{\parskip}{'+refspace+'}'+refleading+r'\subsection{References}')
    if r'\begingroup' in latex:latex+=r'\endgroup'
    tex=J/(name+'.tex');tex.write_text(header.read_text()+latex+'\n'+r'\end{document}'+'\n')
    subprocess.run(['tectonic','--only-cached','--untrusted','--keep-logs',name+'.tex'],cwd=J,check=True)
    log=J/(name+'.log');log.write_text('\n'.join(line.rstrip() for line in log.read_text().splitlines()).rstrip()+'\n')
    info=subprocess.check_output(['pdfinfo',str(J/(name+'.pdf'))],text=True)
    records.append({'path':name+'.pdf','sha256':hashlib.sha256((J/(name+'.pdf')).read_bytes()).hexdigest(),'pages':int(re.search(r'Pages:\s+(\d+)',info)[1])})
text=(J/'manuscript.md').read_text();pre,refs=text.split('\n## References\n',1);abstract=pre.split('## Abstract\n\n')[1].split('\n## 1.')[0]
# Conservative bound: every whitespace token in source, including title, metadata,
# table syntax, citations, URLs, image/caption text; ADD 200 per figure.
figure_count=len(re.findall(r'^!\[',text,re.M));count={'method':'all source whitespace tokens including title/author/abstract/text/tables/captions/references/URLs, plus 200 per figure; conservative diagnostic, publisher adjudicates','abstract':len(abstract.split()),'before_references':len(pre.split()),'references':len(refs.split()),'all_source_tokens':len(text.split()),'figures':figure_count,'figure_allowance':200*figure_count,'inclusive_conservative':len(text.split())+200*figure_count,'limit':5000}
assert count['abstract']<=150,count
assert count['inclusive_conservative']<=5000,count
(J/'word-count.json').write_text(json.dumps(count,indent=2)+'\n')
(J/'build-receipt.json').write_text(json.dumps({'tools':{n:subprocess.check_output([n,'--version'],text=True).splitlines()[0] for n in ('pandoc','tectonic')},'mode':'Tectonic --only-cached --untrusted; no TeX installation; no live publication','outputs':records},indent=2)+'\n')
# Journal sources and local figures are portable; no private author responses.
with zipfile.ZipFile(J/'jesa-source.zip','w',zipfile.ZIP_DEFLATED) as z:
 for name in ('manuscript','supplement','data-instructions'):
  for ext in ('md','tex'):z.write(J/(name+'.'+ext),name+'.'+ext)
 z.write(header,'layout.tex')
 for extra in ('declarations.md','author-metadata.json','tool-use-reconstruction.md','tool-use-reconstruction.json'):
  z.write(J/extra,extra)
 for f in sorted((J/'figures').glob('*.pdf')):z.write(f,'figures/'+f.name)
print(json.dumps(count,indent=2))
