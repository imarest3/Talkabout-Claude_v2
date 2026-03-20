import React from 'react';
import {
    Container, Typography, Box, Paper, Grid, Button,
    CircularProgress, Alert, Divider
} from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import EventIcon from '@mui/icons-material/Event';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ScheduleIcon from '@mui/icons-material/Schedule';
import GroupIcon from '@mui/icons-material/Group';
import HowToRegIcon from '@mui/icons-material/HowToReg';
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';
import apiClient from '../../services/api/client';

interface ActivityStats {
    activity_code: string;
    activity_title: string;
    total_events: number;
    active_events: number;
    completed_events: number;
    total_enrollments: number;
    currently_enrolled: number;
    total_attended: number;
    attendance_rate: number;
}

interface StatCardProps {
    icon: React.ReactNode;
    label: string;
    value: number | string;
    color?: string;
}

const StatCard: React.FC<StatCardProps> = ({ icon, label, value, color = 'primary.main' }) => (
    <Paper elevation={2} sx={{ p: 3, textAlign: 'center', height: '100%' }}>
        <Box sx={{ color, mb: 1 }}>{icon}</Box>
        <Typography variant="h3" fontWeight="bold" color={color}>
            {value}
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
            {label}
        </Typography>
    </Paper>
);

const ActivityStatsPage: React.FC = () => {
    const { code } = useParams<{ code: string }>();
    const navigate = useNavigate();

    const { data: stats, isLoading, isError } = useQuery<ActivityStats>({
        queryKey: ['activity-stats', code],
        queryFn: async () => {
            const response = await apiClient.get<ActivityStats>(`/activities/${code}/statistics/`);
            return response.data;
        },
        enabled: !!code
    });

    if (isLoading) {
        return (
            <Container sx={{ display: 'flex', justifyContent: 'center', mt: 8 }}>
                <CircularProgress />
            </Container>
        );
    }

    if (isError || !stats) {
        return (
            <Container maxWidth="lg" sx={{ mt: 4 }}>
                <Alert severity="error">Error al cargar las estadísticas.</Alert>
                <Button startIcon={<ArrowBackIcon />} onClick={() => navigate(-1)} sx={{ mt: 2 }}>
                    Volver
                </Button>
            </Container>
        );
    }

    return (
        <Container maxWidth="lg">
            <Box sx={{ mb: 4, mt: 2 }}>
                <Button
                    startIcon={<ArrowBackIcon />}
                    onClick={() => navigate(`/activities/${code}`)}
                    sx={{ mb: 2 }}
                    color="inherit"
                >
                    Volver a la actividad
                </Button>

                <Typography variant="h4" component="h1" fontWeight="bold" color="primary.main">
                    Estadísticas
                </Typography>
                <Typography variant="subtitle1" color="text.secondary">
                    {stats.activity_title} · <strong>{stats.activity_code}</strong>
                </Typography>
            </Box>

            {/* Tasa de asistencia destacada */}
            <Paper
                elevation={3}
                sx={{
                    p: 4,
                    mb: 4,
                    textAlign: 'center',
                    background: 'linear-gradient(135deg, #1976d2 0%, #42a5f5 100%)',
                    color: 'white'
                }}
            >
                <Typography variant="overline" sx={{ opacity: 0.85, letterSpacing: 2 }}>
                    Tasa de asistencia
                </Typography>
                <Typography variant="h2" fontWeight="bold">
                    {stats.attendance_rate}%
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.85, mt: 0.5 }}>
                    {stats.total_attended} de {stats.total_enrollments} inscripciones resultaron en asistencia
                </Typography>
            </Paper>

            {/* Métricas de eventos */}
            <Typography variant="h6" fontWeight="bold" color="text.secondary" gutterBottom>
                Eventos
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <Grid container spacing={3} sx={{ mb: 4 }}>
                <Grid item xs={12} sm={4}>
                    <StatCard
                        icon={<EventIcon sx={{ fontSize: 36 }} />}
                        label="Total de eventos"
                        value={stats.total_events}
                    />
                </Grid>
                <Grid item xs={12} sm={4}>
                    <StatCard
                        icon={<ScheduleIcon sx={{ fontSize: 36 }} />}
                        label="Eventos programados"
                        value={stats.active_events}
                        color="warning.main"
                    />
                </Grid>
                <Grid item xs={12} sm={4}>
                    <StatCard
                        icon={<CheckCircleIcon sx={{ fontSize: 36 }} />}
                        label="Eventos completados"
                        value={stats.completed_events}
                        color="success.main"
                    />
                </Grid>
            </Grid>

            {/* Métricas de inscripciones */}
            <Typography variant="h6" fontWeight="bold" color="text.secondary" gutterBottom>
                Inscripciones
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <Grid container spacing={3}>
                <Grid item xs={12} sm={4}>
                    <StatCard
                        icon={<GroupIcon sx={{ fontSize: 36 }} />}
                        label="Total de inscripciones"
                        value={stats.total_enrollments}
                    />
                </Grid>
                <Grid item xs={12} sm={4}>
                    <StatCard
                        icon={<HowToRegIcon sx={{ fontSize: 36 }} />}
                        label="Inscritos actualmente"
                        value={stats.currently_enrolled}
                        color="info.main"
                    />
                </Grid>
                <Grid item xs={12} sm={4}>
                    <StatCard
                        icon={<EmojiEventsIcon sx={{ fontSize: 36 }} />}
                        label="Total de asistentes"
                        value={stats.total_attended}
                        color="success.main"
                    />
                </Grid>
            </Grid>
        </Container>
    );
};

export default ActivityStatsPage;
