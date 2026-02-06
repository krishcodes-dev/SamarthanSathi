import { AlertTriangle, AlertCircle, AlertOctagon, Info, CheckCircle } from 'lucide-react';

export default function UrgencyBadge({ level, score }) {
    const urgencyConfig = {
        'U1 - Critical': {
            bg: 'bg-red-100', text: 'text-red-700', border: 'border-red-200',
            label: 'U1 Critical', icon: AlertOctagon
        },
        'U2 - High': {
            bg: 'bg-orange-100', text: 'text-orange-700', border: 'border-orange-200',
            label: 'U2 High', icon: AlertTriangle
        },
        'U3 - Medium': {
            bg: 'bg-yellow-100', text: 'text-yellow-800', border: 'border-yellow-200',
            label: 'U3 Medium', icon: AlertCircle
        },
        'U4 - Low': {
            bg: 'bg-blue-100', text: 'text-blue-700', border: 'border-blue-200',
            label: 'U4 Low', icon: Info
        },
        'U5 - Minimal': {
            bg: 'bg-gray-100', text: 'text-gray-600', border: 'border-gray-200',
            label: 'U5 Minimal', icon: CheckCircle
        },
    };

    // Default fallback
    const config = urgencyConfig[level] || {
        bg: 'bg-gray-100', text: 'text-gray-600', border: 'border-gray-200',
        label: 'U?', icon: Info
    };

    const Icon = config.icon;

    return (
        <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md border ${config.bg} ${config.border} ${config.text} font-medium text-xs shadow-sm`}>
            <Icon size={14} className="stroke-2" />
            <span>{config.label}</span>
            {score !== undefined && (
                <span className="opacity-75 ml-0.5 border-l border-current pl-1.5 text-[10px] tracking-wide">
                    {score}
                </span>
            )}
        </div>
    );
}
