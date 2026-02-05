export default function ReasoningPanel({ urgencyAnalysis }) {
    if (!urgencyAnalysis) {
        return (
            <div className="p-4  bg-gray-50 rounded text-gray-600">
                No urgency analysis available
            </div>
        );
    }

    const { score, level, reasoning, confidence, flags } = urgencyAnalysis;

    // Safely parse confidence and score
    const displayConfidence = confidence != null ? (confidence * 100).toFixed(0) : '—';
    const displayScore = score != null ? score : '—';

    return (
        <div className="p-4 bg-blue-50 border border-blue-200 rounded animate-fade-in">
            <div className="flex items-center justify-between mb-3">
                <h4 className="font-semibold text-gray-800">Urgency Analysis</h4>
                <div className="flex items-center gap-4">
                    <span className="text-sm text-gray-600">
                        Confidence: {displayConfidence}%
                    </span>
                    <span className="text-sm font-semibold text-blue-700">
                        Score: {displayScore}/100
                    </span>
                </div>
            </div>

            {/* Reasoning breakdown */}
            {reasoning && reasoning.length > 0 && (
                <div className="mb-3">
                    <div className="text-xs font-semibold text-gray-600 mb-2">REASONING:</div>
                    <div className="space-y-1">
                        {reasoning.map((line, idx) => (
                            <div key={idx} className="text-sm text-gray-700 pl-2 border-l-2 border-blue-300">
                                {line}
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Flags/warnings */}
            {flags && flags.length > 0 && (
                <div className="mt-3 pt-3 border-t border-blue-200">
                    <div className="text-xs font-semibold text-gray-600 mb-2">FLAGS:</div>
                    <div className="space-y-1">
                        {flags.map((flag, idx) => (
                            <div key={idx} className="text-sm text-orange-700 flex items-start gap-2">
                                <span>⚠️</span>
                                <span>{flag}</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
