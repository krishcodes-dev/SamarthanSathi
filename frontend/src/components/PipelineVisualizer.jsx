import { useEffect, useState } from 'react';
import {
    MessageSquare,
    Zap,
    BrainCircuit,
    MapPin,
    Ambulance,
    CheckCircle,
    ArrowRight,
    ScanLine,
    Database,
    Radio
} from 'lucide-react';

export default function PipelineVisualizer() {
    const [activeStep, setActiveStep] = useState(0);

    // Loop through the 4 steps
    useEffect(() => {
        const interval = setInterval(() => {
            setActiveStep((prev) => (prev + 1) % 5); // 5 steps including reset pause
        }, 2000);
        return () => clearInterval(interval);
    }, []);

    const steps = [
        {
            id: 1,
            title: "Incoming Request",
            icon: MessageSquare,
            description: "Raw unstructured text from WhatsApp/SMS",
            color: "blue",
            visual: (isActive) => (
                <div className={`relative flex items-center justify-center w-16 h-16 rounded-2xl bg-white border-2 transition-all duration-500 ${isActive ? 'border-blue-500 shadow-xl scale-110' : 'border-gray-100 grayscale opacity-50'}`}>
                    <MessageSquare size={32} className={isActive ? 'text-blue-600' : 'text-gray-400'} />
                    {isActive && (
                        <div className="absolute -top-2 -right-2 bg-red-500 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full animate-bounce">
                            SOS
                        </div>
                    )}
                </div>
            )
        },
        {
            id: 2,
            title: "AI Analysis",
            icon: BrainCircuit,
            description: "NER extraction & Urgency classification",
            color: "purple",
            visual: (isActive) => (
                <div className={`relative flex items-center justify-center w-16 h-16 rounded-2xl bg-white border-2 transition-all duration-500 ${isActive ? 'border-purple-500 shadow-xl scale-110' : 'border-gray-100 grayscale opacity-50'}`}>
                    <BrainCircuit size={32} className={isActive ? 'text-purple-600' : 'text-gray-400'} />
                    {isActive && (
                        <>
                            <ScanLine size={48} className="absolute text-purple-400 animate-ping opacity-20" />
                            <div className="absolute top-0 w-full h-1 bg-purple-500/20 animate-scan"></div>
                        </>
                    )}
                </div>
            )
        },
        {
            id: 3,
            title: "Geospatial Match",
            icon: MapPin,
            description: "Nearest resource query (PostGIS/Haversine)",
            color: "orange",
            visual: (isActive) => (
                <div className={`relative flex items-center justify-center w-16 h-16 rounded-2xl bg-white border-2 transition-all duration-500 ${isActive ? 'border-orange-500 shadow-xl scale-110' : 'border-gray-100 grayscale opacity-50'}`}>
                    <Database size={32} className={isActive ? 'text-orange-600' : 'text-gray-400'} />
                    {isActive && (
                        <div className="absolute inset-0 border-2 border-orange-400 rounded-full animate-[ping_1.5s_ease-in-out_infinite]"></div>
                    )}
                </div>
            )
        },
        {
            id: 4,
            title: "Instant Dispatch",
            icon: Ambulance,
            description: "Resource allocated & notified",
            color: "green",
            visual: (isActive) => (
                <div className={`relative flex items-center justify-center w-16 h-16 rounded-2xl bg-white border-2 transition-all duration-500 ${isActive ? 'border-green-500 shadow-xl scale-110' : 'border-gray-100 grayscale opacity-50'}`}>
                    <CheckCircle size={32} className={isActive ? 'text-green-600' : 'text-gray-400'} />
                    {isActive && (
                        <div className="absolute -bottom-2 px-2 py-0.5 bg-green-100 text-green-700 text-[10px] font-bold rounded-full animate-fade-in-up">
                            SENT
                        </div>
                    )}
                </div>
            )
        }
    ];

    return (
        <div className="py-12 bg-gray-50/50 rounded-3xl border border-gray-100 overflow-hidden relative">
            {/* Background Grid Accent */}
            <div className="absolute inset-0 grid grid-cols-[repeat(20,minmax(0,1fr))] opacity-[0.02] pointer-events-none">
                {[...Array(400)].map((_, i) => <div key={i} className="border border-gray-900/10"></div>)}
            </div>

            <div className="max-w-5xl mx-auto px-6 relative z-10">
                {/* Desktop Horizontal Layout */}
                <div className="hidden md:flex items-center justify-between relative">
                    {/* Connecting Line */}
                    <div className="absolute top-8 left-0 w-full h-1 bg-gray-200 -z-10 rounded-full overflow-hidden">
                        <div
                            className="h-full bg-gradient-to-r from-blue-500 via-purple-500 to-green-500 transition-all duration-500 ease-linear"
                            style={{
                                width: `${Math.min((activeStep / 3) * 100, 100)}%`,
                                opacity: activeStep === 4 ? 0 : 1
                            }}
                        />
                    </div>

                    {steps.map((step, idx) => {
                        const isActive = idx === activeStep; // current step active
                        const isPast = idx < activeStep;     // past steps remain highlighted? Optional visual choice.
                        const isFuture = idx > activeStep;

                        // We highlight the current step specifically
                        const isHighlighted = idx <= activeStep && activeStep !== 4;

                        return (
                            <div key={step.id} className="flex flex-col items-center text-center w-64 group">
                                {step.visual(isActive || (isPast && activeStep !== 4))}

                                <div className={`mt-6 transition-all duration-300 ${isActive ? 'opacity-100 translate-y-0' : 'opacity-60 translate-y-2'}`}>
                                    <h4 className={`text-lg font-bold ${isActive ? 'text-gray-900' : 'text-gray-400'}`}>
                                        {step.title}
                                    </h4>
                                    <p className="text-sm text-gray-500 mt-1 max-w-[180px]">
                                        {step.description}
                                    </p>
                                </div>
                            </div>
                        );
                    })}
                </div>

                {/* Mobile Vertical Layout */}
                <div className="md:hidden space-y-8 relative">
                    <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gray-200 -z-10">
                        <div
                            className="w-full bg-gradient-to-b from-blue-500 to-green-500 transition-all duration-500"
                            style={{
                                height: `${Math.min((activeStep / 3) * 100, 100)}%`,
                                opacity: activeStep === 4 ? 0 : 1
                            }}
                        />
                    </div>

                    {steps.map((step, idx) => (
                        <div key={step.id} className="flex items-center gap-6">
                            {step.visual(idx <= activeStep && activeStep !== 4)}
                            <div className={`transition-all duration-300 ${idx === activeStep ? 'opacity-100' : 'opacity-60'}`}>
                                <h4 className="text-lg font-bold text-gray-900">{step.title}</h4>
                                <p className="text-sm text-gray-500">{step.description}</p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Play/Reset Indicator for UX clarity */}
            <div className="absolute top-4 right-6 text-xs font-mono text-gray-400 flex items-center gap-2">
                {activeStep === 4 ? (
                    <span className="flex items-center gap-1 animate-pulse"><Radio size={12} /> REPEATING</span>
                ) : (
                    <span className="flex items-center gap-1"><ArrowRight size={12} /> LIVE DEMO</span>
                )}
            </div>
        </div>
    );
}
