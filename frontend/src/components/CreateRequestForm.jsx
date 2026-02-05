import { useState } from 'react';
import api from '../api/client';
import LoadingSpinner from './LoadingSpinner';

export default function CreateRequestForm({ onSuccess }) {
    const [message, setMessage] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState(null);
    const [successId, setSuccessId] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setSuccessId(null);
        setIsSubmitting(true);

        try {
            const data = await api.submitRequest(message);
            setSuccessId(data.id);
            setMessage('');
            if (onSuccess) onSuccess();

            // Auto-hide success message after 5s
            setTimeout(() => setSuccessId(null), 5000);

        } catch (err) {
            console.error(err);
            setError(err);
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="bg-white border border-gray-200 rounded-lg shadow-sm p-4 mb-6">
            <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                <span>📣</span> Report a Crisis
            </h3>

            {successId && (
                <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded text-green-700 text-sm flex items-center gap-2">
                    ✅ Request submitted successfully! (ID: {successId.substring(0, 8)}...)
                </div>
            )}

            {error && (
                <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded">
                    <h4 className="font-bold text-red-800 text-sm mb-2 flex items-center gap-2">
                        ❌ Submission Failed
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
                <div className="mb-3">
                    <textarea
                        value={message}
                        onChange={(e) => setMessage(e.target.value)}
                        placeholder="Describe the crisis situation... (e.g., 'Fire at Andheri Station, need ambulance')"
                        className="w-full h-24 p-3 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow resize-none"
                        disabled={isSubmitting}
                    />
                    <div className="flex justify-between mt-1 px-1">
                        <span className={`text-xs ${message.length > 500 ? 'text-red-500 font-bold' :
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
                        className="bg-blue-600 text-white font-medium py-2 px-6 rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2 text-sm"
                    >
                        {isSubmitting ? (
                            <>
                                <LoadingSpinner size="sm" color="text-white" />
                                Submitting...
                            </>
                        ) : (
                            'Submit Report'
                        )}
                    </button>
                </div>
            </form>
        </div>
    );
}
