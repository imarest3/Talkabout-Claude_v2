import React, { useState, useEffect } from 'react';
import {
    Container, Typography, Box, Paper, TextField, Button,
    FormControlLabel, Checkbox, CircularProgress, Alert, Snackbar
} from '@mui/material';
import { useNavigate, useParams } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import SaveIcon from '@mui/icons-material/Save';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';

import apiClient from '../../services/api/client';
import { Activity } from '../../types';

const ActivityFormPage: React.FC = () => {
    const { code } = useParams<{ code: string }>();
    const isEditing = !!code;
    const navigate = useNavigate();
    const queryClient = useQueryClient();

    const [form, setForm] = useState({
        code: '',
        title: '',
        description: '',
        max_participants_per_meeting: 6,
        is_active: true
    });

    const [snackbar, setSnackbar] = useState<{ open: boolean, message: string, severity: 'success' | 'error' }>({
        open: false, message: '', severity: 'success'
    });

    // Fetch activity data if editing
    const { data: activity, isLoading: isFetching } = useQuery({
        queryKey: ['activity', code],
        queryFn: async () => {
            const response = await apiClient.get<Activity>(`/activities/${code}/`);
            return response.data;
        },
        enabled: isEditing
    });

    useEffect(() => {
        if (activity && isEditing) {
            setForm({
                code: activity.code,
                title: activity.title,
                description: activity.description,
                max_participants_per_meeting: activity.max_participants_per_meeting,
                is_active: activity.is_active
            });
        }
    }, [activity, isEditing]);

    const mutation = useMutation({
        mutationFn: async (data: typeof form) => {
            if (isEditing) {
                const response = await apiClient.patch(`/activities/${code}/update/`, data);
                return response.data;
            } else {
                const response = await apiClient.post('/activities/create/', data);
                return response.data;
            }
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['activities'] });
            if (isEditing) {
                queryClient.invalidateQueries({ queryKey: ['activity', code] });
            }
            navigate('/activities');
        },
        onError: (error: any) => {
            const message = error.response?.data?.detail || error.response?.data?.code?.[0] || 'Ocurrió un error al guardar';
            setSnackbar({ open: true, message, severity: 'error' });
        }
    });

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        mutation.mutate(form);
    };

    if (isEditing && isFetching) {
        return (
            <Container sx={{ display: 'flex', justifyContent: 'center', mt: 8 }}>
                <CircularProgress />
            </Container>
        );
    }

    return (
        <Container maxWidth="md">
            <Box sx={{ mb: 4, mt: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <Box>
                    <Button
                        startIcon={<ArrowBackIcon />}
                        onClick={() => isEditing ? navigate(`/activities/${code}`) : navigate('/activities')}
                        sx={{ mb: 1 }}
                        color="inherit"
                        size="small"
                    >
                        Volver
                    </Button>
                    <Typography variant="h4" component="h1" fontWeight="bold" color="primary.main">
                        {isEditing ? 'Editar Actividad' : 'Nueva Actividad'}
                    </Typography>
                </Box>
            </Box>

            <Paper elevation={2} sx={{ p: 4, mb: 4 }}>
                <form onSubmit={handleSubmit}>
                    <TextField
                        fullWidth
                        label="Código de la Actividad (Alfanumérico único)"
                        value={form.code}
                        onChange={(e) => setForm({ ...form, code: e.target.value })}
                        margin="normal"
                        required
                        disabled={isEditing}
                    />
                    <TextField
                        fullWidth
                        label="Título"
                        value={form.title}
                        onChange={(e) => setForm({ ...form, title: e.target.value })}
                        margin="normal"
                        required
                    />
                    <TextField
                        fullWidth
                        label="Descripción"
                        value={form.description}
                        onChange={(e) => setForm({ ...form, description: e.target.value })}
                        margin="normal"
                        required
                        multiline
                        rows={4}
                    />
                    <TextField
                        fullWidth
                        type="number"
                        label="Máximo de Participantes por Evento"
                        value={form.max_participants_per_meeting}
                        onChange={(e) => setForm({ ...form, max_participants_per_meeting: parseInt(e.target.value) || 2 })}
                        margin="normal"
                        required
                        inputProps={{ min: 2 }}
                    />
                    <Box sx={{ mt: 2 }}>
                        <FormControlLabel
                            control={
                                <Checkbox
                                    checked={form.is_active}
                                    onChange={(e) => setForm({ ...form, is_active: e.target.checked })}
                                    color="primary"
                                />
                            }
                            label="Actividad Activa (Visible y permite crear eventos)"
                        />
                    </Box>

                    <Button
                        type="submit"
                        variant="contained"
                        color="primary"
                        startIcon={<SaveIcon />}
                        disabled={mutation.isPending}
                        sx={{ mt: 4, width: '100%', py: 1.5 }}
                    >
                        {mutation.isPending ? 'Guardando...' : (isEditing ? 'Guardar Cambios' : 'Crear Actividad')}
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
    );
};

export default ActivityFormPage;
