import { useEffect, useState } from 'react';
import ErrorBoundary from '../components/ErrorBoundary';
import NotificationToast from '../components/NotificationToast';
import RequestCard from '../components/RequestCard';
import LoadingSkeleton from '../components/LoadingSkeleton';
import LoadingSpinner from '../components/LoadingSpinner';
import CreateRequestForm from '../components/CreateRequestForm';
import EmptyState from '../components/EmptyState';
import useStore from '../store/useStore';
import { ArrowLeft, Info, AlertTriangle } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function Dashboard() {
    const {
        requests,
        fetchQueue,
        checkBackendHealth,
        loading,
        error,
        backendConnected
    } = useStore();

    const [showDemoForm, setShowDemoForm] = useState(false);

    // Initial load and health check
    useEffect(() => {
        const init = async () => {
            const isConnected = await checkBackendHealth();
            if (isConnected) {
                fetchQueue();
            }
        };
        init();
    }, []);

    return (
        <ErrorBoundary>
            <div className="min-h-screen bg-gray-50">
                {/* Notification toasts */}
                <NotificationToast />

                {/* Header */}
                <header className="bg-white border-b border-gray-200 sticky top-0 z-40">
                    <div className="max-w-7xl mx-auto px-4 py-4">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-4">
                                <Link to="/" className="text-gray-500 hover:text-gray-900 transition-colors">
                                    <ArrowLeft size={20} />
                                </Link>
                                <div>
                                    <h1 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                                        SamarthanSathi <span className="text-xs px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full">LIVE</span>
                                    </h1>
                                    <p className="text-sm text-gray-500">Crisis Dispatcher Dashboard</p>
                                </div>
                            </div>

                            {/* Connection status and refresh button */}
                            <div className="flex items-center gap-3">
                                <div className="hidden md:flex items-center gap-2 mr-2">
                                    <div className={`w-2 h-2 rounded-full ${backendConnected ? 'bg-green-500' : 'bg-red-500'
                                        }`}></div>
                                    <span className="text-xs text-gray-500 font-medium">
                                        {backendConnected ? 'SYSTEM ONLINE' : 'OFFLINE'}
                                    </span>
                                </div>

                                <button
                                    onClick={() => setShowDemoForm(true)}
                                    className="px-3 py-1.5 bg-white text-gray-700 rounded-md hover:bg-gray-50 border border-gray-200 text-sm font-medium transition-colors"
                                >
                                    Simulate Request
                                </button>

                                <button
                                    onClick={() => fetchQueue()}
                                    disabled={loading.queue}
                                    className="px-3 py-1.5 bg-gray-900 text-white rounded-md hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium transition-all active:scale-95 shadow-sm"
                                >
                                    {loading.queue ? 'Syncing...' : 'Refresh'}
                                </button>
                            </div>
                        </div>
                    </div>
                </header>

                {/* Main content */}
                <main className="max-w-5xl mx-auto px-4 py-8">

                    {/* Demo Mode: Simulation Modal */}
                    {showDemoForm && (
                        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
                            <div className="bg-white rounded-xl shadow-2xl p-6 max-w-lg w-full max-h-[90vh] overflow-y-auto border border-gray-200">
                                <div className="flex justify-between items-center mb-6">
                                    <h2 className="text-lg font-bold text-gray-900">Simulate Incoming Request</h2>
                                    <button
                                        onClick={() => setShowDemoForm(false)}
                                        className="text-gray-400 hover:text-gray-600"
                                    >
                                        ✕
                                    </button>
                                </div>
                                <div className="bg-blue-50 border border-blue-100 p-4 rounded-lg mb-6 text-sm text-blue-800 flex items-start gap-2">
                                    <Info size={18} className="mt-0.5 shrink-0" />
                                    <span>This tool simulates a citizen submitting an SOS via the public app.</span>
                                </div>
                                <CreateRequestForm onSuccess={() => {
                                    setShowDemoForm(false);
                                    fetchQueue();
                                }} />
                            </div>
                        </div>
                    )}

                    {/* Backend disconnected warning */}
                    {!backendConnected && (
                        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6 text-sm flex items-center gap-2">
                            <AlertTriangle size={18} />
                            <span><strong>Backend Unreachable</strong> • Cannot connect to server on localhost:8000</span>
                        </div>
                    )}

                    {/* Queue error */}
                    {error.queue && (
                        <div className="bg-orange-50 border border-orange-200 text-orange-800 px-4 py-3 rounded-lg mb-6 text-sm">
                            <strong>Error loading queue:</strong> {error.queue}
                        </div>
                    )}

                    {/* Loading state */}
                    {loading.queue && requests.length === 0 && (
                        <div className="space-y-4">
                            <LoadingSkeleton />
                            <LoadingSkeleton />
                            <LoadingSkeleton />
                        </div>
                    )}

                    {/* Empty state */}
                    {!loading.queue && requests.length === 0 && backendConnected && (
                        <EmptyState
                            title="All Clear"
                            message="No pending crisis requests in the queue. System is standing by."
                            action={
                                <button
                                    onClick={() => fetchQueue()}
                                    className="mt-4 px-4 py-2 bg-gray-900 text-white rounded-md hover:bg-gray-800 text-sm"
                                >
                                    Check for new requests
                                </button>
                            }
                        />
                    )}

                    {/* Request queue */}
                    {requests.length > 0 && (
                        <div>
                            <div className="mb-4 flex items-center justify-between">
                                <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">
                                    Active Crisis Queue ({requests.length})
                                </h2>
                                <div className="flex items-center gap-2">
                                    <span className="text-xs text-gray-400">
                                        Sorted by urgency
                                    </span>
                                </div>
                            </div>

                            <div className="space-y-3">
                                {requests.map((request) => (
                                    <RequestCard key={request.id} request={request} />
                                ))}
                            </div>
                        </div>
                    )}
                </main>

                {/* Footer */}
                <footer className="py-8 text-center text-xs text-gray-400">
                    <p>SamarthanSathi • AI-Powered Crisis Response System</p>
                </footer>
            </div>
        </ErrorBoundary>
    );
}
