/**
 * Component to display extracted entities from AI analysis
 */
export default function EntityPanel({ extraction }) {
    if (!extraction) {
        return (
            <div className="p-3 bg-gray-50 rounded text-sm text-gray-600">
                No entity extraction available
            </div>
        );
    }

    const {
        location,
        latitude,
        longitude,
        location_confidence,
        need_type,
        need_type_confidence,
        quantity,
        quantity_confidence,
        contact,
        affected_count,
        location_alternatives
    } = extraction;

    return (
        <div className="p-4 bg-indigo-50 border border-indigo-200 rounded">
            <h4 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                <span>🔍</span>
                <span>Extracted Entities</span>
            </h4>

            <div className="grid grid-cols-2 gap-3 text-sm">
                {/* Location */}
                <div className="col-span-2 sm:col-span-1">
                    <div className="text-xs font-semibold text-gray-600 mb-1">📍 LOCATION</div>
                    <div className="text-gray-800">
                        {location || <span className="text-gray-400 italic">Not detected</span>}
                    </div>
                    {location_confidence && (
                        <div className="text-xs text-gray-500 mt-1">
                            Confidence: {(location_confidence * 100).toFixed(0)}%
                        </div>
                    )}
                </div>

                {/* Location Ambiguity Warning */}
                {location_alternatives && location_alternatives.length > 0 && (
                    <div className="col-span-2 p-3 bg-amber-50 border border-amber-200 rounded mb-2">
                        <div className="flex items-center gap-2 text-amber-800 font-bold mb-2 text-xs uppercase tracking-wide">
                            <span>⚠️</span>
                            <span>Ambiguous Location Detected</span>
                        </div>
                        <div className="text-xs text-amber-700 mb-2">
                            Multiple potential matches found. Please verify:
                        </div>
                        <div className="space-y-2">
                            {location_alternatives.map((alt, idx) => (
                                <div key={idx} className="flex justify-between items-center p-2 bg-white rounded border border-amber-100 hover:bg-amber-50 cursor-pointer transition-colors">
                                    <div>
                                        <div className="font-medium text-gray-800">{alt.value}</div>
                                        <div className="text-[10px] text-gray-500 font-mono">
                                            {alt.lat?.toFixed(4)}°N, {alt.lng?.toFixed(4)}°E • {(alt.confidence * 100).toFixed(0)}%
                                        </div>
                                    </div>
                                    <button
                                        onClick={() => alert(`Location updated to: ${alt.value}`)}
                                        className="text-xs bg-amber-100 text-amber-700 px-2 py-1 rounded hover:bg-amber-200 font-medium"
                                    >
                                        Select
                                    </button>
                                </div>
                            ))}
                        </div>

                        {/* Manual entry option */}
                        <div className="mt-2 pt-2 border-t border-amber-200">
                            <button
                                onClick={() => {
                                    const val = prompt("Enter manual location name:");
                                    if (val) alert(`Location manually set to: ${val}`);
                                }}
                                className="w-full text-xs text-amber-800 hover:text-amber-900 font-medium py-1 dashed border border-amber-300 rounded hover:bg-amber-100"
                            >
                                ✏️ Enter Location Manually
                            </button>
                        </div>
                    </div>
                )}

                {/* Coordinates */}
                <div className="col-span-2 sm:col-span-1">
                    <div className="text-xs font-semibold text-gray-600 mb-1">🗺️ COORDINATES</div>
                    <div className="text-gray-800 font-mono text-xs">
                        {latitude && longitude ? (
                            <>
                                {latitude.toFixed(4)}°N, {longitude.toFixed(4)}°E
                            </>
                        ) : (
                            <span className="text-gray-400 italic">Not available</span>
                        )}
                    </div>
                </div>

                {/* Need Type */}
                <div className="col-span-2 sm:col-span-1">
                    <div className="text-xs font-semibold text-gray-600 mb-1">🆘 NEED TYPE</div>
                    <div className="text-gray-800 capitalize">
                        {need_type || <span className="text-gray-400 italic">Not detected</span>}
                    </div>
                    {need_type_confidence && (
                        <div className="text-xs text-gray-500 mt-1">
                            Confidence: {(need_type_confidence * 100).toFixed(0)}%
                        </div>
                    )}
                </div>

                {/* Contact */}
                <div className="col-span-2 sm:col-span-1">
                    <div className="text-xs font-semibold text-gray-600 mb-1">📞 CONTACT</div>
                    <div className="text-gray-800">
                        {contact || <span className="text-gray-400 italic">Not provided</span>}
                    </div>
                </div>

                {/* Affected Count */}
                <div className="col-span-2 sm:col-span-1">
                    <div className="text-xs font-semibold text-gray-600 mb-1">👥 AFFECTED COUNT</div>
                    <div className="text-gray-800">
                        {affected_count || <span className="text-gray-400 italic">Unknown</span>}
                    </div>
                </div>

                {/* Quantity */}
                {quantity && (
                    <div className="col-span-2 sm:col-span-1">
                        <div className="text-xs font-semibold text-gray-600 mb-1">📦 QUANTITY NEEDED</div>
                        <div className="text-gray-800">
                            {quantity}
                        </div>
                        {quantity_confidence && (
                            <div className="text-xs text-gray-500 mt-1">
                                Confidence: {(quantity_confidence * 100).toFixed(0)}%
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
