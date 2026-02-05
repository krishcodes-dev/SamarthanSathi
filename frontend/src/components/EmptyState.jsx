export default function EmptyState({
    icon = '📭',
    title = 'No requests found',
    message = 'The queue is empty.',
    action = null
}) {
    return (
        <div className="flex flex-col items-center justify-center p-12 bg-gray-50 rounded-lg">
            <div className="text-6xl mb-4">{icon}</div>
            <h3 className="text-xl font-semibold text-gray-700 mb-2">{title}</h3>
            <p className="text-gray-500 mb-6">{message}</p>
            {action}
        </div>
    );
}
