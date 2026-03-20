import React, { useState, useEffect } from 'react';
import {
    Container, Typography, Box, TextField, InputAdornment,
    Grid, Card, CardContent, CardActions, Button, Chip,
    Skeleton, Paper
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import EventIcon from '@mui/icons-material/Event';
import { useQuery } from '@tanstack/react-query';
import { Link, useNavigate } from 'react-router-dom';
import apiClient from '../../services/api/client';
import { Activity } from '../../types';
import { useAuth } from '../../context/AuthContext';
import AddIcon from '@mui/icons-material/Add';

interface ActivitiesResponse {
    count: number;
    next: string | null;
    previous: string | null;
    results: Activity[];
}

const ActivityListPage: React.FC = () => {
    const [searchTerm, setSearchTerm] = useState('');
    const [debouncedSearch, setDebouncedSearch] = useState('');
    const { user } = useAuth();
    const navigate = useNavigate();

    const isTeacherOrAdmin = user?.role === 'teacher' || user?.role === 'admin';

    // Update debounced search term after 300ms delay
    useEffect(() => {
        const timer = setTimeout(() => setDebouncedSearch(searchTerm), 300);
        return () => clearTimeout(timer);
    }, [searchTerm]);

    const { data, isLoading, isError } = useQuery({
        queryKey: ['activities', debouncedSearch],
        queryFn: async () => {
            const response = await apiClient.get<ActivitiesResponse>('/activities/', {
                params: { search: debouncedSearch || undefined }
            });
            return response.data;
        }
    });

    return (
        <Container maxWidth="lg">
            <Box sx={{ mb: 4, mt: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <Box>
                    <Typography variant="h4" component="h1" gutterBottom color="primary.main" fontWeight="bold">
                        Actividades Disponibles
                    </Typography>
                    <Typography variant="body1" color="text.secondary" gutterBottom>
                        Explora y únete a los eventos de conversación programados.
                    </Typography>
                </Box>
                {isTeacherOrAdmin && (
                    <Button
                        variant="contained"
                        color="secondary"
                        startIcon={<AddIcon />}
                        onClick={() => navigate('/activities/create')}
                    >
                        Nueva Actividad
                    </Button>
                )}
            </Box>

            {/* Buscador */}
            <Paper elevation={1} sx={{ p: 2, mb: 4 }}>
                <TextField
                    fullWidth
                    variant="outlined"
                    placeholder="Buscar por código, título o descripción..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    InputProps={{
                        startAdornment: (
                            <InputAdornment position="start">
                                <SearchIcon color="action" />
                            </InputAdornment>
                        ),
                    }}
                />
            </Paper>

            {/* Lista de Resultados */}
            {isError && (
                <Typography color="error">
                    Ha ocurrido un error al cargar las actividades. Por favor, intenta de nuevo.
                </Typography>
            )}

            {isLoading ? (
                <Grid container spacing={3}>
                    {[1, 2, 3, 4].map((skeleton) => (
                        <Grid item xs={12} sm={6} md={4} key={skeleton}>
                            <Card sx={{ height: '100%' }}>
                                <CardContent>
                                    <Skeleton variant="text" height={40} width="80%" />
                                    <Skeleton variant="rectangular" height={60} sx={{ my: 1 }} />
                                    <Skeleton variant="text" width="40%" />
                                </CardContent>
                                <CardActions>
                                    <Skeleton variant="rectangular" height={36} width="100%" />
                                </CardActions>
                            </Card>
                        </Grid>
                    ))}
                </Grid>
            ) : data?.results.length === 0 ? (
                <Box sx={{ textAlign: 'center', py: 8 }}>
                    <Typography variant="h6" color="text.secondary">
                        No se encontraron actividades que coincidan con la búsqueda.
                    </Typography>
                </Box>
            ) : (
                <Grid container spacing={3}>
                    {data?.results.map((activity) => (
                        <Grid item xs={12} sm={6} md={4} key={activity.id}>
                            <Card
                                sx={{
                                    height: '100%',
                                    display: 'flex',
                                    flexDirection: 'column',
                                    transition: 'transform 0.2s',
                                    '&:hover': { transform: 'translateY(-4px)', boxShadow: 4 }
                                }}
                            >
                                <CardContent sx={{ flexGrow: 1 }}>
                                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                                        <Typography variant="h6" component="h2" fontWeight="bold" sx={{ pr: 2 }}>
                                            {activity.title}
                                        </Typography>
                                        <Chip
                                            label={activity.is_active ? 'Activa' : 'Inactiva'}
                                            color={activity.is_active ? 'success' : 'default'}
                                            size="small"
                                        />
                                    </Box>

                                    <Typography variant="subtitle2" color="primary" gutterBottom>
                                        Código: {activity.code}
                                    </Typography>

                                    <Typography
                                        variant="body2"
                                        color="text.secondary"
                                        sx={{
                                            mb: 2,
                                            display: '-webkit-box',
                                            WebkitLineClamp: 3,
                                            WebkitBoxOrient: 'vertical',
                                            overflow: 'hidden'
                                        }}
                                        dangerouslySetInnerHTML={{ __html: activity.description }}
                                    />

                                    <Box sx={{ display: 'flex', alignItems: 'center', color: 'text.secondary', mt: 'auto' }}>
                                        <EventIcon sx={{ fontSize: 20, mr: 1 }} />
                                        <Typography variant="body2" fontWeight="medium">
                                            {activity.event_count || 0} Eventos programados
                                        </Typography>
                                    </Box>
                                </CardContent>
                                <CardActions sx={{ p: 2, pt: 0 }}>
                                    <Button
                                        component={Link}
                                        to={`/activities/${activity.code}`}
                                        fullWidth
                                        variant="contained"
                                        disableElevation
                                    >
                                        Ver Detalles
                                    </Button>
                                </CardActions>
                            </Card>
                        </Grid>
                    ))}
                </Grid>
            )}
        </Container>
    );
};

export default ActivityListPage;
