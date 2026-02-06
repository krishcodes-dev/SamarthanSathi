import { useState } from 'react';
import LoadingSpinner from './LoadingSpinner';
import { Bot, Flame, MapPin, Zap, Check, X } from 'lucide-react';

export default function ConfirmationDialog({ requestData, onConfirm, onCorrect }) {
    const [showCorrection, setShowCorrection] = useState(false);
    const [corrections, setCorrections] = useState({});
    const [isSubmitting, setIsSubmitting] = useState(false);

    // Defensive check
    if (!requestData || !requestData.extraction) return null;

    const { extraction, urgency_analysis } = requestData;

    const handleConfirm = async () => {
        setIsSubmitting(true);
        try {
            await onConfirm();
        } catch (err) {
            console.error(err);
            // Parent handles alerts
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleCorrect = async () => {
        setIsSubmitting(true);
        try {
            await onCorrect(corrections);
        } catch (err) {
            console.error(err);
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 animate-fade-in backdrop-blur-sm">
            <div className="bg-white rounded-xl shadow-2xl p-6 max-w-md w-full border border-gray-100">
                <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                    <Bot className="text-blue-600" size={24} /> Needs Confirmation
                </h3>
                <p className="text-sm text-gray-600 mb-6">
                    Help us learn! Is our interpretation correct?
                </p>

                <div className="space-y-4 mb-8 bg-gray-50 p-4 rounded-lg border border-gray-200">
                    <div className="flex items-start gap-3">
                        <div className="mt-1 p-1 bg-orange-100 rounded text-orange-600">
                            <Flame size={20} />
                        </div>
                        <div>
                            <div className="text-xs font-bold text-gray-500 uppercase tracking-wide">Need Type</div>
                            <div className="text-lg font-semibold text-gray-800 capitalize">
                                {extraction.need_type || 'Unknown'}
                            </div>
                        </div>
                    </div>

                    <div className="flex items-start gap-3">
                        <div className="mt-1 p-1 bg-green-100 rounded text-green-600">
                            <MapPin size={20} />
                        </div>
                        <div>
                            <div className="text-xs font-bold text-gray-500 uppercase tracking-wide">Location</div>
                            <div className="text-lg font-semibold text-gray-800">
                                {extraction.location || 'Unknown'}
                            </div>
                        </div>
                    </div>

                    <div className="flex items-start gap-3">
                        <div className="mt-1 p-1 bg-yellow-100 rounded text-yellow-600">
                            <Zap size={20} />
                        </div>
                        <div>
                            <div className="text-xs font-bold text-gray-500 uppercase tracking-wide">Urgency</div>
                            <div className="flex items-center gap-2">
                                <span className={`px-2 py-0.5 rounded text-sm font-bold 
                                    ${urgency_analysis?.level === 'U1' ? 'bg-red-100 text-red-800' :
                                        urgency_analysis?.level === 'U2' ? 'bg-orange-100 text-orange-800' : 'bg-blue-100 text-blue-800'}`}>
                                    {urgency_analysis?.level || 'N/A'}
                                </span>
                                <span className="text-sm text-gray-600 uppercase font-medium">
                                    ({urgency_analysis?.level === 'U1' ? 'Critical' : urgency_analysis?.level === 'U2' ? 'High' : 'Medium'})
                                </span>
                            </div>
                        </div>
                    </div>
                </div>

                {!showCorrection ? (
                    <div className="flex gap-3">
                        <button
                            onClick={handleConfirm}
                            disabled={isSubmitting}
                            className="flex-1 bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700 transition shadow-sm hover:shadow-md flex justify-center items-center gap-2"
                        >
                            {isSubmitting ? <LoadingSpinner size="sm" color="text-white" /> : (
                                <><Check size={18} /> Correct</>
                            )}
                        </button>

                        <button
                            onClick={() => setShowCorrection(true)}
                            disabled={isSubmitting}
                            className="flex-1 bg-white border-2 border-orange-200 text-orange-600 py-3 rounded-lg font-semibold hover:bg-orange-50 hover:border-orange-300 transition hover:shadow-md flex justify-center items-center gap-2"
                        >
                            <X size={18} /> Incorrect
                        </button>
                    </div>
                ) : (
                    <div className="space-y-4 animate-fade-in-up">
                        <div>
                            <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Correct Need Type</label>
                            <select
                                className="w-full border border-gray-300 rounded p-2 focus:ring-2 focus:ring-blue-500 outline-none"
                                onChange={(e) => setCorrections({ ...corrections, need_type: e.target.value })}
                            >
                                <option value="">Select correct need...</option>
                                <option value="medical">Medical</option>
                                <option value="rescue">Rescue</option>
                                <option value="fire">Fire</option>
                                <option value="food">Food/Water</option>
                                <option value="police">Police/Security</option>
                            </select>
                        </div>

                        <div>
                            <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Correct Location</label>
                            <input
                                type="text"
                                placeholder="E.g., Andheri West"
                                className="w-full border border-gray-300 rounded p-2 focus:ring-2 focus:ring-blue-500 outline-none"
                                onChange={(e) => setCorrections({ ...corrections, location: e.target.value })}
                            />
                        </div>

                        <div className="flex gap-3 pt-2">
                            <button
                                onClick={() => setShowCorrection(false)}
                                className="flex-1 text-gray-500 hover:text-gray-700 font-medium"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleCorrect}
                                disabled={isSubmitting}
                                className="flex-1 bg-teal-600 text-white py-2 rounded-lg font-semibold hover:bg-teal-700 transition shadow-sm"
                            >
                                {isSubmitting ? 'Submitting...' : 'Submit Correction'}
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
