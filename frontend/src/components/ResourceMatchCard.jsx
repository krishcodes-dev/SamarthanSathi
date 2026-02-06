import { useState } from 'react';
import DispatchButton from './DispatchButton';
import DispatchFeedback from './DispatchFeedback';
import { CheckCircle, MapPin, Package } from 'lucide-react';

export default function ResourceMatchCard({ match, requestId, onDispatch }) {
    const {
        resource_id,
        provider_name,
        resource_type,
        quantity_available,
        match_score,
        distance_km,
        reasoning
    } = match;

    const [dispatchSuccess, setDispatchSuccess] = useState(false);
    const [showFeedback, setShowFeedback] = useState(false);
    const [error, setError] = useState(null);

    return (
        <div className="p-4 bg-white border border-gray-100 rounded-lg shadow-sm hover:border-gray-200 transition-colors">
            <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                    <h6 className="font-bold text-gray-900 text-sm mb-1">{provider_name}</h6>
                    <div className="flex items-center gap-3 text-xs text-gray-500">
                        <span className="flex items-center gap-1">
                            <Package size={12} /> {resource_type}
                        </span>
                        <span className="flex items-center gap-1">
                            <MapPin size={12} /> {distance_km.toFixed(1)} km
                        </span>
                    </div>
                </div>
                <div className="text-right">
                    <div className="text-sm font-bold text-green-600 bg-green-50 px-2 py-0.5 rounded">
                        {(match_score * 100).toFixed(0)}% Match
                    </div>
                    <div className="text-xs text-gray-400 mt-1">
                        {quantity_available} units available
                    </div>
                </div>
            </div>

            {/* Match reasoning */}
            {reasoning && reasoning.length > 0 && (
                <div className="mb-3 text-xs text-gray-500 bg-gray-50 p-2 rounded border border-gray-100">
                    {reasoning.map((line, idx) => (
                        <div key={idx} className="flex gap-2 mb-1 last:mb-0">
                            <span className="text-green-500">•</span>
                            {line}
                        </div>
                    ))}
                </div>
            )}

            {/* Dispatch button or success message */}
            <div className="mt-2 text-center">
                {dispatchSuccess ? (
                    <div className="p-3 bg-green-50 text-green-700 rounded-md font-medium text-sm flex items-center justify-center gap-2 animate-fade-in">
                        <CheckCircle size={16} /> Dispatched Successfully
                    </div>
                ) : (
                    <DispatchButton
                        requestId={requestId}
                        resourceId={match.resource_id}
                        maxQuantity={match.quantity_available}
                        onSuccess={() => {
                            setDispatchSuccess(true);
                            setShowFeedback(true);
                            if (onDispatch) onDispatch();
                        }}
                    />
                )}
            </div>

            {showFeedback && (
                <DispatchFeedback
                    requestId={requestId}
                    onComplete={() => setShowFeedback(false)}
                />
            )}

            {error && (
                <div className="mt-2 p-2 text-xs text-red-600 bg-red-50 rounded border border-red-100">
                    {error}
                </div>
            )}
        </div>
    );
}

