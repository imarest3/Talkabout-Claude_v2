import React, { useState, useMemo } from 'react';
import {
    Container, Typography, Box, Paper, TextField, Button,
    Alert, Snackbar, Tabs, Tab,
    FormGroup, FormControlLabel, Checkbox, Chip, Divider,
    Tooltip
} from '@mui/material';
import { useNavigate, useParams } from 'react-router-dom';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import SaveIcon from '@mui/icons-material/Save';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';

import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { TimePicker } from '@mui/x-date-pickers/TimePicker';
import { es } from 'date-fns/locale';
import { format, eachDayOfInterval, isAfter } from 'date-fns';
import { zonedTimeToUtc } from 'date-fns-tz';

import apiClient from '../../services/api/client';
import { useAuth } from '../../context/AuthContext';

// ─── Helpers ─────────────────────────────────────────────────────────────────

const WEEKDAYS = [
    { label: 'Lun', value: 0 },
    { label: 'Mar', value: 1 },
    { label: 'Mié', value: 2 },
    { label: 'Jue', value: 3 },
    { label: 'Vie', value: 4 },
    { label: 'Sáb', value: 5 },
    { label: 'Dom', value: 6 },
];

/**
 * date-fns getDay() returns 0=Sun … 6=Sat
 * Our WEEKDAYS use 0=Mon … 6=Sun (same as Python's weekday())
 * This converts date-fns day to our convention.
 */
function dateFnsDayToOur(day: number): number {
    return day === 0 ? 6 : day - 1;
}

function countBulkEvents(
    startDate: Date | null,
    endDate: Date | null,
    selectedWeekdays: number[],
    timeSlots: Date[]
): number {
    if (!startDate || !endDate || !isAfter(endDate, startDate) || timeSlots.length === 0) return 0;
    const days = eachDayOfInterval({ start: startDate, end: endDate });
    const filteredDays = selectedWeekdays.length === 0
        ? days
        : days.filter(d => selectedWeekdays.includes(dateFnsDayToOur(d.getDay())));
    const now = new Date();
    const futureDays = filteredDays.filter(d => isAfter(d, now) || d.toDateString() === now.toDateString());
    return futureDays.length * timeSlots.length;
}

// ─── Component ───────────────────────────────────────────────────────────────

const EventFormPage: React.FC = () => {
    const { code } = useParams<{ code: string }>();
    const navigate = useNavigate();
    const queryClient = useQueryClient();
    const { user } = useAuth();
    const userTimezone = user?.timezone || Intl.DateTimeFormat().resolvedOptions().timeZone;

    const [tab, setTab] = useState(0);
    const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({
        open: false, message: '', severity: 'success'
    });

    // ── Single event state ──────────────────────────────────────────────────
    const [single, setSingle] = useState({
        activity_code: code || '',
        start_datetime: new Date(),
        end_datetime: new Date(new Date().getTime() + 60 * 60 * 1000),
        waiting_time_minutes: 10,
        first_reminder_minutes: 1440,
        second_reminder_minutes: 60
    });

    // ── Bulk event state ────────────────────────────────────────────────────
    const [bulk, setBulk] = useState({
        startDate: null as Date | null,
        endDate: null as Date | null,
        selectedWeekdays: [] as number[],
        timeSlots: [] as Date[],
        newTimeSlot: null as Date | null,
        duration_minutes: 60,
        waiting_time_minutes: 10,
        first_reminder_minutes: 1440,
        second_reminder_minutes: 60
    });

    const estimatedCount = useMemo(() =>
        countBulkEvents(bulk.startDate, bulk.endDate, bulk.selectedWeekdays, bulk.timeSlots),
        [bulk.startDate, bulk.endDate, bulk.selectedWeekdays, bulk.timeSlots]
    );

    // ── Mutations ───────────────────────────────────────────────────────────
    const singleMutation = useMutation({
        mutationFn: async (data: typeof single) => {
            const payload = {
                ...data,
                start_datetime: data.start_datetime.toISOString(),
                end_datetime: data.end_datetime.toISOString(),
            };
            const response = await apiClient.post('/events/', payload);
            return response.data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['events', code] });
            navigate(`/activities/${code}`);
        },
        onError: (error: any) => {
            const message = error.response?.data?.detail || 'Ocurrió un error al guardar el evento';
            setSnackbar({ open: true, message, severity: 'error' });
        }
    });

    const bulkMutation = useMutation({
        mutationFn: async () => {
            // Convert picked times (treated as userTimezone) to UTC HH:MM for the backend
            const today = new Date();
            const hoursUtc = bulk.timeSlots.map(t => {
                const zonedDate = new Date(
                    today.getFullYear(), today.getMonth(), today.getDate(),
                    t.getHours(), t.getMinutes(), 0
                );
                const utcDate = zonedTimeToUtc(zonedDate, userTimezone);
                return format(utcDate, 'HH:mm');
            });
            const payload: Record<string, any> = {
                activity_code: code,
                start_date: format(bulk.startDate!, 'yyyy-MM-dd'),
                end_date: format(bulk.endDate!, 'yyyy-MM-dd'),
                hours_utc: hoursUtc,
                duration_minutes: bulk.duration_minutes,
                waiting_time_minutes: bulk.waiting_time_minutes,
                first_reminder_minutes: bulk.first_reminder_minutes,
                second_reminder_minutes: bulk.second_reminder_minutes,
            };
            if (bulk.selectedWeekdays.length > 0) {
                payload.weekdays = bulk.selectedWeekdays;
            }
            const response = await apiClient.post('/events/bulk-create/', payload);
            return response.data;
        },
        onSuccess: (data: any) => {
            queryClient.invalidateQueries({ queryKey: ['events', code] });
            const count = data?.created_count ?? data?.events?.length ?? '?';
            setSnackbar({ open: true, message: `¡${count} eventos creados correctamente!`, severity: 'success' });
            setTimeout(() => navigate(`/activities/${code}`), 1500);
        },
        onError: (error: any) => {
            const message = error.response?.data?.detail
                || error.response?.data?.non_field_errors?.[0]
                || 'Ocurrió un error al crear los eventos';
            setSnackbar({ open: true, message, severity: 'error' });
        }
    });

    // ── Handlers ────────────────────────────────────────────────────────────
    const handleSingleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (single.start_datetime >= single.end_datetime) {
            setSnackbar({ open: true, message: 'La fecha de fin debe ser posterior a la de inicio', severity: 'error' });
            return;
        }
        singleMutation.mutate(single);
    };

    const handleBulkSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!bulk.startDate || !bulk.endDate) {
            setSnackbar({ open: true, message: 'Selecciona las fechas de inicio y fin', severity: 'error' });
            return;
        }
        if (bulk.timeSlots.length === 0) {
            setSnackbar({ open: true, message: 'Añade al menos una hora para los eventos', severity: 'error' });
            return;
        }
        if (estimatedCount === 0) {
            setSnackbar({ open: true, message: 'El rango seleccionado no genera ningún evento futuro', severity: 'error' });
            return;
        }
        bulkMutation.mutate();
    };

    const toggleWeekday = (day: number) => {
        setBulk(prev => ({
            ...prev,
            selectedWeekdays: prev.selectedWeekdays.includes(day)
                ? prev.selectedWeekdays.filter(d => d !== day)
                : [...prev.selectedWeekdays, day].sort()
        }));
    };

    const addTimeSlot = () => {
        if (!bulk.newTimeSlot) return;
        const timeStr = format(bulk.newTimeSlot, 'HH:mm');
        if (bulk.timeSlots.some(t => format(t, 'HH:mm') === timeStr)) {
            setSnackbar({ open: true, message: 'Esa hora ya está añadida', severity: 'error' });
            return;
        }
        setBulk(prev => ({
            ...prev,
            timeSlots: [...prev.timeSlots, prev.newTimeSlot!].sort((a, b) => a.getTime() - b.getTime()),
            newTimeSlot: null
        }));
    };

    const removeTimeSlot = (index: number) => {
        setBulk(prev => ({ ...prev, timeSlots: prev.timeSlots.filter((_, i) => i !== index) }));
    };

    // ── Render ───────────────────────────────────────────────────────────────
    return (
        <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={es}>
            <Container maxWidth="md">
                <Box sx={{ mb: 4, mt: 2 }}>
                    <Button
                        startIcon={<ArrowBackIcon />}
                        onClick={() => navigate(`/activities/${code}`)}
                        sx={{ mb: 1 }}
                        color="inherit"
                        size="small"
                    >
                        Volver a la Actividad
                    </Button>
                    <Typography variant="h4" component="h1" fontWeight="bold" color="primary.main">
                        Crear Evento
                    </Typography>
                </Box>

                <Paper elevation={2} sx={{ mb: 4 }}>
                    <Tabs
                        value={tab}
                        onChange={(_, v) => setTab(v)}
                        sx={{ borderBottom: 1, borderColor: 'divider', px: 2 }}
                    >
                        <Tab label="Evento único" />
                        <Tab label="Creación masiva" />
                    </Tabs>

                    {/* ── TAB 0: Evento único ──────────────────────────────── */}
                    {tab === 0 && (
                        <Box sx={{ p: 4 }}>
                            <form onSubmit={handleSingleSubmit}>
                                <TextField
                                    fullWidth
                                    label="Actividad asociada"
                                    value={single.activity_code}
                                    disabled
                                    margin="normal"
                                />

                                <Box sx={{ display: 'flex', gap: 2, mt: 2, mb: 1 }}>
                                    <DateTimePicker
                                        label="Inicio"
                                        value={single.start_datetime}
                                        onChange={(v: Date | null) => v && setSingle({ ...single, start_datetime: v })}
                                        sx={{ flex: 1 }}
                                    />
                                    <DateTimePicker
                                        label="Fin"
                                        value={single.end_datetime}
                                        onChange={(v: Date | null) => v && setSingle({ ...single, end_datetime: v })}
                                        sx={{ flex: 1 }}
                                    />
                                </Box>

                                <TextField fullWidth type="number" margin="normal" required
                                    label="Minutos de sala de espera (antes del inicio)"
                                    value={single.waiting_time_minutes}
                                    onChange={e => setSingle({ ...single, waiting_time_minutes: parseInt(e.target.value) || 0 })}
                                    helperText="Cuántos minutos antes del evento se abrirá la sala de espera"
                                />
                                <TextField fullWidth type="number" margin="normal" required
                                    label="Primer recordatorio (min antes)"
                                    value={single.first_reminder_minutes}
                                    onChange={e => setSingle({ ...single, first_reminder_minutes: parseInt(e.target.value) || 0 })}
                                />
                                <TextField fullWidth type="number" margin="normal" required
                                    label="Segundo recordatorio (min antes)"
                                    value={single.second_reminder_minutes}
                                    onChange={e => setSingle({ ...single, second_reminder_minutes: parseInt(e.target.value) || 0 })}
                                />

                                <Button type="submit" variant="contained" color="primary" fullWidth
                                    startIcon={<SaveIcon />} disabled={singleMutation.isPending}
                                    sx={{ mt: 4, py: 1.5 }}
                                >
                                    {singleMutation.isPending ? 'Creando...' : 'Crear Evento'}
                                </Button>
                            </form>
                        </Box>
                    )}

                    {/* ── TAB 1: Creación masiva ───────────────────────────── */}
                    {tab === 1 && (
                        <Box sx={{ p: 4 }}>
                            <form onSubmit={handleBulkSubmit}>

                                {/* Rango de fechas */}
                                <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                                    Rango de fechas
                                </Typography>
                                <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
                                    <DatePicker
                                        label="Fecha de inicio"
                                        value={bulk.startDate}
                                        onChange={v => setBulk(prev => ({ ...prev, startDate: v }))}
                                        sx={{ flex: 1 }}
                                    />
                                    <DatePicker
                                        label="Fecha de fin"
                                        value={bulk.endDate}
                                        onChange={v => setBulk(prev => ({ ...prev, endDate: v }))}
                                        sx={{ flex: 1 }}
                                    />
                                </Box>

                                {/* Días de la semana */}
                                <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                                    Días de la semana
                                    <Typography component="span" variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                                        (sin selección = todos los días)
                                    </Typography>
                                </Typography>
                                <FormGroup row sx={{ mb: 3 }}>
                                    {WEEKDAYS.map(day => (
                                        <FormControlLabel
                                            key={day.value}
                                            control={
                                                <Checkbox
                                                    size="small"
                                                    checked={bulk.selectedWeekdays.includes(day.value)}
                                                    onChange={() => toggleWeekday(day.value)}
                                                />
                                            }
                                            label={day.label}
                                        />
                                    ))}
                                </FormGroup>

                                {/* Horas UTC */}
                                <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                                    Horas de inicio
                                    <Typography component="span" variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                                        (en tu zona horaria: {userTimezone})
                                    </Typography>
                                </Typography>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                                    <TimePicker
                                        label="Añadir hora"
                                        value={bulk.newTimeSlot}
                                        onChange={v => setBulk(prev => ({ ...prev, newTimeSlot: v }))}
                                        ampm={false}
                                        sx={{ flex: 1 }}
                                    />
                                    <Button
                                        variant="outlined"
                                        startIcon={<AddIcon />}
                                        onClick={addTimeSlot}
                                        disabled={!bulk.newTimeSlot}
                                        sx={{ height: 56 }}
                                    >
                                        Añadir
                                    </Button>
                                </Box>

                                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 3, minHeight: 36 }}>
                                    {bulk.timeSlots.length === 0
                                        ? <Typography variant="body2" color="text.secondary">Sin horas añadidas</Typography>
                                        : bulk.timeSlots.map((t, i) => (
                                            <Chip
                                                key={i}
                                                label={format(t, 'HH:mm')}
                                                onDelete={() => removeTimeSlot(i)}
                                                deleteIcon={
                                                    <Tooltip title="Eliminar">
                                                        <DeleteIcon fontSize="small" />
                                                    </Tooltip>
                                                }
                                                color="primary"
                                                variant="outlined"
                                            />
                                        ))
                                    }
                                </Box>

                                <Divider sx={{ mb: 3 }} />

                                {/* Configuración */}
                                <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                                    Configuración
                                </Typography>
                                <Box sx={{ display: 'flex', gap: 2 }}>
                                    <TextField type="number" label="Duración (min)" required
                                        value={bulk.duration_minutes} inputProps={{ min: 1 }}
                                        onChange={e => setBulk(prev => ({ ...prev, duration_minutes: parseInt(e.target.value) || 60 }))}
                                        sx={{ flex: 1 }}
                                    />
                                    <TextField type="number" label="Sala de espera (min antes)" required
                                        value={bulk.waiting_time_minutes} inputProps={{ min: 0 }}
                                        onChange={e => setBulk(prev => ({ ...prev, waiting_time_minutes: parseInt(e.target.value) || 0 }))}
                                        sx={{ flex: 1 }}
                                    />
                                </Box>
                                <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
                                    <TextField type="number" label="1er recordatorio (min antes)"
                                        value={bulk.first_reminder_minutes} inputProps={{ min: 1 }}
                                        onChange={e => setBulk(prev => ({ ...prev, first_reminder_minutes: parseInt(e.target.value) || 1440 }))}
                                        sx={{ flex: 1 }}
                                    />
                                    <TextField type="number" label="2do recordatorio (min antes)"
                                        value={bulk.second_reminder_minutes} inputProps={{ min: 1 }}
                                        onChange={e => setBulk(prev => ({ ...prev, second_reminder_minutes: parseInt(e.target.value) || 60 }))}
                                        sx={{ flex: 1 }}
                                    />
                                </Box>

                                {/* Preview */}
                                {(bulk.startDate && bulk.endDate && bulk.timeSlots.length > 0) && (
                                    <Alert
                                        severity={estimatedCount > 0 ? 'info' : 'warning'}
                                        sx={{ mt: 3 }}
                                    >
                                        {estimatedCount > 0
                                            ? <>Se crearán aproximadamente <strong>{estimatedCount} eventos</strong> futuros.</>
                                            : 'El rango seleccionado no genera ningún evento futuro.'}
                                    </Alert>
                                )}

                                <Button type="submit" variant="contained" color="primary" fullWidth
                                    startIcon={<SaveIcon />}
                                    disabled={bulkMutation.isPending || estimatedCount === 0}
                                    sx={{ mt: 3, py: 1.5 }}
                                >
                                    {bulkMutation.isPending
                                        ? 'Creando eventos...'
                                        : `Crear ${estimatedCount > 0 ? estimatedCount : ''} eventos`}
                                </Button>
                            </form>
                        </Box>
                    )}
                </Paper>

                <Snackbar
                    open={snackbar.open}
                    autoHideDuration={6000}
                    onClose={() => setSnackbar({ ...snackbar, open: false })}
                    anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
                >
                    <Alert onClose={() => setSnackbar({ ...snackbar, open: false })} severity={snackbar.severity} sx={{ width: '100%' }}>
                        {snackbar.message}
                    </Alert>
                </Snackbar>
            </Container>
        </LocalizationProvider>
    );
};

export default EventFormPage;
