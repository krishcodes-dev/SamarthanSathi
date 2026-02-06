import { create } from 'zustand';
import api from '../api/client';
import { playAlertSound } from '../utils/SoundManager';

const useStore = create((set, get) => ({
    // ===== STATE =====
    requests: [],
    selectedRequestId: null,
    resourceMatches: {},  // { requestId: [match1, match2, ...] }

    loading: {
        queue: false,
        matches: {},    // { requestId: boolean }
        dispatch: {}    // { requestId: boolean }
    },

    error: {
        queue: null,
        matches: {},    // { requestId: string }
        dispatch: {}    // { requestId: string }
    },

    notifications: [],  // { id, type: 'success'|'error'|'info', message }
    backendConnected: false,

    // ===== COMPUTED VALUES =====
    getSelectedRequest: () => {
        const { requests, selectedRequestId } = get();
        return requests.find(r => r.id === selectedRequestId);
    },

    // ===== ACTIONS =====

    fetchQueue: async (limit = 50) => {
        set(state => ({
            loading: { ...state.loading, queue: true },
            error: { ...state.error, queue: null }
        }));

        try {
            const previousRequests = get().requests;
            const data = await api.getQueue(limit);

            // Alerting Logic: Check for new requests
            if (previousRequests.length > 0 && data.length > 0) {
                const prevIds = new Set(previousRequests.map(r => r.id));
                const newRequests = data.filter(r => !prevIds.has(r.id));

                if (newRequests.length > 0) {
                    // 1. Play Sound
                    playAlertSound('default');

                    // 2. Flash Title
                    document.title = `(${newRequests.length}) New Crisis! | SamarthanSathi`;
                    setTimeout(() => { document.title = "SamarthanSathi - Dispatch"; }, 4000);

                    // 3. Toast
                    newRequests.forEach(req => {
                        // Truncate text for the toast
                        const text = req.raw_text.length > 40
                            ? req.raw_text.slice(0, 40) + '...'
                            : req.raw_text;

                        get().addNotification('info', `New Report: ${text}`);
                    });
                }
            }

            set({ requests: data });
        } catch (err) {
            set(state => ({
                error: { ...state.error, queue: err.message }
            }));
        } finally {
            set(state => ({
                loading: { ...state.loading, queue: false }
            }));
        }
    },

    selectRequest: (id) => {
        set({ selectedRequestId: id });
        // Auto-fetch matches when selecting
        if (id && !get().resourceMatches[id]) {
            get().fetchMatches(id);
        }
    },

    fetchMatches: async (requestId) => {
        set(state => ({
            loading: {
                ...state.loading,
                matches: { ...state.loading.matches, [requestId]: true }
            },
            error: {
                ...state.error,
                matches: { ...state.error.matches, [requestId]: null }
            }
        }));

        try {
            const data = await api.getResourceMatches(requestId);
            set(state => ({
                resourceMatches: { ...state.resourceMatches, [requestId]: data }
            }));
        } catch (err) {
            set(state => ({
                error: {
                    ...state.error,
                    matches: { ...state.error.matches, [requestId]: err.message }
                }
            }));
        } finally {
            set(state => ({
                loading: {
                    ...state.loading,
                    matches: { ...state.loading.matches, [requestId]: false }
                }
            }));
        }
    },

    dispatchResource: async (requestId, resourceId, quantity) => {
        set(state => ({
            loading: {
                ...state.loading,
                dispatch: { ...state.loading.dispatch, [requestId]: true }
            },
            error: {
                ...state.error,
                dispatch: { ...state.error.dispatch, [requestId]: null }
            }
        }));

        try {
            await api.dispatchResource(requestId, resourceId, quantity);

            // Success: Add notification (Clean message, icon handled by component)
            get().addNotification('success', `Dispatched ${quantity} units successfully`);

            // Update request status in local state
            set(state => ({
                requests: state.requests.map(r =>
                    r.id === requestId
                        ? { ...r, status: 'in_progress' }
                        : r
                )
            }));

            // Re-fetch queue to get latest data
            setTimeout(() => get().fetchQueue(), 1000);

        } catch (err) {
            set(state => ({
                error: {
                    ...state.error,
                    dispatch: { ...state.error.dispatch, [requestId]: err.message }
                }
            }));
            get().addNotification('error', `Dispatch failed: ${err.message}`);
        } finally {
            set(state => ({
                loading: {
                    ...state.loading,
                    dispatch: { ...state.loading.dispatch, [requestId]: false }
                }
            }));
        }
    },

    addNotification: (type, message) => {
        const id = Date.now();
        set(state => ({
            notifications: [...state.notifications, { id, type, message }]
        }));

        setTimeout(() => {
            set(state => ({
                notifications: state.notifications.filter(n => n.id !== id)
            }));
        }, 5000);
    },

    removeNotification: (id) => {
        set(state => ({
            notifications: state.notifications.filter(n => n.id !== id)
        }));
    },

    checkBackendHealth: async () => {
        try {
            await api.healthCheck();
            set({ backendConnected: true });
            return true;
        } catch (err) {
            set({ backendConnected: false });
            return false;
        }
    }
}));

export default useStore;
