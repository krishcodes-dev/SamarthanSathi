import React from 'react';
import { Activity } from 'lucide-react';

export default function ConfidenceBadge({ confidence }) {
    const getColor = (conf) => {
        if (conf >= 0.8) return 'bg-green-100 text-green-700 border-green-200';
        if (conf >= 0.5) return 'bg-yellow-100 text-yellow-800 border-yellow-200';
        return 'bg-red-100 text-red-700 border-red-200';
    };

    const getLabel = (conf) => {
        if (conf >= 0.8) return 'High';
        if (conf >= 0.5) return 'Medium';
        return 'Low';
    };

    const confValue = confidence !== undefined && confidence !== null ? confidence : 0;

    return (
        <span className={`px-2 py-0.5 rounded-md text-xs font-medium border flex items-center gap-1.5 ${getColor(confValue)}`}>
            <Activity size={12} />
            {getLabel(confValue)}
            <span className="opacity-75 border-l border-current pl-1 ml-0.5">
                {(confValue * 100).toFixed(0)}%
            </span>
        </span>
    );
}
