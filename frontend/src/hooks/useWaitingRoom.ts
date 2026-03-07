import { useState, useEffect, useRef, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';

interface Participant {
    id: string; // Puede ser el user_id o el channel_name del WS
    user_code?: string;
    alias?: string;
    is_ready?: boolean;
}

interface WaitingRoomState {
    participants: Participant[];
    count: number;
    eventStatus: 'scheduled' | 'in_waiting' | 'in_progress' | 'completed' | 'cancelled';
    connectionStatus: 'connecting' | 'connected' | 'reconnecting' | 'disconnected';
    error: string | null;
}

const WS_BASE_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws';

export const useWaitingRoom = (eventId: string | undefined) => {
    const { user } = useAuth();

    const [state, setState] = useState<WaitingRoomState>({
        participants: [],
        count: 0,
        eventStatus: 'scheduled',
        connectionStatus: 'disconnected',
        error: null
    });

    const wsRef = useRef<WebSocket | null>(null);
    const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
    const pingIntervalRef = useRef<NodeJS.Timeout | null>(null);
    const reconnectAttemptsRef = useRef(0);
    const maxReconnectAttempts = 5;

    const connect = useCallback(() => {
        if (!eventId || !user) return;

        setState(prev => ({ ...prev, connectionStatus: reconnectAttemptsRef.current > 0 ? 'reconnecting' : 'connecting', error: null }));

        // Obtener el token de acceso para la autenticación en el WebSocket
        // Dependiendo de la implementación de tu backend (si usa django-channels-jwt-auth_middleware), 
        // podrías necesitar enviarlo en la URL, subprotocol, o el primer mensaje.
        // Asumiendo envío por query_param para este ejemplo genérico reconociendo el interceptor
        const token = localStorage.getItem('access_token');
        const wsUrl = `${WS_BASE_URL}/waiting-room/${eventId}/?token=${token}`;

        try {
            const ws = new WebSocket(wsUrl);
            wsRef.current = ws;

            ws.onopen = () => {
                console.log('WebSocket connected');
                setState(prev => ({ ...prev, connectionStatus: 'connected', error: null }));
                reconnectAttemptsRef.current = 0;

                // Enviar mensaje de que el usuario está listo si es requerido por tu backend
                ws.send(JSON.stringify({ type: 'ready' }));

                // Configurar el Ping cada 30 segundos
                pingIntervalRef.current = setInterval(() => {
                    if (ws.readyState === WebSocket.OPEN) {
                        ws.send(JSON.stringify({ type: 'ping' }));
                    }
                }, 30000);
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);

                    switch (data.type) {
                        case 'participant_list':
                            setState(prev => ({
                                ...prev,
                                participants: data.participants || [],
                                count: data.count || 0
                            }));
                            break;

                        case 'event_status':
                            setState(prev => ({
                                ...prev,
                                eventStatus: data.status
                            }));
                            break;

                        case 'pong':
                            // Opcional: manejar latencia
                            break;

                        case 'error':
                            setState(prev => ({ ...prev, error: data.message }));
                            break;
                    }
                } catch (e) {
                    console.error('Error parsing WebSocket message:', e);
                }
            };

            ws.onclose = (event) => {
                console.log(`WebSocket disconnected. Code: ${event.code}, Reason: ${event.reason}`);

                // Limpiar intervalos
                if (pingIntervalRef.current) {
                    clearInterval(pingIntervalRef.current);
                    pingIntervalRef.current = null;
                }

                // Lógica de reconexión
                if (reconnectAttemptsRef.current < maxReconnectAttempts) {
                    setState(prev => ({ ...prev, connectionStatus: 'reconnecting' }));
                    const timeout = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 10000); // Exponential backoff max 10s

                    reconnectTimeoutRef.current = setTimeout(() => {
                        reconnectAttemptsRef.current += 1;
                        connect();
                    }, timeout);
                } else {
                    setState(prev => ({
                        ...prev,
                        connectionStatus: 'disconnected',
                        error: 'Conexión perdida. Por favor, recarga la página.'
                    }));
                }
            };

            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                // The onclose event will fire immediately after onerror in most implementations.
            };

        } catch (err) {
            console.error('Failed to create WebSocket:', err);
            setState(prev => ({ ...prev, connectionStatus: 'disconnected', error: 'Fallo al inicializar conexión' }));
        }
    }, [eventId, user]);

    // Limpieza y Setup inicial
    useEffect(() => {
        connect();

        return () => {
            if (pingIntervalRef.current) clearInterval(pingIntervalRef.current);
            if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);

            if (wsRef.current) {
                // Cerrar de forma limpia (1000 Normal Closure)
                wsRef.current.close(1000, 'Component unmounted');
                wsRef.current = null;
            }
        };
    }, [connect]);

    // Método expuesto por si se necesita forzar envío de acción
    const sendMessage = useCallback((type: string, payload: any = {}) => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({ type, ...payload }));
            return true;
        }
        return false;
    }, []);

    return {
        ...state,
        sendMessage,
        reconnect: () => {
            reconnectAttemptsRef.current = 0;
            connect();
        }
    };
};
