import { useState, useEffect } from 'react';
import { Check, Circle } from 'lucide-react';

export default function Step4Review({ matchedQuotes }: { matchedQuotes: any[] }) {
  const [activeSection, setActiveSection] = useState<string>('');
  const [format, setFormat] = useState('APA');

  useEffect(() => {
    if (matchedQuotes && matchedQuotes.length > 0) {
      setActiveSection(matchedQuotes[0].id);
    }
  }, [matchedQuotes]);

  const formats = ['APA', 'MLA', 'Chicago'];

  const currentSection = matchedQuotes.find(s => s.id === activeSection);
  const quotes = currentSection?.quotes || [];

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
              <div key={i} className="bg-green-50/50 border border-green-100 rounded-xl p-6 relative">
                <div className="absolute top-6 right-6 text-green-500">
                  <div className="w-5 h-5 rounded-full bg-green-500 flex items-center justify-center text-white">
                    <Check size={12} strokeWidth={3} />
                  </div>
                </div>
                <p className="text-gray-800 text-sm italic mb-4 pr-8 leading-relaxed">
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
            <button className="px-6 py-2.5 rounded-full bg-gray-900 text-white text-sm font-medium hover:bg-black transition-colors">
              Export {format} Citations
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
