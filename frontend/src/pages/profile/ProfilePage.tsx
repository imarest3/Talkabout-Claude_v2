import React, { useState } from 'react';
import {
    Container,
    Typography,
    Box,
    Paper,
    Grid,
    TextField,
    Button,
    CircularProgress,
    Divider,
    Alert,
    Snackbar
} from '@mui/material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import SaveIcon from '@mui/icons-material/Save';
import VpnKeyIcon from '@mui/icons-material/VpnKey';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';

import apiClient from '../../services/api/client';
import { User } from '../../types';

const ProfilePage: React.FC = () => {
    const queryClient = useQueryClient();
    const [snackbar, setSnackbar] = useState<{ open: boolean, message: string, severity: 'success' | 'error' }>({
        open: false,
        message: '',
        severity: 'success'
    });

    // Estado del formulario de perfil
    const [profileForm, setProfileForm] = useState({
        email: '',
        timezone: ''
    });

    // Estado del formulario de contraseña
    const [passwordForm, setPasswordForm] = useState({
        old_password: '',
        new_password: '',
        confirm_password: ''
    });

    // 1. Obtener datos del perfil
    const { data: profile, isLoading } = useQuery<User>({
        queryKey: ['profile'],
        queryFn: async () => {
            const response = await apiClient.get<User>('/users/profile/');
            return response.data;
        }
    });

    React.useEffect(() => {
        if (profile) {
            setProfileForm({
                email: profile.email || '',
                timezone: profile.timezone || ''
            });
        }
    }, [profile]);

    // 2. Mutación para actualizar perfil
    const updateProfileMutation = useMutation({
        mutationFn: async (data: { email: string; timezone: string }) => {
            const response = await apiClient.patch('/users/profile/update/', data);
            return response.data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['profile'] });
            setSnackbar({ open: true, message: 'Perfil actualizado correctamente', severity: 'success' });
        },
        onError: () => {
            setSnackbar({ open: true, message: 'Error al actualizar el perfil', severity: 'error' });
        }
    });

    // 3. Mutación para cambiar contraseña
    const changePasswordMutation = useMutation({
        mutationFn: async (data: any) => {
            // Se envía a endpoint de cambio de contraseña 
            // NOTA: Ajusta la URL según corresponda a tu backend (ej: /users/profile/change-password/ o /users/auth/change-password/)
            const response = await apiClient.post('/users/profile/change-password/', data);
            return response.data;
        },
        onSuccess: () => {
            setPasswordForm({ old_password: '', new_password: '', confirm_password: '' });
            setSnackbar({ open: true, message: 'Contraseña cambiada exitosamente', severity: 'success' });
        },
        onError: (error: any) => {
            const detail = error.response?.data?.detail || error.response?.data?.old_password?.[0] || 'Error al cambiar la contraseña';
            setSnackbar({ open: true, message: detail, severity: 'error' });
        }
    });

    const handleProfileSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        updateProfileMutation.mutate(profileForm);
    };

    const handlePasswordSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (passwordForm.new_password !== passwordForm.confirm_password) {
            setSnackbar({ open: true, message: 'Las contraseñas nuevas no coinciden', severity: 'error' });
            return;
        }
        changePasswordMutation.mutate({
            old_password: passwordForm.old_password,
            new_password: passwordForm.new_password,
            new_password_confirm: passwordForm.confirm_password
        });
    };

    if (isLoading) {
        return (
            <Container sx={{ display: 'flex', justifyContent: 'center', mt: 8 }}>
                <CircularProgress />
            </Container>
        );
    }

    return (
        <Container maxWidth="md">
            <Box sx={{ mb: 4, mt: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
                <AccountCircleIcon sx={{ fontSize: 40, color: 'primary.main' }} />
                <Typography variant="h4" component="h1" fontWeight="bold" color="primary.main">
                    Mi Perfil
                </Typography>
            </Box>

            <Grid container spacing={4}>
                {/* Columna Izquierda: Datos No Editables y Formulario de Edición */}
                <Grid item xs={12} md={6}>
                    <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
                        <Typography variant="h6" gutterBottom fontWeight="bold" color="primary">
                            Información de la Cuenta
                        </Typography>
                        <Divider sx={{ mb: 3 }} />

                        <Box sx={{ mb: 3 }}>
                            <Typography variant="subtitle2" color="text.secondary">Código de Usuario</Typography>
                            <Typography variant="body1" fontWeight="medium">{profile?.user_code || 'N/A'}</Typography>
                        </Box>

                        <Box sx={{ mb: 3 }}>
                            <Typography variant="subtitle2" color="text.secondary">Rol</Typography>
                            <Typography variant="body1" fontWeight="medium" textTransform="capitalize">
                                {profile?.role || 'Estudiante'}
                            </Typography>
                        </Box>
                    </Paper>

                    <Paper elevation={2} sx={{ p: 3 }}>
                        <Typography variant="h6" gutterBottom fontWeight="bold" color="primary">
                            Editar Perfil
                        </Typography>
                        <Divider sx={{ mb: 3 }} />

                        <form onSubmit={handleProfileSubmit}>
                            <TextField
                                fullWidth
                                label="Correo Electrónico"
                                type="email"
                                value={profileForm.email}
                                onChange={(e) => setProfileForm({ ...profileForm, email: e.target.value })}
                                margin="normal"
                                required
                            />
                            <TextField
                                fullWidth
                                label="Zona Horaria"
                                value={profileForm.timezone}
                                onChange={(e) => setProfileForm({ ...profileForm, timezone: e.target.value })}
                                margin="normal"
                                helperText="Ejemplo: Europe/Madrid o America/Mexico_City"
                                required
                            />

                            <Button
                                type="submit"
                                variant="contained"
                                color="primary"
                                startIcon={<SaveIcon />}
                                disabled={updateProfileMutation.isPending}
                                sx={{ mt: 3, width: '100%' }}
                            >
                                {updateProfileMutation.isPending ? 'Guardando...' : 'Guardar Cambios'}
                            </Button>
                        </form>
                    </Paper>
                </Grid>

                {/* Columna Derecha: Cambio de Contraseña */}
                <Grid item xs={12} md={6}>
                    <Paper elevation={2} sx={{ p: 3 }}>
                        <Typography variant="h6" gutterBottom fontWeight="bold" color="primary" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <VpnKeyIcon /> Seguridad
                        </Typography>
                        <Divider sx={{ mb: 3 }} />

                        <form onSubmit={handlePasswordSubmit}>
                            <TextField
                                fullWidth
                                label="Contraseña Actual"
                                type="password"
                                value={passwordForm.old_password}
                                onChange={(e) => setPasswordForm({ ...passwordForm, old_password: e.target.value })}
                                margin="normal"
                                required
                            />
                            <TextField
                                fullWidth
                                label="Nueva Contraseña"
                                type="password"
                                value={passwordForm.new_password}
                                onChange={(e) => setPasswordForm({ ...passwordForm, new_password: e.target.value })}
                                margin="normal"
                                required
                            />
                            <TextField
                                fullWidth
                                label="Confirmar Nueva Contraseña"
                                type="password"
                                value={passwordForm.confirm_password}
                                onChange={(e) => setPasswordForm({ ...passwordForm, confirm_password: e.target.value })}
                                margin="normal"
                                required
                                error={passwordForm.confirm_password !== '' && passwordForm.new_password !== passwordForm.confirm_password}
                                helperText={passwordForm.confirm_password !== '' && passwordForm.new_password !== passwordForm.confirm_password ? "Las contraseñas no coinciden" : ""}
                            />

                            <Button
                                type="submit"
                                variant="outlined"
                                color="primary"
                                disabled={changePasswordMutation.isPending}
                                sx={{ mt: 3, width: '100%' }}
                            >
                                {changePasswordMutation.isPending ? 'Cambiando...' : 'Actualizar Contraseña'}
                            </Button>
                        </form>
                    </Paper>
                </Grid>
            </Grid>

            {/* Snackbar para notificaciones */}
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

export default ProfilePage;
