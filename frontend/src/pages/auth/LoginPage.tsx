import React, { useState } from 'react';
import {
    Container, Box, Typography, TextField, Button, Paper, Alert
} from '@mui/material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const LoginPage: React.FC = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const { login } = useAuth();

    const [userCode, setUserCode] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);

    // Intentamos recuperar la ruta a la que intentaba ir el usuario antes de loguearse
    const from = (location.state as any)?.from?.pathname || '/activities';

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setIsLoading(true);

        try {
            await login({ user_code: userCode, password });
            navigate(from, { replace: true });
        } catch (err: any) {
            if (err.response?.status === 401) {
                setError('Credenciales incorrectas. Verifique su código de usuario y contraseña.');
            } else {
                setError('Ha ocurrido un error inesperado al intentar iniciar sesión. Inténtelo más tarde.');
            }
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <Container maxWidth="xs">
            <Paper elevation={3} sx={{ padding: 4, mt: 8, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <Typography component="h1" variant="h5" color="primary" sx={{ fontWeight: 'bold', mb: 3 }}>
                    Iniciar Sesión
                </Typography>

                {error && (
                    <Alert severity="error" sx={{ width: '100%', mb: 2 }}>
                        {error}
                    </Alert>
                )}

                <Box component="form" onSubmit={handleSubmit} sx={{ width: '100%' }}>
                    <TextField
                        margin="normal"
                        required
                        fullWidth
                        id="userCode"
                        label="Código de Usuario"
                        name="userCode"
                        autoComplete="username"
                        autoFocus
                        value={userCode}
                        onChange={(e) => setUserCode(e.target.value)}
                    />
                    <TextField
                        margin="normal"
                        required
                        fullWidth
                        name="password"
                        label="Contraseña"
                        type="password"
                        id="password"
                        autoComplete="current-password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                    />
                    <Button
                        type="submit"
                        fullWidth
                        variant="contained"
                        color="primary"
                        disabled={isLoading}
                        sx={{ mt: 3, mb: 2, py: 1.5 }}
                    >
                        {isLoading ? 'Ingresando...' : 'Ingresar'}
                    </Button>
                </Box>
            </Paper>
        </Container>
    );
};

export default LoginPage;
