import { useEffect, useState } from 'react';
import { Check } from 'lucide-react';

export default function Step3Matching({ 
  outline, files, setMatchedQuotes, onNext 
}: { 
  outline: string; files: File[]; setMatchedQuotes: (quotes: any[]) => void; onNext: () => void 
}) {
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState(0);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Artificial progress update while waiting
    const timer = setInterval(() => {
      setProgress(p => {
        if (p >= 95) return 95; // Wait at 95% until fetch completes
        const newP = p + Math.random() * 5; 
        if (newP > 25) setCurrentStep(1);
        if (newP > 50) setCurrentStep(2);
        if (newP > 75) setCurrentStep(3);
        return newP;
      });
    }, 500);

    const matchQuotes = async () => {
      try {
        const formData = new FormData();
        formData.append('outline', outline);
        files.forEach(file => {
          formData.append('files', file);
        });

        const res = await fetch('/api/match', {
          method: 'POST',
          body: formData,
        });

        if (!res.ok) {
          const errData = await res.json().catch(() => ({}));
          throw new Error(errData.error || 'Failed to match quotes.');
        }

        const data = await res.json();
        setMatchedQuotes(data);
        
        // Complete progress
        clearInterval(timer);
        setProgress(100);
        setCurrentStep(4);
        setTimeout(onNext, 1000);
        
      } catch (err: any) {
        clearInterval(timer);
        setError(err.message);
      }
    };

    matchQuotes();

    return () => clearInterval(timer);
  }, [files, outline, onNext, setMatchedQuotes]);

  const steps = [
    "Analyzing outline for evidence needs",
    "Semantic search across parsed passages",
    "Ranking best-fitting quotes per section",
    "Verification — exact-match against original source text"
  ];

  return (
    <div className="animate-in fade-in duration-500 py-12">
      <div className="text-center mb-6 text-sm text-gray-600">Matching quotes to outline sections...</div>
      
      <div className="h-1 w-full max-w-lg mx-auto bg-gray-100 rounded-full mb-3 overflow-hidden">
        <div 
          className="h-full bg-blue-500 transition-all duration-75 ease-linear"
          style={{ width: `${progress}%` }}
        ></div>
      </div>
      
      <div className="text-center text-xs text-gray-400 mb-16">Scanning {files.length} sources</div>

      {error ? (
        <div className="max-w-md mx-auto text-sm text-red-500 bg-red-50 p-4 rounded-xl text-center">
          {error}
        </div>
      ) : (
        <div className="max-w-md mx-auto space-y-5">
          {steps.map((step, i) => {
            const isActive = currentStep === i;
            const isPast = currentStep > i;
            return (
              <div key={i} className={`flex items-center gap-4 text-sm ${isPast ? 'text-gray-400' : isActive ? 'text-gray-900 font-medium' : 'text-gray-300'}`}>
                <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs shrink-0 ${isPast ? 'bg-gray-100 text-gray-400' : isActive ? 'bg-blue-50 text-blue-600' : 'bg-gray-50 text-gray-300'}`}>
                  {i + 1}
                </div>
                {step}
              </div>
            );
          })}
        </div>
      )}

      <div className={`max-w-md mx-auto mt-10 flex items-center gap-2 text-sm text-green-600 font-medium transition-opacity duration-500 ${progress === 100 ? 'opacity-100' : 'opacity-0'}`}>
        <Check size={16} strokeWidth={3} /> All quotes verified against source documents
      </div>
    </div>
  );
}
