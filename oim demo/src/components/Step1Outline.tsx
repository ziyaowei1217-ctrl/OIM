import { useState } from 'react';
import { Upload, Sparkles, Loader2 } from 'lucide-react';

export default function Step1Outline({ 
  outline, setOutline, outlineTitle, setOutlineTitle, onNext 
}: { 
  outline: string; setOutline: (v: string) => void;
  outlineTitle: string; setOutlineTitle: (v: string) => void;
  onNext: () => void 
}) {
  const [description, setDescription] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (!description.trim()) return;
    
    setIsGenerating(true);
    setError(null);
    
    try {
      const res = await fetch('/api/generate-outline', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description })
      });
      
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.error || 'Failed to generate outline.');
      }
      
      const data = await res.json();
      if (data.title) setOutlineTitle(data.title);
      if (data.outline) setOutline(data.outline);
      setDescription(''); // Optional: clear description after gen
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="animate-in fade-in duration-500 h-full flex flex-col">
      <div className="mb-3 text-[10px] font-bold text-gray-400 tracking-widest uppercase">Paper Outline</div>
      
      {/* AI Generate Section */}
      <div className="mb-4 p-4 bg-blue-50/50 border border-blue-100 rounded-xl">
        <label className="block text-xs font-semibold text-blue-800 mb-2">Draft with AI ✨</label>
        <div className="flex gap-3">
          <input 
            type="text" 
            className="flex-1 bg-white border border-blue-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-400 transition-all placeholder:text-gray-400"
            placeholder="E.g. A paper on renewable energy policy in Europe focusing on Germany vs France..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            disabled={isGenerating}
          />
          <button 
            onClick={handleGenerate}
            disabled={isGenerating || !description.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors flex items-center gap-2 disabled:opacity-50"
          >
            {isGenerating ? <Loader2 size={16} className="animate-spin" /> : <Sparkles size={16} />}
            Generate
          </button>
        </div>
        {error && <p className="text-red-500 text-xs mt-2">{error}</p>}
      </div>

      {/* Outline Edit Section */}
      <div className="flex-1 bg-gray-50 rounded-xl p-6 mb-6 border border-gray-200 focus-within:border-gray-400 transition-all flex flex-col min-h-[300px]">
        <input 
          type="text" 
          className="w-full bg-transparent font-semibold text-gray-900 mb-4 outline-none placeholder:text-gray-400" 
          placeholder="Paper Title (e.g. Renewable Energy Policy in the EU)"
          value={outlineTitle}
          onChange={(e) => setOutlineTitle(e.target.value)}
          disabled={isGenerating}
        />
        <textarea 
          className="w-full flex-1 bg-transparent text-sm text-gray-600 outline-none resize-none placeholder:text-gray-400 leading-relaxed"
          placeholder="Type or paste your outline here..."
          value={outline}
          onChange={(e) => setOutline(e.target.value)}
          disabled={isGenerating}
        />
      </div>

      <div className="flex justify-between items-center mb-12">
        <button className="flex items-center gap-2 px-5 py-2.5 rounded-full border border-gray-200 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors">
          <Upload size={16} />
          Upload Outline File
        </button>
        <button 
          onClick={onNext}
          className="px-6 py-2.5 rounded-full bg-gray-900 text-white text-sm font-medium hover:bg-black transition-colors"
        >
          Continue to Sources
        </button>
      </div>

      <div className="opacity-40 pointer-events-none">
        <div className="mb-2 text-[10px] font-bold text-gray-400 tracking-widest uppercase">Upload Research Sources</div>
        <p className="text-sm text-gray-400">Complete outline to continue</p>
      </div>
    </div>
  );
}
