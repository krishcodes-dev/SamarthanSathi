import { useEffect } from 'react';
import ErrorBoundary from './components/ErrorBoundary';
import NotificationToast from './components/NotificationToast';
import RequestCard from './components/RequestCard';
import LoadingSkeleton from './components/LoadingSkeleton';
import LoadingSpinner from './components/LoadingSpinner';
import CreateRequestForm from './components/CreateRequestForm';
import EmptyState from './components/EmptyState';
import useStore from './store/useStore';

function App() {
  const {
    requests,
    fetchQueue,
    checkBackendHealth,
    loading,
    error,
    backendConnected
  } = useStore();

  // Initial load and health check
  useEffect(() => {
    const init = async () => {
      const isConnected = await checkBackendHealth();
      if (isConnected) {
        fetchQueue();
      }
    };
    init();

    // Auto-refresh every 30 seconds
    const interval = setInterval(() => {
      if (backendConnected) {
        fetchQueue();
      }
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-100">
        {/* Notification toasts */}
        <NotificationToast />

        {/* Header */}
        <header className="bg-white border-b border-gray-200 shadow-sm">
          <div className="max-w-7xl mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-gray-800">
                  🆘 SamarthanSathi
                </h1>
                <p className="text-sm text-gray-600">Crisis Dispatcher Dashboard</p>
              </div>

              {/* Connection status and refresh button */}
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full ${backendConnected ? 'bg-green-500' : 'bg-red-500'
                    }`}></div>
                  <span className="text-sm text-gray-600">
                    {backendConnected ? 'Connected' : 'Disconnected'}
                  </span>
                </div>

                <button
                  onClick={() => fetchQueue()}
                  disabled={loading.queue}
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
                >
                  {loading.queue ? '⟳ Refreshing...' : '🔄 Refresh Queue'}
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Main content */}
        <main className="max-w-7xl mx-auto px-4 py-6">
          {/* Create Request Form */}
          <div className="mb-6">
            <CreateRequestForm onSuccess={fetchQueue} />
          </div>

          {/* Backend disconnected warning */}
          {!backendConnected && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              <strong>⚠️ Backend Unreachable</strong>
              <p className="text-sm mt-1">
                Cannot connect to the backend server. Is it running on http://localhost:8000?
              </p>
            </div>
          )}

          {/* Queue error */}
          {error.queue && (
            <div className="bg-yellow-100 border border-yellow-400  text-yellow-700 px-4 py-3 rounded mb-4">
              <strong>Error loading queue:</strong> {error.queue}
            </div>
          )}

          {/* Loading state */}
          {loading.queue && requests.length === 0 && (
            <div>
              <LoadingSkeleton />
              <LoadingSkeleton />
              <LoadingSkeleton />
            </div>
          )}

          {/* Empty state */}
          {!loading.queue && requests.length === 0 && backendConnected && (
            <EmptyState
              icon="✅"
              title="All Clear!"
              message="No pending crisis requests in the queue."
              action={
                <button
                  onClick={() => fetchQueue()}
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  Refresh Queue
                </button>
              }
            />
          )}

          {/* Request queue */}
          {requests.length > 0 && (
            <div>
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-lg font-semibold text-gray-700">
                  Crisis Queue ({requests.length} requests)
                </h2>
                <p className="text-xs text-gray-500">
                  Sorted by urgency (highest first)
                </p>
              </div>

              <div className="space-y-0">
                {requests.map((request) => (
                  <RequestCard key={request.id} request={request} />
                ))}
              </div>
            </div>
          )}
        </main>

        {/* Footer */}
        <footer className="mt-8 py-4 text-center text-xs text-gray-500">
          Powered by explainable AI • Built with React + Zustand + Tailwind
        </footer>
      </div>
    </ErrorBoundary>
  );
}

export default App;
