import React, { useState } from 'react';
import {
    Container, Typography, Box, Paper, TextField, Button,
    CircularProgress, Alert, Snackbar
} from '@mui/material';
import { useNavigate, useParams } from 'react-router-dom';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import SaveIcon from '@mui/icons-material/Save';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';

// Date picker imports
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { es } from 'date-fns/locale';

import apiClient from '../../services/api/client';

const EventFormPage: React.FC = () => {
    const { code } = useParams<{ code: string }>();
    const navigate = useNavigate();
    const queryClient = useQueryClient();

    const [form, setForm] = useState({
        activity_code: code || '',
        start_datetime: new Date(),
        end_datetime: new Date(new Date().getTime() + 60 * 60 * 1000), // Default 1 hour later
        waiting_time_minutes: 10,
        first_reminder_minutes: 1440,
        second_reminder_minutes: 60
    });

    const [snackbar, setSnackbar] = useState<{ open: boolean, message: string, severity: 'success' | 'error' }>({
        open: false, message: '', severity: 'success'
    });

    const mutation = useMutation({
        mutationFn: async (data: any) => {
            // Need to convert dates to ISO strings before sending to API
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

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();

        if (form.start_datetime >= form.end_datetime) {
            setSnackbar({ open: true, message: 'La fecha de fin debe ser posterior a la de inicio', severity: 'error' });
            return;
        }

        mutation.mutate(form);
    };

    return (
        <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={es}>
            <Container maxWidth="md">
                <Box sx={{ mb: 4, mt: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <Box>
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
                            Nuevo Evento
                        </Typography>
                    </Box>
                </Box>

                <Paper elevation={2} sx={{ p: 4, mb: 4 }}>
                    <form onSubmit={handleSubmit}>
                        <TextField
                            fullWidth
                            label="Código de la Actividad (Asociada)"
                            value={form.activity_code}
                            disabled
                            margin="normal"
                        />

                        <Box sx={{ display: 'flex', gap: 2, mt: 2, mb: 1 }}>
                            <Box sx={{ flex: 1 }}>
                                <DateTimePicker
                                    label="Fecha y Hora de Inicio"
                                    value={form.start_datetime}
                                    onChange={(newValue: Date | null) => {
                                        if (newValue) {
                                            setForm({ ...form, start_datetime: newValue });
                                        }
                                    }}
                                    sx={{ width: '100%' }}
                                />
                            </Box>
                            <Box sx={{ flex: 1 }}>
                                <DateTimePicker
                                    label="Fecha y Hora de Fin"
                                    value={form.end_datetime}
                                    onChange={(newValue: Date | null) => {
                                        if (newValue) {
                                            setForm({ ...form, end_datetime: newValue });
                                        }
                                    }}
                                    sx={{ width: '100%' }}
                                />
                            </Box>
                        </Box>

                        <TextField
                            fullWidth
                            type="number"
                            label="Minutos de Sala de Espera (antes del inicio)"
                            value={form.waiting_time_minutes}
                            onChange={(e) => setForm({ ...form, waiting_time_minutes: parseInt(e.target.value) || 0 })}
                            margin="normal"
                            required
                            helperText="¿Cuántos minutos antes del evento se abrirá la sala de espera?"
                        />

                        <TextField
                            fullWidth
                            type="number"
                            label="Primer Recordatorio (Minutos antes del evento)"
                            value={form.first_reminder_minutes}
                            onChange={(e) => setForm({ ...form, first_reminder_minutes: parseInt(e.target.value) || 0 })}
                            margin="normal"
                            required
                        />

                        <TextField
                            fullWidth
                            type="number"
                            label="Segundo Recordatorio (Minutos antes del evento)"
                            value={form.second_reminder_minutes}
                            onChange={(e) => setForm({ ...form, second_reminder_minutes: parseInt(e.target.value) || 0 })}
                            margin="normal"
                            required
                        />

                        <Button
                            type="submit"
                            variant="contained"
                            color="primary"
                            startIcon={<SaveIcon />}
                            disabled={mutation.isPending}
                            sx={{ mt: 4, width: '100%', py: 1.5 }}
                        >
                            {mutation.isPending ? 'Creando evento...' : 'Crear Evento'}
                        </Button>
                    </form>
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
