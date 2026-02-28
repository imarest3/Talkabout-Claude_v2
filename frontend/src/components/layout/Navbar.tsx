import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box, Container } from '@mui/material';
import { Link, useNavigate } from 'react-router-dom';

const Navbar: React.FC = () => {
    const navigate = useNavigate();

    return (
        <AppBar position="sticky" elevation={1}>
            <Container maxWidth="lg">
                <Toolbar disableGutters>
                    <Typography
                        variant="h6"
                        component={Link}
                        to="/"
                        sx={{
                            flexGrow: 1,
                            fontWeight: 800,
                            color: 'primary.main',
                            textDecoration: 'none',
                            letterSpacing: '-0.5px'
                        }}
                    >
                        TALKABOUT
                    </Typography>

                    <Box sx={{ display: 'flex', gap: 2 }}>
                        <Button color="inherit" component={Link} to="/activities">
                            Actividades
                        </Button>
                        {/* TODO: Reemplazar con AuthContext cuando se implemente */}
                        <Button variant="outlined" color="primary" onClick={() => navigate('/login')}>
                            Iniciar Sesión
                        </Button>
                        <Button variant="contained" color="primary" onClick={() => navigate('/register')}>
                            Registrarse
                        </Button>
                    </Box>
                </Toolbar>
            </Container>
        </AppBar>
    );
};

export default Navbar;
