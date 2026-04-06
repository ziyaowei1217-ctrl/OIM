import { useState } from 'react';
import { LayoutList, FileText, Cpu, CheckSquare, Check } from 'lucide-react';
import Step1Outline from './components/Step1Outline';
import Step2Sources from './components/Step2Sources';
import Step3Matching from './components/Step3Matching';
import Step4Review from './components/Step4Review';

export default function App() {
  const [step, setStep] = useState(1);
  const [maxStep, setMaxStep] = useState(1);
  
  const [outline, setOutline] = useState('I. Introduction — current state of EU energy policy\nII. Literature Review — effectiveness studies\nIII. Policy Analysis — comparing member states\nIV. Conclusion — recommendations');
  const [outlineTitle, setOutlineTitle] = useState('Renewable Energy Policy in the EU');
  const [files, setFiles] = useState<File[]>([]);
  const [matchedQuotes, setMatchedQuotes] = useState<any[]>([]);

  const handleNext = (nextStep: number) => {
    setStep(nextStep);
    setMaxStep(Math.max(maxStep, nextStep));
  };

  const navItems = [
    { id: 1, label: 'Outline Upload', icon: LayoutList },
    { id: 2, label: 'Source Upload', icon: FileText },
    { id: 3, label: 'Quote Matching', icon: Cpu },
    { id: 4, label: 'Review & Export', icon: CheckSquare },
  ];

  return (
    <div className="min-h-screen bg-white flex font-sans text-gray-900">
      {/* Sidebar */}
      <div className="w-64 bg-[#F9FAFB] border-r border-gray-200 flex flex-col shrink-0">
        <div className="h-16 flex items-center px-6 border-b border-gray-200 bg-white">
          <h1 className="text-xl font-bold tracking-tight">SourceMatch</h1>
        </div>
        
        <div className="p-4">
          <div className="text-xs font-bold text-gray-400 tracking-widest uppercase mb-4 px-2">Workflow</div>
          <nav className="space-y-1">
            {navItems.map((item) => {
              const isActive = step === item.id;
              const isAccessible = item.id <= maxStep;
              const Icon = item.icon;
              
              return (
                <button
                  key={item.id}
                  onClick={() => isAccessible && setStep(item.id)}
                  disabled={!isAccessible}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                    isActive 
                      ? 'bg-blue-50 text-blue-700' 
                      : isAccessible 
                        ? 'text-gray-600 hover:bg-gray-100 hover:text-gray-900' 
                        : 'text-gray-400 opacity-50 cursor-not-allowed'
                  }`}
                >
                  <Icon size={18} className={isActive ? 'text-blue-600' : isAccessible ? 'text-gray-500' : 'text-gray-300'} />
                  {item.label}
                  {item.id < maxStep && !isActive && (
                    <Check size={14} className="ml-auto text-green-500" />
                  )}
                </button>
              );
            })}
          </nav>
        </div>
        
        <div className="mt-auto p-4 border-t border-gray-200">
           <div className="flex items-center gap-3 px-2">
             <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center text-xs font-bold text-gray-600">A</div>
             <div className="text-sm font-medium text-gray-700">Alex Researcher</div>
           </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col h-screen overflow-hidden bg-white">
        {/* Top Header */}
        <div className="h-16 flex items-center justify-between px-8 border-b border-gray-100 shrink-0">
          <h2 className="text-lg font-medium text-gray-800">
            {navItems.find(i => i.id === step)?.label}
          </h2>
          {step === 4 && matchedQuotes.length > 0 && (
            <span className="text-sm font-medium text-green-600 flex items-center gap-1 bg-green-50 px-3 py-1 rounded-full">
              <Check size={16} strokeWidth={3} /> {matchedQuotes.reduce((acc, curr) => acc + (curr.quotes?.length || 0), 0)} quotes verified
            </span>
          )}
        </div>

        {/* Content Area */}
        <div className="flex-1 overflow-y-auto p-8">
          <div className="max-w-4xl mx-auto h-full">
            {step === 1 && <Step1Outline outline={outline} setOutline={setOutline} outlineTitle={outlineTitle} setOutlineTitle={setOutlineTitle} onNext={() => handleNext(2)} />}
            {step === 2 && <Step2Sources files={files} setFiles={setFiles} outlineTitle={outlineTitle} onNext={() => handleNext(3)} />}
            {step === 3 && <Step3Matching outline={outline} files={files} setMatchedQuotes={setMatchedQuotes} onNext={() => handleNext(4)} />}
            {step === 4 && <Step4Review matchedQuotes={matchedQuotes} />}
          </div>
        </div>
      </div>
    </div>
  );
}
