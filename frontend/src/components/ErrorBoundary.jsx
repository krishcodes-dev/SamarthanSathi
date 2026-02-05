import React from 'react';

class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }

    componentDidCatch(error, errorInfo) {
        console.error('ErrorBoundary caught:', error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="p-4 bg-red-50 border border-red-200 rounded">
                    <h2 className="text-red-800 font-bold text-lg mb-2">Something went wrong</h2>
                    <p className="text-red-600 text-sm mb-4">
                        {this.state.error?.message || 'Unknown error occurred'}
                    </p>
                    <button
                        onClick={() => window.location.reload()}
                        className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
                    >
                        Reload Dashboard
                    </button>
                </div>
            );
        }
        return this.props.children;
    }
}

export default ErrorBoundary;
