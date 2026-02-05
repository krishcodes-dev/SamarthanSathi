import { useState } from 'react';
import UrgencyBadge from './UrgencyBadge';
import ConfidenceBadge from './ConfidenceBadge';
import ReasoningPanel from './ReasoningPanel';
import EntityPanel from './EntityPanel';
import ResourceMatchCard from './ResourceMatchCard';
import LoadingSpinner from './LoadingSpinner';
import useStore from '../store/useStore';

export default function RequestCard({ request }) {
    const [showReasoning, setShowReasoning] = useState(false);
    const [showMatches, setShowMatches] = useState(false);
    const [showDetails, setShowDetails] = useState(false);

    const { fetchMatches, resourceMatches, loading, error } = useStore();
    const matches = resourceMatches[request.id] || [];
    const isLoadingMatches = loading.matches[request.id];
    const matchError = error.matches[request.id];

    const extraction = request.extraction || {};
    const urgency = request.urgency_analysis || {};

    const handleFindResources = () => {
        if (!showMatches) {
            setShowMatches(true);
            if (!matches.length && !isLoadingMatches) {
                fetchMatches(request.id);
            }
        } else {
            setShowMatches(false);
        }
    };

    return (
        <div className="bg-white border border-gray-200 rounded-lg shadow-sm p-4 mb-4 hover:shadow-md transition-shadow">
            {/* Header with urgency badge */}
            <div className="flex items-start justify-between mb-3">
                <UrgencyBadge level={urgency.level} score={urgency.score} />
                <span className="text-xs text-gray-500">
                    {new Date(request.created_at).toLocaleString()}
                </span>
            </div>

            {/* Crisis message */}
            <div className="mb-3">
                <p className="text-gray-800 text-sm leading-relaxed">
                    {request.raw_text}
                </p>
            </div>

            {/* Confidence Indicators */}
            {(extraction.overall_confidence !== undefined || (extraction.flags && extraction.flags.length > 0)) && (
                <div className="flex flex-wrap items-center gap-2 mb-3">
                    {extraction.overall_confidence !== undefined && (
                        <ConfidenceBadge confidence={extraction.overall_confidence} />
                    )}

                    {extraction.flags && extraction.flags.map((flag, idx) => (
                        <span key={idx} className="text-xs bg-orange-50 text-orange-700 border border-orange-200 px-2 py-0.5 rounded-full flex items-center gap-1 font-medium">
                            <span>⚠️</span> {flag.replace(/_/g, ' ')}
                        </span>
                    ))}
                </div>
            )}

            {/* Extracted entities */}
            <div className="grid grid-cols-2 gap-2 mb-3 text-xs">
                {extraction.need_type && (
                    <div>
                        <span className="font-semibold text-gray-600">Need:</span>{' '}
                        <span className="text-gray-800">{extraction.need_type}</span>
                    </div>
                )}
                {extraction.quantity && (
                    <div>
                        <span className="font-semibold text-gray-600">Quantity:</span>{' '}
                        <span className="text-gray-800">{extraction.quantity || extraction.affected_count}</span>
                    </div>
                )}
                {extraction.location && (
                    <div>
                        <span className="font-semibold text-gray-600">Location:</span>{' '}
                        <span className="text-gray-800">{extraction.location}</span>
                    </div>
                )}
                {extraction.contact && (
                    <div>
                        <span className="font-semibold text-gray-600">Contact:</span>{' '}
                        <span className="text-gray-800">{extraction.contact}</span>
                    </div>
                )}
            </div>

            {/* Action buttons */}
            <div className="flex gap-2 mb-3 flex-wrap">
                <button
                    onClick={() => setShowReasoning(!showReasoning)}
                    className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors"
                >
                    {showReasoning ? '▼' : '▶'} Reasoning
                </button>
                <button
                    onClick={handleFindResources}
                    className="px-3 py-1 text-sm bg-green-100 text-green-700 rounded hover:bg-green-200 transition-colors"
                >
                    {showMatches ? '▼' : '🔍'} Find Resources
                </button>
                <button
                    onClick={() => setShowDetails(!showDetails)}
                    className="px-3 py-1 text-sm bg-purple-100 text-purple-700 rounded hover:bg-purple-200 transition-colors"
                >
                    {showDetails ? '▼' : '📋'} Show Details
                </button>
                <span className={`ml-auto px-2 py-1 text-xs rounded ${request.status === 'new' ? 'bg-gray-200 text-gray-700' :
                    request.status === 'in_progress' ? 'bg-yellow-200 text-yellow-800' :
                        request.status === 'dispatched' ? 'bg-green-200 text-green-800' :
                            'bg-gray-200 text-gray-700'
                    }`}>
                    {request.status.toUpperCase()}
                </span>
            </div>

            {/* Expandable reasoning panel */}
            {showReasoning && (
                <div className="mb-3">
                    <ReasoningPanel urgencyAnalysis={urgency} />
                </div>
            )}

            {/* Entity extraction details */}
            {showDetails && (
                <div className="mb-3">
                    <EntityPanel extraction={extraction} />
                </div>
            )}

            {/* Resource matches */}
            {showMatches && (
                <div className="mt-3 pt-3 border-t border-gray-200">
                    <h5 className="font-semibold text-gray-700 mb-2">Resource Matches</h5>

                    {isLoadingMatches && <LoadingSpinner size="sm" text="Finding resources..." />}

                    {matchError && (
                        <div className="p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
                            Error: {matchError}
                        </div>
                    )}

                    {!isLoadingMatches && !matchError && matches.length === 0 && (
                        <div className="p-3 bg-gray-50 rounded text-gray-600 text-sm">
                            No matching resources found
                        </div>
                    )}

                    {matches.length > 0 && (
                        <div className="space-y-2">
                            {matches.map((match, idx) => (
                                <ResourceMatchCard
                                    key={idx}
                                    match={match}
                                    requestId={request.id}
                                />
                            ))}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
