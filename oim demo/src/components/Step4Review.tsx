import { useState, useEffect } from 'react';
import { Check, Circle, Copy } from 'lucide-react';

const toTitleCase = (str: string) => {
  if (!str) return '';
  if (str.startsWith('[')) return str;
  let lowerStr = str.toLowerCase();
  return lowerStr.replace(/(?:^|\s|-)\S/g, (c) => c.toUpperCase());
};

const toMLATitleCase = (str: string) => {
  if (!str) return '';
  if (str.startsWith('[')) return str;
  const lowers = ['a', 'an', 'the', 'and', 'but', 'or', 'for', 'nor', 'on', 'at', 'to', 'from', 'by', 'of', 'in', 'with'];
  return str.split(/(\s+|-)/).map((word, index, arr) => {
    if (word.match(/^\s+|-$/)) return word; // separators
    const lowerWord = word.toLowerCase();
    if (index === 0 || index === arr.length - 1 || !lowers.includes(lowerWord)) {
      return lowerWord.charAt(0).toUpperCase() + lowerWord.slice(1);
    }
    return lowerWord;
  }).join('');
};

const toSentenceCase = (str: string) => {
  if (!str) return '';
  if (str.startsWith('[')) return str;
  let lowerStr = str.toLowerCase();
  return lowerStr.charAt(0).toUpperCase() + lowerStr.slice(1);
};

const parseAuthors = (authorStr: string) => {
  if (!authorStr || authorStr === 'Unknown' || authorStr === 'Unknown Author' || authorStr.includes('[Author Name]')) {
    return [{ first: '[Firstname]', last: '[Surname]' }];
  }
  const parts = authorStr.split(/\s+and\s+|\s*&\s*|;/i).flatMap(p => p.split(',')).map(p => p.trim()).filter(p => p);
  
  if (authorStr.includes(',') && !authorStr.toLowerCase().includes('and') && !authorStr.includes('&') && authorStr.split(',').length === 2) {
    const p = authorStr.split(',');
    return [{ last: toTitleCase(p[0].trim()), first: toTitleCase(p[1].trim()) }];
  }

  const authors = parts.map(part => {
    const names = part.split(/\s+/);
    if (names.length === 1) return { first: '', last: toTitleCase(names[0]) };
    const last = names.pop() || '';
    const first = names.join(' ');
    return { first: toTitleCase(first), last: toTitleCase(last) };
  });

  return authors.length > 0 ? authors : [{ first: '[Firstname]', last: '[Surname]' }];
};

const getInTextCitation = (format: string, authors: ReturnType<typeof parseAuthors>, year: string | number, pages: string) => {
  let authorPart = '';
  if (authors.length === 1) {
    authorPart = authors[0].last;
  } else if (authors.length === 2) {
    if (format === 'APA') authorPart = `${authors[0].last} & ${authors[1].last}`;
    else authorPart = `${authors[0].last} and ${authors[1].last}`;
  } else {
    authorPart = `${authors[0].last} et al.`;
  }

  let pageRaw = String(pages).trim();
  if (pageRaw === 'n.p.' || pageRaw === 'N/A') pageRaw = '';
  
  const hasMultiplePages = pageRaw.includes('-') || pageRaw.includes(',') || pageRaw.includes('–');
  const pageText = pageRaw.replace(/\s*-\s*/g, '–');

  let pagePart = '';
  if (pageText) {
    if (format === 'APA') {
      pagePart = hasMultiplePages ? `pp. ${pageText}` : `p. ${pageText}`;
    } else {
      pagePart = pageText;
    }
  }

  if (format === 'APA') {
    if (pagePart) return `(${authorPart}, ${year}, ${pagePart})`;
    return `(${authorPart}, ${year})`;
  } else if (format === 'MLA') {
    if (pagePart) return `(${authorPart} ${pagePart})`;
    return `(${authorPart})`;
  } else { // Chicago
    if (pagePart) return `(${authorPart} ${year}, ${pagePart})`;
    return `(${authorPart} ${year})`;
  }
};

const getReferenceEntry = (format: string, authors: ReturnType<typeof parseAuthors>, year: string | number, source: string, publisher: string) => {
  let refAuthor = '';
  if (format === 'APA') {
    const formatted = authors.map(a => {
      const init = a.first ? (a.first.startsWith('[') ? a.first : `${a.first.charAt(0)}.`) : '';
      return `${a.last}, ${init}`.replace(/,\s*$/, '').trim();
    });
    if (formatted.length === 1) refAuthor = formatted[0];
    else if (formatted.length === 2) refAuthor = `${formatted[0]} & ${formatted[1]}`;
    else refAuthor = formatted.slice(0, -1).join(', ') + ', & ' + formatted[formatted.length - 1];
  } else {
    if (authors.length === 1) {
      refAuthor = `${authors[0].last}, ${authors[0].first}`.replace(/,\s*$/, '');
    } else if (authors.length === 2) {
      refAuthor = `${authors[0].last}, ${authors[0].first}, and ${authors[1].first} ${authors[1].last}`;
    } else {
      refAuthor = `${authors[0].last}, ${authors[0].first}, et al.`;
    }
  }

  const titleCaseSource = toMLATitleCase(source);
  const sentenceCaseSource = toSentenceCase(source);

  if (format === 'APA') {
    return `${refAuthor} (${year}). *${sentenceCaseSource}*. ${publisher}.`.replace(/\.\./g, '.');
  } else if (format === 'MLA') {
    return `${refAuthor}. *${titleCaseSource}*. ${publisher}, ${year}.`.replace(/\.\./g, '.');
  } else { // Chicago
    return `${refAuthor}. ${year}. *${titleCaseSource}*. [Place of publication]: ${publisher}.`.replace(/\.\.\*/g, '.*').replace(/\.\./g, '.');
  }
};

export default function Step4Review({ matchedQuotes }: { matchedQuotes: any[] }) {
  const [activeSection, setActiveSection] = useState<string>('');
  const [format, setFormat] = useState('APA');
  const [copiedQuoteIdx, setCopiedQuoteIdx] = useState<number | null>(null);
  const [copiedAll, setCopiedAll] = useState(false);

  useEffect(() => {
    if (matchedQuotes && matchedQuotes.length > 0) {
      setActiveSection(matchedQuotes[0].id);
    }
  }, [matchedQuotes]);

  const formats = ['APA', 'MLA', 'Chicago'];

  const currentSection = matchedQuotes.find(s => s.id === activeSection);
  const quotes = currentSection?.quotes || [];

  const handleCopyQuote = (quote: any, idx: number) => {
    const authorStr = quote.author && quote.author !== 'Unknown' && quote.author !== 'Unknown Author' ? quote.author : '[Author Name]';
    const year = quote.year && quote.year !== 'Unknown' ? quote.year : new Date().getFullYear();
    const page = quote.page || 'n.p.';
    
    const parsedAuthors = parseAuthors(authorStr);
    const citationTag = getInTextCitation(format, parsedAuthors, year, page);
    let cleanText = quote.text.trim().replace(/[.,]$/, '');
    const citation = `"${cleanText}" ${citationTag}.`;

    navigator.clipboard.writeText(citation);
    setCopiedQuoteIdx(idx);
    setTimeout(() => setCopiedQuoteIdx(null), 2000);
  };

  const handleExportAll = () => {
    let allText = '';
    const author = '[Author Name]';
    const year = new Date().getFullYear();
    const references = new Set<string>();

    allText += `${format} FORMAT EXPORT\n\n`;
    allText += '====================\n';
    allText += 'IN-TEXT CITATIONS\n';
    allText += '====================\n\n';

    matchedQuotes.forEach(section => {
      allText += `${section.label}\n\n`;
      section.quotes?.forEach((quote: any) => {
        const source = quote.source || 'Unknown Source';
        const page = quote.page || 'n.p.';
        const authorStr = quote.author && quote.author !== 'Unknown' && quote.author !== 'Unknown Author' ? quote.author : '[Author Name]';
        const year = quote.year && quote.year !== 'Unknown' ? quote.year : new Date().getFullYear();
        const publisher = quote.publisher && quote.publisher !== 'Unknown' ? quote.publisher : '[Publisher]';
        
        const parsedAuthors = parseAuthors(authorStr);
        const citationTag = getInTextCitation(format, parsedAuthors, year, page);
        let cleanText = quote.text.trim().replace(/[.,]$/, '');
        const citation = `"${cleanText}" ${citationTag}.`;
        const refStr = getReferenceEntry(format, parsedAuthors, year, source, publisher);
        
        references.add(refStr);
        allText += `${citation}\n\n`;
      });
      allText += '---\n\n';
    });

    allText += '====================\n';
    allText += format === 'MLA' ? 'WORKS CITED\n' : (format === 'APA' ? 'REFERENCES\n' : 'BIBLIOGRAPHY\n');
    allText += '====================\n\n';
    
    Array.from(references).sort().forEach(ref => {
      allText += `${ref}\n\n`;
    });

    navigator.clipboard.writeText(allText);
    setCopiedAll(true);
    setTimeout(() => setCopiedAll(false), 2000);
  };

  return (
    <div className="animate-in fade-in duration-500 h-full flex flex-col">
      <div className="flex gap-12 flex-1 min-h-0">
        {/* Left Sidebar */}
        <div className="w-1/3 border-r border-gray-100 pr-8 overflow-y-auto">
          <div className="mb-4 text-[10px] font-bold text-gray-400 tracking-widest uppercase">Outline</div>
          <div className="space-y-1">
            {matchedQuotes.map(s => (
              <div 
                key={s.id}
                onClick={() => setActiveSection(s.id)}
                className={`px-4 py-2.5 rounded-lg text-sm transition-colors cursor-pointer ${
                  activeSection === s.id 
                    ? 'bg-gray-900 text-white font-medium' 
                    : 'text-gray-500 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                {s.label}
              </div>
            ))}
            {matchedQuotes.length === 0 && (
              <div className="text-sm text-gray-400">No sections found.</div>
            )}
          </div>
        </div>

        {/* Right Content */}
        <div className="flex-1 flex flex-col min-h-0">
          <div className="mb-4 text-[10px] font-bold text-gray-400 tracking-widest uppercase">
            {currentSection?.label.replace(/^[IVX]+\.\\s/, '') || 'Quotes'}
          </div>
          
          <div className="space-y-4 mb-8 flex-1 overflow-y-auto pr-4">
            {quotes.map((quote: any, i: number) => (
              <div key={i} className="bg-green-50/50 hover:bg-green-100/50 transition-colors border border-green-100 rounded-xl p-6 relative group">
                <div className="absolute top-6 right-6 flex gap-2">
                  <button 
                    onClick={() => handleCopyQuote(quote, i)}
                    className={`w-8 h-8 rounded-full bg-white border flex items-center justify-center transition-all shadow-sm ${
                      copiedQuoteIdx === i 
                        ? 'border-green-500 text-green-500' 
                        : 'border-green-200 text-green-600 hover:bg-green-50 opacity-0 group-hover:opacity-100'
                    }`}
                    title="Copy citation"
                  >
                    {copiedQuoteIdx === i ? <Check size={14} strokeWidth={3} /> : <Copy size={14} />}
                  </button>
                  <div className="w-8 h-8 rounded-full bg-green-500 flex items-center justify-center text-white shadow-sm">
                    <Check size={16} strokeWidth={3} />
                  </div>
                </div>
                <p className="text-gray-800 text-sm italic mb-4 pr-16 leading-relaxed">
                  "{quote.text}"
                </p>
                <p className="text-xs text-gray-500">{quote.source} · p. {quote.page}</p>
              </div>
            ))}
            {quotes.length === 0 && (
              <div className="text-sm text-gray-400">No quotes matched for this section.</div>
            )}
          </div>

          {/* Footer Actions */}
          <div className="flex items-center justify-between pt-6 border-t border-gray-100 mt-auto shrink-0">
            <div className="flex gap-1 bg-gray-100 p-1 rounded-lg">
              {formats.map(f => (
                <button 
                  key={f}
                  onClick={() => setFormat(f)}
                  className={`px-4 py-1.5 text-xs font-medium rounded-md transition-all ${
                    format === f 
                      ? 'bg-white shadow-sm text-gray-900' 
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  {f}
                </button>
              ))}
            </div>
            <button 
              onClick={handleExportAll}
              className="px-6 py-2.5 rounded-full bg-gray-900 text-white text-sm font-medium hover:bg-black transition-colors flex items-center gap-2"
            >
              {copiedAll ? <Check size={16} /> : <Copy size={16} />}
              {copiedAll ? 'Copied to Clipboard!' : `Export ${format} Citations`}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
