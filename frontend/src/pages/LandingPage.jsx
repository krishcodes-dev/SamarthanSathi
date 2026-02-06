import { Link } from 'react-router-dom';
import { ArrowRight, Activity, MapPin, Radio, ShieldCheck, Zap } from 'lucide-react';
import PipelineVisualizer from '../components/PipelineVisualizer';

export default function LandingPage() {
    return (
        <div className="min-h-screen bg-white text-gray-900 font-sans selection:bg-blue-100">
            {/* Navigation */}
            <nav className="fixed w-full bg-white/80 backdrop-blur-md z-50 border-b border-gray-100">
                <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
                    <div className="font-bold text-xl tracking-tight flex items-center gap-2">
                        <div className="w-8 h-8 bg-black rounded-lg flex items-center justify-center text-white">
                            <Zap size={18} fill="white" />
                        </div>
                        SamarthanSathi
                    </div>
                    <Link
                        to="/dashboard"
                        className="px-5 py-2 bg-black text-white rounded-full text-sm font-medium hover:bg-gray-800 transition-all hover:shadow-lg hover:-translate-y-0.5"
                    >
                        Launch System
                    </Link>
                </div>
            </nav>

            {/* Hero Section */}
            <section className="pt-32 pb-20 px-6 max-w-6xl mx-auto text-center">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 text-blue-700 text-xs font-semibold uppercase tracking-wide mb-8 animate-fade-in-up">
                    <span className="relative flex h-2 w-2">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
                    </span>
                    Live Crisis Response System
                </div>

                <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-8 leading-[1.1]">
                    Unstructured chaos to <br />
                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">actionable response.</span>
                </h1>

                <p className="text-xl text-gray-500 max-w-2xl mx-auto mb-12 leading-relaxed">
                    Turning raw SOS messages into prioritized emergency response—when every second matters.
                </p>

                <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                    <Link
                        to="/dashboard"
                        className="group px-8 py-4 bg-black text-white rounded-full text-lg font-medium hover:bg-gray-800 transition-all hover:shadow-xl flex items-center gap-2"
                    >
                        Try Live System <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" />
                    </Link>
                    <a href="#how-it-works" className="px-8 py-4 bg-white text-gray-700 border border-gray-200 rounded-full text-lg font-medium hover:bg-gray-50 transition-colors">
                        How it works
                    </a>
                </div>
            </section>

            {/* How it Works / Feature Grid */}
            <section id="how-it-works" className="py-24 bg-gray-50">
                <div className="max-w-6xl mx-auto px-6">
                    <div className="text-center mb-16">
                        <h2 className="text-3xl font-bold mb-4">The Response Pipeline</h2>
                        <p className="text-gray-500 max-w-xl mx-auto">From a messy WhatsApp message to a dispatched ambulance in milliseconds.</p>
                    </div>

                    <div className="mb-20">
                        <PipelineVisualizer />
                    </div>

                    <div className="grid md:grid-cols-3 gap-8 text-left">
                        {/* Detail Card 1 */}
                        <div className="bg-white p-6 rounded-xl hover:bg-gray-50 transition-colors">
                            <h3 className="font-bold text-gray-900 mb-2 flex items-center gap-2">
                                <span className="w-2 h-2 rounded-full bg-blue-500"></span>
                                Hyper-Local Context
                            </h3>
                            <p className="text-sm text-gray-500">
                                Specialized NER models trained on Indian dialects, landmarks ("near generic store"), and unstructured formats.
                            </p>
                        </div>

                        {/* Detail Card 2 */}
                        <div className="bg-white p-6 rounded-xl hover:bg-gray-50 transition-colors">
                            <h3 className="font-bold text-gray-900 mb-2 flex items-center gap-2">
                                <span className="w-2 h-2 rounded-full bg-purple-500"></span>
                                Transparent Scoring
                            </h3>
                            <p className="text-sm text-gray-500">
                                Every decision is explainable. Urgency scores come with a breakdown of exactly <i>why</i> a request was flagged critical.
                            </p>
                        </div>

                        {/* Detail Card 3 */}
                        <div className="bg-white p-6 rounded-xl hover:bg-gray-50 transition-colors">
                            <h3 className="font-bold text-gray-900 mb-2 flex items-center gap-2">
                                <span className="w-2 h-2 rounded-full bg-green-500"></span>
                                Real-Time Dispatch
                            </h3>
                            <p className="text-sm text-gray-500">
                                Instant availability checks against registered resources. Zero latency between analysis and action.
                            </p>
                        </div>
                    </div>
                </div>
            </section>

            {/* Trust/Footer Section */}
            <section className="py-20 border-t border-gray-200">
                <div className="max-w-4xl mx-auto text-center px-6">
                    <h2 className="text-2xl font-bold mb-8">Built for reliability, not just hype.</h2>
                    <div className="flex flex-wrap justify-center gap-8 md:gap-16 opacity-50 grayscale">
                        {/* Trusted logos placeholders or text */}
                        <div className="flex items-center gap-2 font-semibold text-lg"><Radio size={20} /> Low Latency</div>
                        <div className="flex items-center gap-2 font-semibold text-lg"><ShieldCheck size={20} /> Explanable AI</div>
                        <div className="flex items-center gap-2 font-semibold text-lg"><Activity size={20} /> 99.9% Uptime</div>
                    </div>
                </div>
            </section>
        </div>
    );
}
