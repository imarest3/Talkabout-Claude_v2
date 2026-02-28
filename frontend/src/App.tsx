import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline, Box, Typography } from '@mui/material';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import theme from './theme';
import MainLayout from './components/layout/MainLayout';
import { AuthProvider } from './context/AuthContext';
import LoginPage from './pages/auth/LoginPage';

// Crear cliente de React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

// Componente placeholder para desarrollo
const Placeholder = ({ title }: { title: string }) => (
  <Box sx={{ textAlign: 'center', py: 8 }}>
    <Typography variant="h4" color="primary" gutterBottom>
      {title}
    </Typography>
    <Typography variant="body1" color="text.secondary">
      Componente en construcción (Próximamente)...
    </Typography>
  </Box>
);

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <AuthProvider>
          <BrowserRouter>
            <Routes>
              <Route path="/" element={<MainLayout />}>
                <Route index element={<Navigate to="/activities" replace />} />
                <Route path="activities" element={<Placeholder title="Lista de Actividades" />} />
                <Route path="activities/:id" element={<Placeholder title="Detalle de Actividad" />} />
                <Route path="waiting-room/:eventId" element={<Placeholder title="Sala de Espera" />} />
                <Route path="profile" element={<Placeholder title="Perfil de Usuario" />} />

                {/* Rutas Públicas de Auth */}
                <Route path="login" element={<LoginPage />} />
                <Route path="register" element={<Placeholder title="Registro de Usuario" />} />

                <Route path="*" element={<Placeholder title="Error 404 - Página No Encontrada" />} />
              </Route>
            </Routes>
          </BrowserRouter>
        </AuthProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
