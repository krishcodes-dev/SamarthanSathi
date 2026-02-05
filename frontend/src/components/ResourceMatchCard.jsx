import DispatchButton from './DispatchButton';

export default function ResourceMatchCard({ match, requestId }) {
    const {
        resource_id,
        provider_name,
        resource_type,
        quantity_available,
        match_score,
        distance_km,
        reasoning
    } = match;

    return (
        <div className="p-3 bg-green-50 border border-green-200 rounded">
            <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                    <h6 className="font-semibold text-gray-800">{provider_name}</h6>
                    <p className="text-xs text-gray-600">
                        {resource_type} • {distance_km.toFixed(1)} km away
                    </p>
                </div>
                <div className="text-right">
                    <div className="text-sm font-semibold text-green-700">
                        Match: {(match_score * 100).toFixed(0)}%
                    </div>
                    <div className="text-xs text-gray-600">
                        Available: {quantity_available}
                    </div>
                </div>
            </div>

            {/* Match reasoning */}
            {reasoning && reasoning.length > 0 && (
                <div className="mb-2 text-xs text-gray-600">
                    {reasoning.slice(0, 2).map((line, idx) => (
                        <div key={idx} className="pl-2 border-l-2 border-green-300">
                            {line}
                        </div>
                    ))}
                </div>
            )}

            {/* Dispatch button */}
            <div className="mt-2">
                <DispatchButton
                    requestId={requestId}
                    resourceId={resource_id}
                    suggestedQuantity={1}
                    maxQuantity={quantity_available}
                />
            </div>
        </div>
    );
}
