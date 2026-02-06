import useStore from '../store/useStore';
import { CheckCircle, AlertCircle, Info, X } from 'lucide-react';
import { useEffect } from 'react';

export default function NotificationToast() {
    const { notifications, removeNotification } = useStore();

    if (notifications.length === 0) return null;

    return (
        <div className="fixed top-24 right-6 z-50 flex flex-col gap-3 pointer-events-none">
            {notifications.map(notif => (
                <ToastItem
                    key={notif.id}
                    notif={notif}
                    onClose={() => removeNotification(notif.id)}
                />
            ))}
        </div>
    );
}

function ToastItem({ notif, onClose }) {
    // Auto-dismiss logic handled in store usually, but we can add exit animation logic if needed

    const config = {
        success: {
            icon: CheckCircle,
            bg: 'bg-white',
            border: 'border-l-4 border-l-green-500',
            text: 'text-gray-800',
            iconColor: 'text-green-500'
        },
        error: {
            icon: AlertCircle,
            bg: 'bg-white',
            border: 'border-l-4 border-l-red-500',
            text: 'text-gray-800',
            iconColor: 'text-red-500'
        },
        info: {
            icon: Info,
            bg: 'bg-white',
            border: 'border-l-4 border-l-blue-500',
            text: 'text-gray-800',
            iconColor: 'text-blue-500'
        }
    };

    const style = config[notif.type] || config.info;
    const Icon = style.icon;

    return (
        <div className={`pointer-events-auto min-w-[320px] max-w-sm p-4 rounded-lg shadow-lg border border-gray-100 ${style.bg} ${style.border} flex items-start gap-3 animate-slide-in-right`}>
            <div className={`mt-0.5 ${style.iconColor}`}>
                <Icon size={20} />
            </div>
            <div className="flex-1">
                <p className={`text-sm font-medium ${style.text}`}>
                    {notif.message}
                </p>
            </div>
            <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600 transition-colors"
                aria-label="Close notification"
            >
                <X size={16} />
            </button>
        </div>
    );
}
