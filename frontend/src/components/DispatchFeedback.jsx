import { useState } from 'react';
import client from '../api/client';

export default function DispatchFeedback({ requestId, onComplete }) {
    const [extractionRating, setExtractionRating] = useState(0);
    const [matchingRating, setMatchingRating] = useState(0);
    const [comments, setComments] = useState('');
    const [submitting, setSubmitting] = useState(false);
    const [submitted, setSubmitted] = useState(false);

    // If user dismisses or skips
    if (submitted) return null;

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSubmitting(true);

        try {
            // Use the strict dispatcher feedback endpoint
            await client.submitDispatcherFeedback({
                request_id: requestId,
                extraction_rating: extractionRating || null,
                matching_rating: matchingRating || null,
                comment: comments
            });
            // Silent success - don't block user
            console.log('Feedback submitted successfully');
        } catch (error) {
            // Silent failure - log but don't alert
            console.error('Feedback submission failed:', error);
        } finally {
            setSubmitting(false);
            setSubmitted(true);
            if (onComplete) onComplete();
        }
    };

    const handleSkip = () => {
        setSubmitted(true);
        if (onComplete) onComplete();
    };

    return (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-4 animate-fade-in">
            <div className="flex justify-between items-start mb-2">
                <h4 className="text-sm font-semibold text-blue-800">
                    How was this match?
                </h4>
                <button
                    onClick={handleSkip}
                    className="text-gray-400 hover:text-gray-600 text-xs"
                >
                    ✕
                </button>
            </div>

            <p className="text-xs text-blue-600 mb-3">
                Your feedback helps improve future recommendations.
            </p>

            <form onSubmit={handleSubmit}>
                {/* Extraction Rating */}
                <div className="mb-3">
                    <label className="block text-xs font-bold text-gray-500 uppercase mb-1">
                        Extraction Accuracy
                    </label>
                    <div className="flex gap-1">
                        {[1, 2, 3, 4, 5].map((star) => (
                            <button
                                key={star}
                                type="button"
                                className={`text-xl transition-colors ${star <= extractionRating ? 'text-yellow-400' : 'text-gray-300'}`}
                                onClick={() => setExtractionRating(star)}
                                title="Rate extraction quality"
                            >
                                ★
                            </button>
                        ))}
                    </div>
                </div>

                {/* Matching Rating */}
                <div className="mb-3">
                    <label className="block text-xs font-bold text-gray-500 uppercase mb-1">
                        Resource Matching
                    </label>
                    <div className="flex gap-1">
                        {[1, 2, 3, 4, 5].map((star) => (
                            <button
                                key={star}
                                type="button"
                                className={`text-xl transition-colors ${star <= matchingRating ? 'text-yellow-400' : 'text-gray-300'}`}
                                onClick={() => setMatchingRating(star)}
                                title="Rate matching quality"
                            >
                                ★
                            </button>
                        ))}
                    </div>
                </div>

                {/* Optional Comment */}
                <textarea
                    value={comments}
                    onChange={(e) => setComments(e.target.value)}
                    placeholder="Optional comments on AI performance..."
                    className="w-full text-xs p-2 border border-gray-300 rounded mb-2 focus:ring-1 focus:ring-blue-500 outline-none resize-none"
                    rows="2"
                />

                {/* Actions */}
                <div className="flex gap-2 justify-end">
                    <button
                        type="button"
                        onClick={handleSkip}
                        className="px-3 py-1 text-xs text-gray-500 hover:text-gray-700"
                    >
                        Skip
                    </button>
                    <button
                        type="submit"
                        disabled={(!extractionRating && !matchingRating) || submitting}
                        className="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {submitting ? 'Sending...' : 'Submit Feedback'}
                    </button>
                </div>
            </form>
        </div>
    );
}
