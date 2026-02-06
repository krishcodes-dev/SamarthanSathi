import { useState } from 'react';
import api from '../api/client';
import LoadingSpinner from './LoadingSpinner';
import ConfirmationDialog from './ConfirmationDialog';
import { Megaphone, CheckCircle, XCircle, Send } from 'lucide-react';

export default function CreateRequestForm({ onSuccess }) {
    const [message, setMessage] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [previewData, setPreviewData] = useState(null); // Stores preview response
    const [error, setError] = useState(null);
    const [successMessage, setSuccessMessage] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsSubmitting(true);
        setError(null);
        setSuccessMessage('');
        setPreviewData(null);

        try {
            // STEP 1: Get Preview (No persistence)
            const data = await api.previewRequest(message);
            setPreviewData(data);
            // Dialog will now appear due to previewData presence
        } catch (err) {
            console.error(err);
            setError(err.message || 'Failed to process request');
            // If preview fails, we just show error, no dialog
        } finally {
            setIsSubmitting(false);
        }
    };

    // Callback for "Yes, Correct"
    const handleConfirm = async () => {
        try {
            // STEP 2: Submit Real Request
            const request = await api.submitRequest(message, true, previewData.preview_id);

            // STEP 3: Submit Positive Feedback (Audit)
            await api.submitUserFeedback({
                request_id: request.id,
                is_correct: true
            });

            // Success State
            setSuccessMessage(`Request #${request.id.slice(0, 8)} submitted successfully.`);
            setMessage('');
            setPreviewData(null);
            if (onSuccess) onSuccess();

            // Auto-hide success message
            setTimeout(() => setSuccessMessage(''), 5000);
        } catch (err) {
            console.error('Confirm failed:', err);
            alert('Failed to submit confirmed request. Please try again.');
        }
    };

    // Callback for "No, Incorrect" (with corrections)
    const handleCorrect = async (corrections) => {
        try {
            // STEP 2: Submit Real Request (Flagged as unconfirmed)
            const request = await api.submitRequest(message, false, previewData.preview_id);

            // STEP 3: Submit Negative Feedback (Training Data)
            await api.submitUserFeedback({
                request_id: request.id,
                is_correct: false,
                corrected_text: JSON.stringify(corrections)
            });

            // Success State
            setSuccessMessage(`Request submitted with corrections.`);
            setMessage('');
            setPreviewData(null);
            if (onSuccess) onSuccess();

            setTimeout(() => setSuccessMessage(''), 5000);
        } catch (err) {
            console.error('Correction submit failed:', err);
            alert('Failed to submit request. Please try again.');
        }
    };

    return (
        <div className="bg-white border border-gray-100 rounded-xl shadow-sm p-5 mb-6">
            <h3 className="font-bold text-gray-900 mb-4 flex items-center gap-2 text-sm uppercase tracking-wide">
                <Megaphone size={16} className="text-blue-600" /> Report a Crisis
            </h3>

            {/* Confirmation Dialog (Preview Gate) */}
            {previewData && (
                <ConfirmationDialog
                    requestData={previewData}
                    onConfirm={handleConfirm}
                    onCorrect={handleCorrect}
                />
            )}

            {successMessage && !previewData && (
                <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-md text-green-700 text-sm flex items-center gap-2 font-medium">
                    <CheckCircle size={16} /> {successMessage}
                </div>
            )}

            {error && (
                <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
                    <h4 className="font-bold text-red-800 text-sm mb-2 flex items-center gap-2">
                        <XCircle size={16} /> Submission Failed
                    </h4>
                    <p className="text-sm text-red-700 mb-2 font-medium">{error.message}</p>

                    {/* Structured errors */}
                    {error.details && error.details.reasons && (
                        <ul className="list-disc ml-5 text-xs text-red-600 space-y-1">
                            {error.details.reasons.map((reason, idx) => (
                                <li key={idx}>{reason}</li>
                            ))}
                        </ul>
                    )}
                </div>
            )}

            <form onSubmit={handleSubmit}>
                <div className="mb-4">
                    <textarea
                        value={message}
                        onChange={(e) => setMessage(e.target.value)}
                        placeholder="Describe the crisis situation... (e.g., 'Fire at Andheri Station, need ambulance')"
                        className="w-full h-28 p-4 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-black focus:border-black transition-all resize-none shadow-sm"
                        disabled={isSubmitting}
                    />
                    <div className="flex justify-between mt-2 px-1">
                        <span className={`text-xs font-medium ${message.length > 500 ? 'text-red-500' :
                            message.length > 0 && message.length < 10 ? 'text-orange-500' : 'text-gray-400'}`}>
                            {message.length} chars
                        </span>
                        <span className="text-xs text-gray-400">Min 10 chars</span>
                    </div>
                </div>

                <div className="flex justify-end">
                    <button
                        type="submit"
                        disabled={isSubmitting || !message.trim()}
                        className="bg-black text-white font-medium py-2.5 px-6 rounded-lg hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all hover:shadow-lg active:scale-95 flex items-center justify-center gap-2 text-sm"
                    >
                        {isSubmitting ? (
                            <>
                                <LoadingSpinner size="sm" color="text-white" />
                                Analyzing...
                            </>
                        ) : (
                            <>
                                <Send size={14} /> Submit Report
                            </>
                        )}
                    </button>
                </div>
            </form>
        </div>
    );
}
