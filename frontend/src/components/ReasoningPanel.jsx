import { AlertTriangle } from 'lucide-react';

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
        <div className="p-4 bg-blue-50 border border-blue-100 rounded-lg animate-fade-in shadow-sm">
            <div className="flex items-center justify-between mb-3">
                <h4 className="font-semibold text-blue-900 text-sm uppercase tracking-wide">Urgency Analysis</h4>
                <div className="flex items-center gap-4">
                    <span className="text-xs text-blue-600 font-medium">
                        Confidence: {displayConfidence}%
                    </span>
                    <span className="text-sm font-bold text-blue-800 bg-blue-100 px-2 py-0.5 rounded">
                        Score: {displayScore}/100
                    </span>
                </div>
            </div>

            {/* Reasoning breakdown */}
            {reasoning && reasoning.length > 0 && (
                <div className="mb-3">
                    <div className="text-xs font-bold text-blue-400 mb-2">REASONING</div>
                    <div className="space-y-2">
                        {reasoning.map((line, idx) => (
                            <div key={idx} className="text-sm text-gray-700 pl-3 border-l-2 border-blue-400 py-0.5">
                                {line}
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Flags/warnings */}
            {flags && flags.length > 0 && (
                <div className="mt-3 pt-3 border-t border-blue-200">
                    <div className="text-xs font-bold text-orange-600 mb-2">FLAGS</div>
                    <div className="space-y-1">
                        {flags.map((flag, idx) => (
                            <div key={idx} className="text-sm text-orange-800 flex items-start gap-2 bg-orange-50 p-2 rounded border border-orange-100">
                                <AlertTriangle size={16} />
                                <span className="font-medium">{flag}</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
