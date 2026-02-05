import React from 'react';

export default function ConfidenceBadge({ confidence }) {
    const getColor = (conf) => {
        if (conf >= 0.8) return 'bg-green-100 text-green-800 border-green-200';
        if (conf >= 0.5) return 'bg-yellow-100 text-yellow-800 border-yellow-200';
        return 'bg-red-100 text-red-800 border-red-200';
    };

    const getLabel = (conf) => {
        if (conf >= 0.8) return 'High Confidence';
        if (conf >= 0.5) return 'Medium Confidence';
        return 'Low Confidence';
    };

    const confValue = confidence !== undefined && confidence !== null ? confidence : 0;

    return (
        <span className={`px-2 py-0.5 rounded-full text-xs font-medium border flex items-center gap-1 ${getColor(confValue)}`}>
            <span className="w-1.5 h-1.5 rounded-full bg-current opacity-60"></span>
            {getLabel(confValue)} {(confValue * 100).toFixed(0)}%
        </span>
    );
}
