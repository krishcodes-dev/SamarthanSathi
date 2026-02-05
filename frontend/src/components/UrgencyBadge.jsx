export default function UrgencyBadge({ level, score }) {
    const urgencyConfig = {
        'U1 - Critical': { bg: 'bg-urgency-u1', text: 'text-white', label: 'U1' },
        'U2 - High': { bg: 'bg-urgency-u2', text: 'text-white', label: 'U2' },
        'U3 - Medium': { bg: 'bg-urgency-u3', text: 'text-gray-900', label: 'U3' },
        'U4 - Low': { bg: 'bg-urgency-u4', text: 'text-white', label: 'U4' },
        'U5 - Minimal': { bg: 'bg-urgency-u5', text: 'text-white', label: 'U5' },
    };

    // Extract U1, U2, etc. from level if it exists
    const config = urgencyConfig[level] || { bg: 'bg-gray-500', text: 'text-white', label: 'U?' };

    return (
        <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full ${config.bg} ${config.text} font-semibold text-sm`}>
            <span>{config.label}</span>
            {score !== undefined && (
                <span className="text-xs opacity-90">({score})</span>
            )}
        </div>
    );
}
