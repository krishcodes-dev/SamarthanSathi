import useStore from '../store/useStore';

export default function NotificationToast() {
    const { notifications, removeNotification } = useStore();

    return (
        <div className="fixed top-4 right-4 z-50 space-y-2">
            {notifications.map(notif => (
                <div
                    key={notif.id}
                    className={`p-4 rounded shadow-lg animate-slide-in ${notif.type === 'success' ? 'bg-green-500' :
                            notif.type === 'error' ? 'bg-red-500' : 'bg-blue-500'
                        } text-white flex items-center justify-between min-w-[300px]`}
                >
                    <span>{notif.message}</span>
                    <button
                        onClick={() => removeNotification(notif.id)}
                        className="ml-4 text-white hover:text-gray-200"
                    >
                        ✕
                    </button>
                </div>
            ))}
        </div>
    );
}
