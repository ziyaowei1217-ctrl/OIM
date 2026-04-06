import { Check, ArrowRight, UploadCloud } from 'lucide-react';
import { useRef } from 'react';

export default function Step2Sources({ 
  files, setFiles, outlineTitle, onNext 
}: { 
  files: File[]; setFiles: (f: File[]) => void;
  outlineTitle: string; onNext: () => void 
}) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles([...files, ...Array.from(e.target.files)]);
    }
  };

  return (
    <div className="animate-in fade-in duration-500">
      <div className="bg-gray-50 rounded-xl p-4 mb-8 flex items-center gap-3">
        <div className="w-5 h-5 rounded-full bg-green-500 flex items-center justify-center text-white shrink-0">
          <Check size={12} strokeWidth={3} />
        </div>
        <span className="text-sm text-gray-600 font-medium">Outline — {outlineTitle}</span>
      </div>

      <div className="mb-3 text-[10px] font-bold text-gray-400 tracking-widest uppercase">Research Sources</div>
      
      <div 
        className="border border-dashed border-gray-300 rounded-xl p-10 flex flex-col items-center justify-center text-gray-400 mb-6 hover:bg-gray-50 transition-colors cursor-pointer"
        onClick={() => fileInputRef.current?.click()}
      >
        <UploadCloud size={24} className="mb-3 text-gray-300" />
        <span className="text-sm">Click to upload PDFs</span>
        <input 
          type="file" 
          multiple 
          accept=".pdf" 
          ref={fileInputRef} 
          className="hidden" 
          onChange={handleFileChange} 
        />
      </div>

      <div className="space-y-1 mb-4">
        {files.map((file, i) => (
          <div key={i} className="flex items-center justify-between py-3 border-b border-gray-50 last:border-0">
            <div className="flex items-center gap-3">
              <span className="text-[10px] font-bold text-gray-400 bg-gray-100 px-2 py-1 rounded">PDF</span>
              <span className="text-sm text-gray-700">{file.name}</span>
            </div>
            <div className="flex items-center gap-4">
               <span className="text-sm text-gray-400">{(file.size / 1024 / 1024).toFixed(2)} MB</span>
              <Check size={16} className="text-green-500" />
            </div>
          </div>
        ))}
      </div>
      
      {files.length > 0 && (
        <div className="text-xs text-gray-400 mb-10">{files.length} files selected</div>
      )}

      <button 
        onClick={onNext}
        disabled={files.length === 0}
        className="px-6 py-3 rounded-full bg-gray-900 text-white text-sm font-medium hover:bg-black transition-colors flex items-center gap-2 disabled:opacity-50"
      >
        Find My Quotes <ArrowRight size={16} />
      </button>
    </div>
  );
}
