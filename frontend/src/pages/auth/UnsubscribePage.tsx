import React, { useEffect, useState } from 'react';
import {
    Container, Box, Typography, Button, Paper, Alert,
    CircularProgress, Divider, Dialog, DialogTitle,
    DialogContent, DialogContentText, DialogActions
} from '@mui/material';
import NotificationsOffIcon from '@mui/icons-material/NotificationsOff';
import NotificationsActiveIcon from '@mui/icons-material/NotificationsActive';
import DeleteForeverIcon from '@mui/icons-material/DeleteForever';
import { useSearchParams } from 'react-router-dom';
import apiClient from '../../services/api/client';

type PageState = 'loading' | 'ready' | 'invalid' | 'done_email' | 'done_account' | 'done_reactivate';

interface UserInfo {
    email_masked: string;
    email_notifications_enabled: boolean;
}

const UnsubscribePage: React.FC = () => {
    const [searchParams] = useSearchParams();
    const token = searchParams.get('token') || '';

    const [pageState, setPageState] = useState<PageState>('loading');
    const [userInfo, setUserInfo] = useState<UserInfo | null>(null);
    const [errorMsg, setErrorMsg] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [confirmDeleteOpen, setConfirmDeleteOpen] = useState(false);

    useEffect(() => {
        if (!token) {
            setPageState('invalid');
            setErrorMsg('No se ha proporcionado un token válido.');
            return;
        }

        apiClient.get(`/users/unsubscribe/${token}/`)
            .then(res => {
                setUserInfo(res.data);
                setPageState('ready');
            })
            .catch(err => {
                setPageState('invalid');
                setErrorMsg(err.response?.data?.error || 'Token inválido o caducado.');
            });
    }, [token]);

    const handleUnsubscribeEmail = async () => {
        setIsSubmitting(true);
        try {
            await apiClient.post(`/users/unsubscribe/${token}/email/`);
            setPageState('done_email');
        } catch (err: any) {
            setErrorMsg(err.response?.data?.error || 'Error al procesar la solicitud.');
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleReactivateEmail = async () => {
        setIsSubmitting(true);
        try {
            await apiClient.post(`/users/unsubscribe/${token}/reactivate/`);
            setPageState('done_reactivate');
        } catch (err: any) {
            setErrorMsg(err.response?.data?.error || 'Error al procesar la solicitud.');
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleDeleteAccount = async () => {
        setConfirmDeleteOpen(false);
        setIsSubmitting(true);
        try {
            await apiClient.post(`/users/unsubscribe/${token}/account/`);
            setPageState('done_account');
        } catch (err: any) {
            setErrorMsg(err.response?.data?.error || 'Error al procesar la solicitud.');
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <Container maxWidth="sm" sx={{ mt: 8 }}>
            <Paper elevation={3} sx={{ p: 4 }}>
                <Typography variant="h5" fontWeight="bold" gutterBottom color="primary">
                    Gestión de suscripción
                </Typography>
                <Divider sx={{ mb: 3 }} />

                {pageState === 'loading' && (
                    <Box display="flex" justifyContent="center" py={4}>
                        <CircularProgress />
                    </Box>
                )}

                {pageState === 'invalid' && (
                    <Alert severity="error">{errorMsg}</Alert>
                )}

                {pageState === 'ready' && userInfo && (
                    <>
                        <Typography variant="body1" gutterBottom>
                            Cuenta: <strong>{userInfo.email_masked}</strong>
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                            Desde aquí puedes gestionar las notificaciones por correo o eliminar tu cuenta definitivamente.
                        </Typography>

                        {errorMsg && <Alert severity="error" sx={{ mb: 2 }}>{errorMsg}</Alert>}

                        {/* Sección correos */}
                        <Box sx={{ mb: 2 }}>
                            {userInfo.email_notifications_enabled ? (
                                <>
                                    <Typography variant="subtitle2" gutterBottom>
                                        Notificaciones por correo: <strong style={{ color: 'green' }}>Activas</strong>
                                    </Typography>
                                    <Button
                                        variant="outlined"
                                        color="warning"
                                        startIcon={<NotificationsOffIcon />}
                                        fullWidth
                                        disabled={isSubmitting}
                                        onClick={handleUnsubscribeEmail}
                                    >
                                        Dar de baja el envío de correos
                                    </Button>
                                </>
                            ) : (
                                <>
                                    <Typography variant="subtitle2" gutterBottom>
                                        Notificaciones por correo: <strong style={{ color: 'gray' }}>Desactivadas</strong>
                                    </Typography>
                                    <Button
                                        variant="outlined"
                                        color="success"
                                        startIcon={<NotificationsActiveIcon />}
                                        fullWidth
                                        disabled={isSubmitting}
                                        onClick={handleReactivateEmail}
                                    >
                                        Reactivar envío de correos
                                    </Button>
                                </>
                            )}
                        </Box>

                        <Divider sx={{ my: 3 }} />

                        {/* Sección baja definitiva */}
                        <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                            Baja definitiva
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                            Esta acción eliminará tu correo electrónico y anonimizará todos tus datos. Las estadísticas de participación se conservan de forma anónima. Esta acción es irreversible.
                        </Typography>
                        <Button
                            variant="contained"
                            color="error"
                            startIcon={<DeleteForeverIcon />}
                            fullWidth
                            disabled={isSubmitting}
                            onClick={() => setConfirmDeleteOpen(true)}
                        >
                            Eliminar mi cuenta definitivamente
                        </Button>
                    </>
                )}

                {pageState === 'done_email' && (
                    <Alert severity="success" icon={<NotificationsOffIcon />}>
                        Has sido dado de baja del envío de correos. Ya no recibirás notificaciones de Talkabout.
                        Puedes volver a activarlos en cualquier momento usando este mismo enlace.
                    </Alert>
                )}

                {pageState === 'done_reactivate' && (
                    <Alert severity="success" icon={<NotificationsActiveIcon />}>
                        Notificaciones por correo reactivadas correctamente. Volverás a recibir recordatorios de tus eventos.
                    </Alert>
                )}

                {pageState === 'done_account' && (
                    <Alert severity="info" icon={<DeleteForeverIcon />}>
                        Tu cuenta ha sido eliminada definitivamente. Tus datos personales han sido anonimizados y ya no recibirás más comunicaciones.
                    </Alert>
                )}
            </Paper>

            {/* Diálogo de confirmación de baja definitiva */}
            <Dialog open={confirmDeleteOpen} onClose={() => setConfirmDeleteOpen(false)}>
                <DialogTitle>¿Eliminar cuenta definitivamente?</DialogTitle>
                <DialogContent>
                    <DialogContentText>
                        Esta acción es <strong>irreversible</strong>. Tu correo electrónico será eliminado y tus datos anonimizados. Las estadísticas de participación se conservarán de forma anónima.
                    </DialogContentText>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setConfirmDeleteOpen(false)}>Cancelar</Button>
                    <Button onClick={handleDeleteAccount} color="error" variant="contained">
                        Eliminar mi cuenta
                    </Button>
                </DialogActions>
            </Dialog>
        </Container>
    );
};

export default UnsubscribePage;
