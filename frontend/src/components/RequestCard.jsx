import { useState } from 'react';
import UrgencyBadge from './UrgencyBadge';
import ConfidenceBadge from './ConfidenceBadge';
import ReasoningPanel from './ReasoningPanel';
import EntityPanel from './EntityPanel';
import ResourceMatchCard from './ResourceMatchCard';
import LoadingSpinner from './LoadingSpinner';
import useStore from '../store/useStore';
import {
    ChevronDown,
    ChevronUp,
    Search,
    FileText,
    MapPin,
    Phone,
    Box,
    Hash,
    BrainCircuit,
    AlertTriangle
} from 'lucide-react';

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
        <div className="bg-white border border-gray-100 rounded-xl shadow-sm p-5 mb-4 hover:shadow-md transition-all duration-200">
            {/* Header with urgency badge */}
            <div className="flex items-start justify-between mb-4">
                <UrgencyBadge level={urgency.level} score={urgency.score} />
                <span className="text-xs text-gray-400 font-medium">
                    {new Date(request.created_at).toLocaleString()}
                </span>
            </div>

            {/* Crisis message */}
            <div className="mb-4">
                <p className="text-gray-900 text-sm leading-relaxed font-medium">
                    {request.raw_text}
                </p>
            </div>

            {/* Confidence Indicators */}
            {(extraction.overall_confidence !== undefined || (extraction.flags && extraction.flags.length > 0)) && (
                <div className="flex flex-wrap items-center gap-2 mb-4">
                    {extraction.overall_confidence !== undefined && (
                        <ConfidenceBadge confidence={extraction.overall_confidence} />
                    )}

                    {extraction.flags && extraction.flags.map((flag, idx) => (
                        <span key={idx} className="text-xs bg-orange-50 text-orange-700 border border-orange-100 px-2 py-0.5 rounded-md flex items-center gap-1 font-medium">
                            <AlertTriangle size={10} /> {flag.replace(/_/g, ' ')}
                        </span>
                    ))}
                </div>
            )}

            {/* Extracted entities grid */}
            <div className="grid grid-cols-2 gap-3 mb-5 text-xs">
                {extraction.need_type && (
                    <div className="flex items-center gap-2 text-gray-600">
                        <Box size={14} className="text-gray-400" />
                        <div>
                            <span className="font-semibold text-gray-700">Need:</span>{' '}
                            <span className="text-gray-900 bg-gray-50 px-1.5 py-0.5 rounded">{extraction.need_type}</span>
                        </div>
                    </div>
                )}
                {extraction.quantity && (
                    <div className="flex items-center gap-2 text-gray-600">
                        <Hash size={14} className="text-gray-400" />
                        <div>
                            <span className="font-semibold text-gray-700">Quantity:</span>{' '}
                            <span className="text-gray-900">{extraction.quantity || extraction.affected_count}</span>
                        </div>
                    </div>
                )}
                {extraction.location && (
                    <div className="flex items-center gap-2 text-gray-600">
                        <MapPin size={14} className="text-gray-400" />
                        <div>
                            <span className="font-semibold text-gray-700">Location:</span>{' '}
                            <span className="text-gray-900">{extraction.location}</span>
                        </div>
                    </div>
                )}
                {extraction.contact && (
                    <div className="flex items-center gap-2 text-gray-600">
                        <Phone size={14} className="text-gray-400" />
                        <div>
                            <span className="font-semibold text-gray-700">Contact:</span>{' '}
                            <span className="text-gray-900">{extraction.contact}</span>
                        </div>
                    </div>
                )}
            </div>

            {/* Action buttons */}
            <div className="flex items-center justify-between gap-2 border-t border-gray-100 pt-4">
                <div className="flex gap-2">
                    <button
                        onClick={() => setShowReasoning(!showReasoning)}
                        className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium bg-blue-50 text-blue-700 rounded-md hover:bg-blue-100 transition-colors"
                    >
                        <BrainCircuit size={14} />
                        Reasoning
                        {showReasoning ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                    </button>

                    <button
                        onClick={() => setShowDetails(!showDetails)}
                        className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium bg-purple-50 text-purple-700 rounded-md hover:bg-purple-100 transition-colors"
                    >
                        <FileText size={14} />
                        Details
                        {showDetails ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                    </button>
                </div>

                <div className="flex gap-2 items-center">
                    <span className={`px-2 py-1 text-[10px] font-bold uppercase tracking-wider rounded-md ${request.status === 'new' ? 'bg-gray-100 text-gray-600' :
                        request.status === 'in_progress' ? 'bg-yellow-100 text-yellow-800' :
                            request.status === 'dispatched' ? 'bg-green-100 text-green-800' :
                                'bg-gray-100 text-gray-600'
                        }`}>
                        {request.status.replace('_', ' ')}
                    </span>

                    <button
                        onClick={handleFindResources}
                        disabled={!extraction.need_type}
                        className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${extraction.need_type
                            ? 'bg-black text-white hover:bg-gray-800 shadow-sm'
                            : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                            }`}
                        title={!extraction.need_type ? 'Cannot find resources: Need type not identified' : 'Find matching resources'}
                    >
                        <Search size={14} />
                        {extraction.need_type ? 'Find Resources' : 'Unknown Need'}
                    </button>
                </div>
            </div>

            {/* Expandable reasoning panel */}
            {showReasoning && (
                <div className="mt-4 animate-fade-in-down">
                    <ReasoningPanel urgencyAnalysis={urgency} />
                </div>
            )}

            {/* Entity extraction details */}
            {showDetails && (
                <div className="mt-4 animate-fade-in-down">
                    <EntityPanel extraction={extraction} />
                </div>
            )}

            {/* Resource matches */}
            {showMatches && (
                <div className="mt-4 pt-4 border-t border-gray-100 animate-fade-in-down">
                    <h5 className="font-semibold text-gray-900 text-xs uppercase tracking-wide mb-3 flex items-center gap-2">
                        <Search size={14} /> Resource Matches
                    </h5>

                    {isLoadingMatches && <LoadingSpinner size="sm" text="Finding resources..." />}

                    {matchError && (
                        <div className="p-3 bg-red-50 border border-red-100 rounded-md text-red-600 text-xs">
                            Error: {matchError}
                        </div>
                    )}

                    {!isLoadingMatches && !matchError && matches.length === 0 && (
                        <div className="p-4 bg-gray-50 rounded-lg text-gray-500 text-sm text-center italic">
                            No matching resources found nearby.
                        </div>
                    )}

                    {matches.length > 0 && (
                        <div className="space-y-3">
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
