import { useState } from 'react';
import useStore from '../store/useStore';

export default function DispatchButton({ requestId, resourceId, suggestedQuantity, maxQuantity }) {
    const [quantity, setQuantity] = useState(suggestedQuantity || 1);
    const [showConfirm, setShowConfirm] = useState(false);

    const { dispatchResource, loading, error } = useStore();
    const isDispatching = loading.dispatch[requestId];
    const dispatchError = error.dispatch[requestId];

    const handleDispatch = async () => {
        await dispatchResource(requestId, resourceId, quantity);
        setShowConfirm(false);
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
                    className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {isDispatching ? 'Dispatching...' : 'Confirm'}
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
                className="w-full px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700"
            >
                🚨 Dispatch
            </button>
            {dispatchError && (
                <div className="mt-1 text-xs text-red-600">
                    {dispatchError}
                </div>
            )}
        </div>
    );
}
