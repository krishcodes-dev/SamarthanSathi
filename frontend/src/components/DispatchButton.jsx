import { useState } from 'react';
import { Ambulance, Loader2 } from 'lucide-react';
import api from '../api/client';

export default function DispatchButton({ requestId, resourceId, suggestedQuantity, maxQuantity, onSuccess }) {
    const [quantity, setQuantity] = useState(suggestedQuantity || 1);
    const [showConfirm, setShowConfirm] = useState(false);
    const [isDispatching, setIsDispatching] = useState(false);
    const [dispatchError, setDispatchError] = useState(null);

    const handleDispatch = async () => {
        // Guard against missing IDs (User instruction)
        if (!requestId || !resourceId) {
            console.error("Dispatch attempted with missing IDs", {
                requestId,
                resourceId,
            });
            setDispatchError("Internal Error: Missing IDs");
            return;
        }

        // Quick Sanity Check (User instruction)

        setIsDispatching(true);
        setDispatchError(null);

        try {
            await api.dispatchResource(requestId, resourceId, quantity);
            setShowConfirm(false);
            if (onSuccess) onSuccess();
        } catch (err) {
            console.error("Dispatch failed:", err);
            setDispatchError(err.message || "Dispatch failed");
        } finally {
            setIsDispatching(false);
        }
    };

    if (showConfirm) {
        return (
            <div className="flex items-center gap-2">
                <input
                    type="number"
                    min="1"
                    max={maxQuantity}
                    value={quantity}
                    onChange={(e) => setQuantity(parseInt(e.target.value) || 1)}
                    className="w-20 px-2 py-1 text-sm border border-gray-300 rounded"
                    disabled={isDispatching}
                />
                <button
                    onClick={handleDispatch}
                    disabled={isDispatching || quantity > maxQuantity}
                    className="w-full mt-3 bg-black text-white py-2 rounded-lg text-sm font-medium hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
                >
                    {isDispatching ? (
                        <Loader2 size={16} className="animate-spin" />
                    ) : (
                        <Ambulance size={16} />
                    )}
                    {isDispatching ? 'Dispatching...' : 'Dispatch Resource'}
                </button>
                <button
                    onClick={() => setShowConfirm(false)}
                    disabled={isDispatching}
                    className="px-3 py-1 text-sm bg-gray-300 text-gray-700 rounded hover:bg-gray-400"
                >
                    Cancel
                </button>
            </div>
        );
    }

    return (
        <div>
            <button
                onClick={() => setShowConfirm(true)}
                className="w-full px-3 py-2 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium flex items-center justify-center gap-2 transition-colors shadow-sm"
            >
                <Ambulance size={16} />
                Dispatch Resource
            </button>
            {dispatchError && (
                <div className="mt-1 text-xs text-red-600">
                    {dispatchError}
                </div>
            )}
        </div>
    );
}
