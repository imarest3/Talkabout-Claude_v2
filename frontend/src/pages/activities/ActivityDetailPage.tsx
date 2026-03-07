import React from 'react';
import {
    Container, Typography, Box, Paper, Grid, Button,
    Skeleton, Divider, Chip, Alert, Accordion, AccordionSummary, AccordionDetails
} from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { formatInTimeZone } from 'date-fns-tz';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import AttachFileIcon from '@mui/icons-material/AttachFile';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import apiClient from '../../services/api/client';
import { Activity, Event } from '../../types';
import { useAuth } from '../../context/AuthContext';

// Extender tipo para manejar los files devueltos por la API
interface ActivityDetailed extends Activity {
    files?: Array<{ id: string; filename: string; file_url: string }>;
}

interface EventsResponse {
    results: Event[];
}

interface EnrollmentsResponse {
    results: Array<{ event: string; event_id: string; id: string; status: string }>;
}

const ActivityDetailPage: React.FC = () => {
    const { id: activityCode } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const queryClient = useQueryClient();
    const { user } = useAuth();

    // Obtener la zona horaria del usuario o defaults a local
    const userTimezone = user?.timezone || Intl.DateTimeFormat().resolvedOptions().timeZone;

    // Query 1: Detalles de la actividad
    const {
        data: activity,
        isLoading: isActivityLoading,
        isError: isActivityError
    } = useQuery({
        queryKey: ['activity', activityCode],
        queryFn: async () => {
            const response = await apiClient.get<ActivityDetailed>(`/activities/${activityCode}/`);
            return response.data;
        },
        enabled: !!activityCode
    });

    // Query 2: Eventos de esta actividad
    const {
        data: eventsData,
        isLoading: isEventsLoading
    } = useQuery({
        queryKey: ['events', activityCode],
        queryFn: async () => {
            const response = await apiClient.get<EventsResponse>('/events/', {
                params: { activity_code: activityCode }
            });
            return response.data;
        },
        enabled: !!activityCode
    });

    // Query 3: Inscripciones del usuario 
    const { data: myEnrollments } = useQuery({
        queryKey: ['my-enrollments'],
        queryFn: async () => {
            const response = await apiClient.get<EnrollmentsResponse>('/events/my-enrollments/');
            return response.data.results || [];
        }
    });

    // Mapear qué eventos está inscrito el usuario excluyendo cancelados
    const enrolledEventIds = new Set(
        myEnrollments
            ?.filter(e => e.status === 'enrolled')
            .map(e => e.event_id || e.event) || []
    );

    // Mutaciones
    const enrollMutation = useMutation({
        mutationFn: async (eventId: string) => {
            const response = await apiClient.post('/events/enroll/', { event_id: eventId });
            return response.data;
        },
        onSuccess: async () => {
            await Promise.all([
                queryClient.invalidateQueries({ queryKey: ['my-enrollments'] }),
                queryClient.invalidateQueries({ queryKey: ['events', activityCode] })
            ]);
        }
    });

    const unenrollMutation = useMutation({
        mutationFn: async (eventId: string) => {
            const response = await apiClient.post(`/events/${eventId}/unenroll/`, {
                event_id: eventId // Garantiza que no perdamos las headers de Axios
            });
            return response.data;
        },
        onSuccess: async () => {
            console.log('Unenroll exitoso - Invalidando Queries:', ['my-enrollments'], ['events', activityCode]);
            await Promise.all([
                queryClient.invalidateQueries({ queryKey: ['my-enrollments'] }),
                queryClient.invalidateQueries({ queryKey: ['events', activityCode] })
            ]);
        }
    });

    if (isActivityError) {
        return (
            <Container maxWidth="lg" sx={{ mt: 4 }}>
                <Alert severity="error">Error al cargar la actividad. Verifica que el código sea correcto.</Alert>
                <Button startIcon={<ArrowBackIcon />} onClick={() => navigate('/activities')} sx={{ mt: 2 }}>
                    Volver a actividades
                </Button>
            </Container>
        );
    }

    // Dividir eventos
    const now = new Date();
    const upcomingEvents = eventsData?.results.filter(e => new Date(e.end_datetime) >= now) || [];
    const pastEvents = eventsData?.results.filter(e => new Date(e.end_datetime) < now) || [];

    const renderEventList = (eventList: Event[], isPast: boolean) => (
        <Box display="flex" flexDirection="column" gap={2}>
            {eventList.map((event) => {
                const isEnrolled = enrolledEventIds.has(event.id);
                const isProcessing = enrollMutation.isPending || unenrollMutation.isPending;

                // Localizar fecha
                const localDate = formatInTimeZone(new Date(event.start_datetime), userTimezone, "EEEE, d 'de' MMMM yyyy");
                const localTimeStart = formatInTimeZone(new Date(event.start_datetime), userTimezone, "HH:mm");
                const localTimeEnd = formatInTimeZone(new Date(event.end_datetime), userTimezone, "HH:mm");

                return (
                    <Box
                        key={event.id}
                        sx={{
                            p: 2,
                            border: '1px solid',
                            borderColor: 'divider',
                            borderRadius: 1,
                            bgcolor: isPast ? (isEnrolled ? 'action.hover' : 'background.paper') : (isEnrolled ? 'action.hover' : 'background.paper'),
                            opacity: isPast ? 0.6 : 1
                        }}
                    >
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                            <Typography variant="subtitle2" fontWeight="bold" textTransform="capitalize">
                                {localDate}
                            </Typography>
                            {isPast && (
                                <Chip label="Finalizado" size="small" sx={{ height: 20, fontSize: '0.65rem' }} />
                            )}
                        </Box>

                        <Typography variant="body2" color="text.secondary" gutterBottom>
                            {localTimeStart} - {localTimeEnd}
                        </Typography>

                        {!isPast && (
                            <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 1 }}>
                                {isEnrolled && (event.status === 'in_waiting' || event.status === 'in_progress') && (
                                    <Button
                                        variant="contained"
                                        color="success"
                                        size="small"
                                        fullWidth
                                        onClick={() => navigate(`/events/${event.id}/waiting-room`)}
                                    >
                                        Ir a la Sala de Espera
                                    </Button>
                                )}

                                {isEnrolled ? (
                                    <Button
                                        variant="outlined"
                                        color="error"
                                        size="small"
                                        fullWidth
                                        disabled={isProcessing}
                                        onClick={() => unenrollMutation.mutate(event.id)}
                                    >
                                        Cancelar Inscripción
                                    </Button>
                                ) : (
                                    <Button
                                        variant="contained"
                                        color="primary"
                                        size="small"
                                        fullWidth
                                        disabled={isProcessing || event.status !== 'scheduled'}
                                        onClick={() => enrollMutation.mutate(event.id)}
                                    >
                                        {event.status === 'scheduled' ? 'Inscribirse' : 'Evento en curso'}
                                    </Button>
                                )}
                            </Box>
                        )}
                    </Box>
                );
            })}
        </Box>
    );

    return (
        <Container maxWidth="lg">
            <Box sx={{ mb: 4, mt: 2 }}>
                <Button
                    startIcon={<ArrowBackIcon />}
                    onClick={() => navigate('/activities')}
                    sx={{ mb: 2 }}
                    color="inherit"
                >
                    Volver
                </Button>

                {isActivityLoading ? (
                    <>
                        <Skeleton variant="text" height={60} width="60%" />
                        <Skeleton variant="text" width="30%" />
                    </>
                ) : activity && (
                    <>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1, gap: 2 }}>
                            <Typography variant="h4" component="h1" fontWeight="bold" color="primary.main">
                                {activity.title}
                            </Typography>
                            <Chip
                                label={activity.is_active ? 'Activa' : 'Inactiva'}
                                color={activity.is_active ? 'success' : 'default'}
                            />
                        </Box>
                        <Typography variant="subtitle1" color="text.secondary" gutterBottom>
                            Código: <strong>{activity.code}</strong> | Participantes máx por sala: {activity.max_participants_per_meeting}
                        </Typography>
                    </>
                )}
            </Box>

            <Grid container spacing={4}>
                {/* Columna Izquierda: Descripción y Archivos */}
                <Grid item xs={12} md={8}>
                    <Paper elevation={1} sx={{ p: 3, mb: 4 }}>
                        <Typography variant="h6" gutterBottom fontWeight="bold">
                            Descripción de la Actividad
                        </Typography>
                        <Divider sx={{ mb: 2 }} />
                        {isActivityLoading ? (
                            <Box>
                                <Skeleton variant="text" />
                                <Skeleton variant="text" />
                                <Skeleton variant="text" width="80%" />
                            </Box>
                        ) : (
                            <Box
                                className="activity-description"
                                dangerouslySetInnerHTML={{ __html: activity?.description || '' }}
                            />
                        )}
                    </Paper>

                    {!isActivityLoading && activity?.files && activity.files.length > 0 && (
                        <Paper elevation={1} sx={{ p: 3, mb: 4 }}>
                            <Typography variant="h6" gutterBottom fontWeight="bold">
                                Archivos Adjuntos
                            </Typography>
                            <Divider sx={{ mb: 2 }} />
                            <Box display="flex" flexDirection="column" gap={1}>
                                {activity.files.map((file) => (
                                    <Button
                                        key={file.id}
                                        href={file.file_url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        startIcon={<AttachFileIcon />}
                                        variant="outlined"
                                        sx={{ justifyContent: 'flex-start', textTransform: 'none' }}
                                    >
                                        {file.filename || 'Documento adjunto'}
                                    </Button>
                                ))}
                            </Box>
                        </Paper>
                    )}
                </Grid>

                {/* Columna Derecha: Eventos */}
                <Grid item xs={12} md={4}>
                    <Paper elevation={1} sx={{ p: 3, mb: 3 }}>
                        <Typography variant="h6" gutterBottom fontWeight="bold">
                            Próximos Eventos
                        </Typography>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                            Horarios mostrados en tu zona horaria ({userTimezone})
                        </Typography>
                        <Divider sx={{ mb: 2 }} />

                        {isEventsLoading ? (
                            <Box display="flex" flexDirection="column" gap={2}>
                                <Skeleton variant="rectangular" height={80} />
                                <Skeleton variant="rectangular" height={80} />
                            </Box>
                        ) : upcomingEvents.length === 0 ? (
                            <Typography variant="body2" color="text.secondary" align="center" sx={{ py: 3 }}>
                                No hay eventos próximos programados.
                            </Typography>
                        ) : (
                            renderEventList(upcomingEvents, false)
                        )}
                    </Paper>

                    {/* Eventos Pasados */}
                    {!isEventsLoading && pastEvents.length > 0 && (
                        <Accordion elevation={1}>
                            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                                <Typography variant="body1" fontWeight="medium">
                                    Ver eventos anteriores ({pastEvents.length})
                                </Typography>
                            </AccordionSummary>
                            <AccordionDetails sx={{ pt: 0, px: 2, pb: 2 }}>
                                {renderEventList(pastEvents, true)}
                            </AccordionDetails>
                        </Accordion>
                    )}
                </Grid>
            </Grid>
        </Container>
    );
};

export default ActivityDetailPage;
