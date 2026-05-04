import React, { useState, useMemo } from 'react';
import {
    Container, Typography, Box, Paper, Grid, Button, Chip,
    List, ListItem, Divider, CircularProgress, Alert, Badge
} from '@mui/material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFnsV3';
import { DateCalendar } from '@mui/x-date-pickers/DateCalendar';
import { PickersDay, PickersDayProps } from '@mui/x-date-pickers/PickersDay';
import { es } from 'date-fns/locale';
import { format, startOfMonth, endOfMonth, isSameDay, parseISO } from 'date-fns';
import { formatInTimeZone } from 'date-fns-tz';
import { useNavigate } from 'react-router-dom';
import CalendarMonthIcon from '@mui/icons-material/CalendarMonth';
import VideocamIcon from '@mui/icons-material/Videocam';

import apiClient from '../../services/api/client';
import { useAuth } from '../../context/AuthContext';
import { Event } from '../../types';

interface EnrollmentsResponse {
    results: Array<{ event_id: string; id: string; status: string }>;
}

interface EventsResponse {
    results: Event[];
}

// ─── Custom day with event badge ─────────────────────────────────────────────

function EventDay(
    props: PickersDayProps<Date> & { eventDates?: Date[] }
) {
    const { eventDates = [], day, outsideCurrentMonth, ...other } = props;
    const hasEvent = !outsideCurrentMonth && eventDates.some(d => isSameDay(d, day));

    return (
        <Badge
            key={day.toString()}
            overlap="circular"
            badgeContent={hasEvent ? '•' : undefined}
            color="primary"
            sx={{ '& .MuiBadge-badge': { fontSize: 18, top: 6, right: 6, minWidth: 'unset', width: 8, height: 8, p: 0 } }}
        >
            <PickersDay {...other} outsideCurrentMonth={outsideCurrentMonth} day={day} />
        </Badge>
    );
}

// ─── Component ───────────────────────────────────────────────────────────────

const CalendarPage: React.FC = () => {
    const { user } = useAuth();
    const navigate = useNavigate();
    const queryClient = useQueryClient();
    const userTimezone = user?.timezone || Intl.DateTimeFormat().resolvedOptions().timeZone;

    const [selectedDate, setSelectedDate] = useState<Date>(new Date());
    const [visibleMonth, setVisibleMonth] = useState<Date>(new Date());

    // Fetch events for the visible month
    const { data: eventsData, isLoading } = useQuery({
        queryKey: ['calendar-events', format(visibleMonth, 'yyyy-MM')],
        queryFn: async () => {
            const start = startOfMonth(visibleMonth).toISOString();
            const end = endOfMonth(visibleMonth).toISOString();
            const response = await apiClient.get<EventsResponse>('/events/', {
                params: {
                    start_datetime: start,
                    end_datetime: end,
                    page_size: 200,
                    ordering: 'start_datetime'
                }
            });
            return response.data.results || [];
        }
    });

    // Fetch user's enrollments
    const { data: myEnrollments } = useQuery({
        queryKey: ['my-enrollments'],
        queryFn: async () => {
            const response = await apiClient.get<EnrollmentsResponse>('/events/my-enrollments/');
            return response.data.results || [];
        }
    });

    const enrolledEventIds = useMemo(() =>
        new Set(myEnrollments?.filter(e => e.status === 'enrolled').map(e => e.event_id) || []),
        [myEnrollments]
    );

    // Dates that have at least one event (for calendar badges)
    const eventDates = useMemo(() =>
        (eventsData || []).map(e => parseISO(e.start_datetime)),
        [eventsData]
    );

    // Events for the selected day
    const eventsForDay = useMemo(() =>
        (eventsData || []).filter(e => isSameDay(parseISO(e.start_datetime), selectedDate)),
        [eventsData, selectedDate]
    );

    // Mutations
    const enrollMutation = useMutation({
        mutationFn: async (eventId: string) => {
            const response = await apiClient.post('/events/enroll/', { event_id: eventId });
            return response.data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['my-enrollments'] });
            queryClient.invalidateQueries({ queryKey: ['calendar-events'] });
        }
    });

    const unenrollMutation = useMutation({
        mutationFn: async (eventId: string) => {
            await apiClient.post(`/events/${eventId}/unenroll/`, {});
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['my-enrollments'] });
            queryClient.invalidateQueries({ queryKey: ['calendar-events'] });
        }
    });

    const isProcessing = enrollMutation.isPending || unenrollMutation.isPending;

    return (
        <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={es}>
            <Container maxWidth="lg">
                <Box sx={{ mb: 4, mt: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                        <CalendarMonthIcon color="primary" />
                        <Typography variant="h4" component="h1" fontWeight="bold" color="primary.main">
                            Calendario de Eventos
                        </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                        Horarios en tu zona horaria: <strong>{userTimezone}</strong>
                    </Typography>
                </Box>

                <Grid container spacing={3}>
                    {/* ── Calendario ── */}
                    <Grid item xs={12} md={5}>
                        <Paper elevation={2} sx={{ p: 1 }}>
                            {isLoading && (
                                <Box sx={{ display: 'flex', justifyContent: 'center', py: 1 }}>
                                    <CircularProgress size={20} />
                                </Box>
                            )}
                            <DateCalendar
                                value={selectedDate}
                                onChange={(date) => date && setSelectedDate(date)}
                                onMonthChange={(month) => setVisibleMonth(month)}
                                slots={{ day: EventDay }}
                                slotProps={{
                                    day: { eventDates } as any
                                }}
                                sx={{ width: '100%', maxHeight: 'none' }}
                            />
                        </Paper>
                    </Grid>

                    {/* ── Eventos del día ── */}
                    <Grid item xs={12} md={7}>
                        <Paper elevation={2} sx={{ p: 3, minHeight: 300 }}>
                            <Typography variant="h6" fontWeight="bold" gutterBottom>
                                {format(selectedDate, "EEEE, d 'de' MMMM", { locale: es })}
                            </Typography>
                            <Divider sx={{ mb: 2 }} />

                            {eventsForDay.length === 0 ? (
                                <Box sx={{ textAlign: 'center', py: 6 }}>
                                    <CalendarMonthIcon sx={{ fontSize: 48, color: 'text.disabled', mb: 1 }} />
                                    <Typography variant="body1" color="text.secondary">
                                        No hay eventos programados para este día
                                    </Typography>
                                </Box>
                            ) : (
                                <List disablePadding>
                                    {eventsForDay.map((event, idx) => {
                                        const isEnrolled = enrolledEventIds.has(event.id);
                                        const isPast = new Date(event.end_datetime) < new Date();
                                        const isActive = event.status === 'in_waiting' || event.status === 'in_progress';
                                        const isFull = event.enrolled_count != null &&
                                            (event as any).max_participants != null &&
                                            event.enrolled_count >= (event as any).max_participants;

                                        const localStart = formatInTimeZone(
                                            parseISO(event.start_datetime), userTimezone, 'HH:mm'
                                        );
                                        const localEnd = formatInTimeZone(
                                            parseISO(event.end_datetime), userTimezone, 'HH:mm'
                                        );

                                        return (
                                            <React.Fragment key={event.id}>
                                                {idx > 0 && <Divider sx={{ my: 1 }} />}
                                                <ListItem
                                                    disablePadding
                                                    sx={{
                                                        py: 1.5,
                                                        flexDirection: 'column',
                                                        alignItems: 'flex-start'
                                                    }}
                                                >
                                                    {/* Header row */}
                                                    <Box sx={{ display: 'flex', justifyContent: 'space-between', width: '100%', mb: 0.5 }}>
                                                        <Typography variant="subtitle2" fontWeight="bold">
                                                            {localStart} – {localEnd}
                                                        </Typography>
                                                        <Box sx={{ display: 'flex', gap: 0.5 }}>
                                                            {isPast && <Chip label="Finalizado" size="small" />}
                                                            {!isPast && isEnrolled && <Chip label="Inscrito" size="small" color="success" />}
                                                            {!isPast && isActive && <Chip label="En curso" size="small" color="warning" />}
                                                        </Box>
                                                    </Box>

                                                    {/* Activity name */}
                                                    <Typography
                                                        variant="body2"
                                                        color="primary"
                                                        sx={{ cursor: 'pointer', '&:hover': { textDecoration: 'underline' }, mb: 1 }}
                                                        onClick={() => navigate(`/activities/${event.activity_code}`)}
                                                    >
                                                        {event.activity_title}
                                                    </Typography>

                                                    {/* Actions */}
                                                    {!isPast && (
                                                        <Box sx={{ display: 'flex', gap: 1 }}>
                                                            {isEnrolled && isActive && (
                                                                <Button
                                                                    size="small"
                                                                    variant="contained"
                                                                    color="success"
                                                                    startIcon={<VideocamIcon />}
                                                                    onClick={() => navigate(`/events/${event.id}/waiting-room`)}
                                                                >
                                                                    Sala de espera
                                                                </Button>
                                                            )}
                                                            {isEnrolled && !isActive && (
                                                                <Button
                                                                    size="small"
                                                                    variant="outlined"
                                                                    color="success"
                                                                    onClick={() => navigate(`/events/${event.id}/waiting-room`)}
                                                                >
                                                                    Ver sala de espera
                                                                </Button>
                                                            )}
                                                            {isEnrolled ? (
                                                                <Button
                                                                    size="small"
                                                                    variant="outlined"
                                                                    color="error"
                                                                    disabled={isProcessing || isActive}
                                                                    onClick={() => unenrollMutation.mutate(event.id)}
                                                                >
                                                                    Cancelar inscripción
                                                                </Button>
                                                            ) : (
                                                                <Button
                                                                    size="small"
                                                                    variant="contained"
                                                                    color="primary"
                                                                    disabled={isProcessing || event.status !== 'scheduled' || isFull}
                                                                    onClick={() => enrollMutation.mutate(event.id)}
                                                                >
                                                                    {isFull ? 'Sin cupos' : 'Inscribirse'}
                                                                </Button>
                                                            )}
                                                        </Box>
                                                    )}
                                                </ListItem>
                                            </React.Fragment>
                                        );
                                    })}
                                </List>
                            )}

                            {(enrollMutation.isError || unenrollMutation.isError) && (
                                <Alert severity="error" sx={{ mt: 2 }}>
                                    No se pudo completar la acción. Inténtalo de nuevo.
                                </Alert>
                            )}
                        </Paper>
                    </Grid>
                </Grid>
            </Container>
        </LocalizationProvider>
    );
};

export default CalendarPage;
