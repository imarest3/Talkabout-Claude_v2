import React, { useState, useEffect } from 'react';
import {
    Container, Typography, Box, Paper, Grid, Button,
    CircularProgress, Alert, List, ListItem, ListItemAvatar,
    Avatar, ListItemText, Divider, Chip
} from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { formatInTimeZone } from 'date-fns-tz';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import VideocamIcon from '@mui/icons-material/Videocam';
import PersonIcon from '@mui/icons-material/Person';
import WifiOffIcon from '@mui/icons-material/WifiOff';
import SyncIcon from '@mui/icons-material/Sync';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';

import apiClient from '../../services/api/client';
import { useAuth } from '../../context/AuthContext';
import { useWaitingRoom } from '../../hooks/useWaitingRoom';
import { Event } from '../../types';

interface MyMeetingResponse {
    meeting_url: string;
    room_name: string;
}

const WaitingRoomPage: React.FC = () => {
    const { eventId } = useParams<{ eventId: string }>();
    const navigate = useNavigate();
    const { user } = useAuth();

    const [timeRemaining, setTimeRemaining] = useState<string>('');
    const [meetingError, setMeetingError] = useState<string | null>(null);

    const userTimezone = user?.timezone || Intl.DateTimeFormat().resolvedOptions().timeZone;

    // 1. Obtener detalles básicos del Evento para UI
    const { data: event, isLoading: isEventLoading } = useQuery({
        queryKey: ['event', eventId],
        queryFn: async () => {
            const response = await apiClient.get<Event>(`/events/${eventId}/`);
            return response.data;
        },
        enabled: !!eventId
    });

    // 2. Conectar al WebSocket
    const {
        participants,
        count,
        eventStatus,
        connectionStatus,
        error: wsError,
        reconnect
    } = useWaitingRoom(eventId);

    // 3. Cuando el backend ordene 'in_progress', buscar la Meeting URL
    const { data: meetingData, isFetching: isMeetingFetching, error: fetchMeetingError } = useQuery({
        queryKey: ['my-meeting', eventId],
        queryFn: async () => {
            try {
                const response = await apiClient.get<MyMeetingResponse>(`/events/${eventId}/my-meeting/`);
                setMeetingError(null);
                return response.data;
            } catch (err: any) {
                if (err.response?.status === 404) {
                    setMeetingError('No se te ha asignado a ningún grupo para esta sesión o se ha cancelado por falta de aforo.');
                } else {
                    setMeetingError('Ocurrió un error al buscar tu videollamada.');
                }
                throw err;
            }
        },
        // Solo llamar si el WS nos ha dicho que ya empezó o si por polling normal sabemos que el evento ya está en progreso
        enabled: !!eventId && (eventStatus === 'in_progress' || event?.status === 'in_progress'),
        retry: 1
    });

    // Contador regresivo
    useEffect(() => {
        if (!event || eventStatus === 'in_progress' || event.status === 'in_progress') {
            setTimeRemaining('');
            return;
        }

        const interval = setInterval(() => {
            const start = new Date(event.start_datetime).getTime();
            const now = new Date().getTime();
            const distance = start - now;

            if (distance < 0) {
                setTimeRemaining('Iniciando...');
                clearInterval(interval);
                return;
            }

            const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((distance % (1000 * 60)) / 1000);

            setTimeRemaining(`${minutes}m ${seconds}s`);
        }, 1000);

        return () => clearInterval(interval);
    }, [event, eventStatus]);

    // Auto-redirección
    useEffect(() => {
        if (meetingData?.meeting_url) {
            // Un pequeño timeout para que el usuario alcance a ver el mensaje de "Salas listas"
            const timer = setTimeout(() => {
                window.open(meetingData.meeting_url, '_blank', 'noopener,noreferrer');
            }, 1000);
            return () => clearTimeout(timer);
        }
    }, [meetingData?.meeting_url]);

    // Función auxiliar para botones
    const handleJoinMeeting = () => {
        if (meetingData?.meeting_url) {
            window.open(meetingData.meeting_url, '_blank', 'noopener,noreferrer');
        }
    };

    if (isEventLoading) {
        return (
            <Container maxWidth="md" sx={{ mt: 8, textAlign: 'center' }}>
                <CircularProgress />
                <Typography sx={{ mt: 2 }}>Cargando sala de espera...</Typography>
            </Container>
        );
    }

    if (!event) {
        return (
            <Container maxWidth="md" sx={{ mt: 4 }}>
                <Alert severity="error">No se encontró el evento solicitado.</Alert>
                <Button sx={{ mt: 2 }} startIcon={<ArrowBackIcon />} onClick={() => navigate('/activities')}>
                    Volver
                </Button>
            </Container>
        );
    }

    const isReadyToJoin = eventStatus === 'in_progress' || event.status === 'in_progress';
    const isEnded = eventStatus === 'completed' || eventStatus === 'cancelled' || event.status === 'completed' || event.status === 'cancelled';
    const hasMeetingUrl = !!meetingData?.meeting_url;

    const localTimeStart = formatInTimeZone(new Date(event.start_datetime), userTimezone, "HH:mm");

    return (
        <Container maxWidth="md">
            <Box sx={{ mb: 4, mt: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <Box>
                    <Button
                        startIcon={<ArrowBackIcon />}
                        onClick={() => navigate(`/activities/${event.activity_code}`)}
                        sx={{ mb: 1 }}
                        color="inherit"
                        size="small"
                    >
                        Volver a la Actividad
                    </Button>
                    <Typography variant="h4" component="h1" fontWeight="bold" color="primary.main">
                        Sala de Espera
                    </Typography>
                    <Typography variant="subtitle1" color="text.secondary">
                        {event.activity_title} - Hoy a las {localTimeStart}
                    </Typography>
                </Box>

                {/* Status Indicator */}
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {connectionStatus === 'connected' && <Chip icon={<CheckCircleOutlineIcon />} label="Conectado" color="success" size="small" variant="outlined" />}
                    {connectionStatus === 'connecting' && <Chip icon={<SyncIcon sx={{ animation: 'spin 2s linear infinite' }} />} label="Conectando..." color="warning" size="small" variant="outlined" />}
                    {connectionStatus === 'reconnecting' && <Chip icon={<SyncIcon />} label="Reconectando..." color="warning" size="small" variant="outlined" />}
                    {connectionStatus === 'disconnected' && (
                        <Chip
                            icon={<WifiOffIcon />}
                            label="Desconectado"
                            color="error"
                            size="small"
                            variant="outlined"
                            onClick={reconnect}
                            clickable
                        />
                    )}
                </Box>
            </Box>

            {wsError && (
                <Alert severity="error" sx={{ mb: 3 }} action={
                    <Button color="inherit" size="small" onClick={reconnect}>Reintentar</Button>
                }>
                    {wsError}
                </Alert>
            )}

            <Grid container spacing={3}>
                {/* Panel Principal */}
                <Grid item xs={12} md={8}>
                    <Paper
                        elevation={3}
                        sx={{
                            p: 4,
                            textAlign: 'center',
                            height: '100%',
                            display: 'flex',
                            flexDirection: 'column',
                            justifyContent: 'center',
                            alignItems: 'center',
                            bgcolor: isReadyToJoin ? 'success.50' : 'background.paper',
                            transition: 'background-color 0.5s ease',
                            border: isReadyToJoin ? 2 : 0,
                            borderColor: 'success.main'
                        }}
                    >
                        {isEnded ? (
                            <>
                                <Typography variant="h5" color="text.secondary" gutterBottom>
                                    El evento ha finalizado
                                </Typography>
                                <Typography variant="body1" paragraph>
                                    Es posible que no se haya alcanzado el número mínimo de participantes para formar grupos, o que la actividad haya sido cancelada.
                                </Typography>
                                <Button
                                    variant="outlined"
                                    onClick={() => navigate('/activities')}
                                    sx={{ mt: 2 }}
                                >
                                    Volver al inicio
                                </Button>
                            </>
                        ) : !isReadyToJoin ? (
                            <>
                                <Typography variant="h5" gutterBottom fontWeight="medium">
                                    El evento está a punto de comenzar
                                </Typography>
                                <Typography variant="body1" color="text.secondary" paragraph>
                                    No cierres esta pestaña. Te redirigiremos automáticamente a tu grupo cuando todos estén listos.
                                </Typography>

                                <Box sx={{ my: 4 }}>
                                    <Typography variant="overline" color="text.secondary">
                                        Tiempo restante
                                    </Typography>
                                    <Typography variant="h2" component="div" fontWeight="bold" color="primary">
                                        {timeRemaining || '0m 0s'}
                                    </Typography>
                                </Box>
                                <CircularProgress size={24} color="inherit" />
                            </>
                        ) : (
                            <>
                                <VideocamIcon sx={{ fontSize: 60, color: 'success.main', mb: 2 }} />
                                <Typography variant="h5" color="success.main" fontWeight="bold" gutterBottom>
                                    ¡Las salas están listas!
                                </Typography>

                                {isMeetingFetching ? (
                                    <Box sx={{ mt: 3, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                                        <CircularProgress size={30} sx={{ mb: 2 }} />
                                        <Typography>Buscando tu sala asignada...</Typography>
                                    </Box>
                                ) : hasMeetingUrl ? (
                                    <Box sx={{ mt: 3, width: '100%' }}>
                                        <Typography variant="body1" paragraph>
                                            El sistema te ha emparejado exitosamente. Haz clic abajo para entrar.
                                        </Typography>
                                        <Button
                                            variant="contained"
                                            color="success"
                                            size="large"
                                            fullWidth
                                            onClick={handleJoinMeeting}
                                            startIcon={<VideocamIcon />}
                                            sx={{ py: 1.5, fontSize: '1.1rem' }}
                                        >
                                            Entrar a la videollamada
                                        </Button>
                                    </Box>
                                ) : meetingError ? (
                                    <Alert severity="warning" sx={{ mt: 2, textAlign: 'left' }}>
                                        {meetingError}
                                    </Alert>
                                ) : (
                                    <Alert severity="error" sx={{ mt: 2 }}>
                                        No se pudo obtener el enlace a la sala. Inténtalo de nuevo más tarde.
                                    </Alert>
                                )}
                            </>
                        )}
                    </Paper>
                </Grid>

                {/* Panel lateral: Participantes */}
                <Grid item xs={12} md={4}>
                    <Paper elevation={1} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                        <Box sx={{ p: 2, bgcolor: 'primary.main', color: 'primary.contrastText', borderTopLeftRadius: 4, borderTopRightRadius: 4 }}>
                            <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <PersonIcon /> Participantes listos ({count})
                            </Typography>
                        </Box>

                        <List sx={{ flexGrow: 1, overflow: 'auto', maxHeight: 400 }}>
                            {participants.length === 0 ? (
                                <ListItem>
                                    <ListItemText
                                        primary="Aún no hay participantes"
                                        secondary="Serás el primero en la lista"
                                        sx={{ textAlign: 'center', color: 'text.secondary', my: 2 }}
                                    />
                                </ListItem>
                            ) : (
                                participants.map((participant, index) => (
                                    <React.Fragment key={participant.user_code || index}>
                                        <ListItem>
                                            <ListItemAvatar>
                                                <Avatar sx={{ bgcolor: 'secondary.main' }}>
                                                    {participant.user_code ? participant.user_code[0].toUpperCase() : 'U'}
                                                </Avatar>
                                            </ListItemAvatar>
                                            <ListItemText
                                                primary={participant.user_code || 'Usuario Anónimo'}
                                            />
                                        </ListItem>
                                        {index < participants.length - 1 && <Divider variant="inset" component="li" />}
                                    </React.Fragment>
                                ))
                            )}
                        </List>
                    </Paper>
                </Grid>
            </Grid>
        </Container>
    );
};

export default WaitingRoomPage;
