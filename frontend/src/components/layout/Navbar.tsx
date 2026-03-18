import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box, Container } from '@mui/material';
import { Link, useNavigate } from 'react-router-dom';
import upvLogo from '../../assets/upv-logo.png';
import { useAuth } from '../../context/AuthContext';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';

const Navbar: React.FC = () => {
    const navigate = useNavigate();
    const { isAuthenticated, logout, user } = useAuth();

    const handleLogout = async () => {
        await logout();
        navigate('/login');
    };

    return (
        <AppBar position="sticky" elevation={1}>
            <Container maxWidth="lg">
                <Toolbar disableGutters>
                    <Box
                        sx={{
                            display: 'flex',
                            alignItems: 'center',
                            flexGrow: 1,
                            gap: 2
                        }}
                    >
                        <a href="https://www.upv.es/" target="_blank" rel="noopener noreferrer" style={{ display: 'flex', alignItems: 'center' }}>
                            <Box
                                component="img"
                                src={upvLogo}
                                alt="UPV Logo"
                                sx={{ height: 40, display: 'block' }}
                            />
                        </a>
                        <Typography
                            component={Link}
                            to="/"
                            variant="h6"
                            sx={{
                                fontWeight: 800,
                                color: 'primary.main',
                                letterSpacing: '-0.5px',
                                textDecoration: 'none'
                            }}
                        >
                            TALKABOUT
                        </Typography>
                    </Box>

                    <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                        {isAuthenticated ? (
                            <>
                                <Button color="inherit" component={Link} to="/activities">
                                    Actividades
                                </Button>
                                <Button color="inherit" component={Link} to="/calendar">
                                    Calendario
                                </Button>
                                <Button color="inherit" component={Link} to="/profile">
                                    Perfil
                                </Button>

                                <Box sx={{ display: 'flex', alignItems: 'center', ml: 2, mr: 1, gap: 1, color: 'text.secondary' }}>
                                    <AccountCircleIcon />
                                    <Typography variant="body2" fontWeight="bold">
                                        {user?.user_code}
                                    </Typography>
                                </Box>

                                <Button variant="outlined" color="primary" onClick={handleLogout}>
                                    Cerrar Sesión
                                </Button>
                            </>
                        ) : (
                            <Button variant="outlined" color="primary" onClick={() => navigate('/login')}>
                                Iniciar Sesión
                            </Button>
                        )}
                    </Box>
                </Toolbar>
            </Container>
        </AppBar>
    );
};

export default Navbar;
