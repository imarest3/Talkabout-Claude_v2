import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline, Box, Typography } from '@mui/material';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import theme from './theme';
import MainLayout from './components/layout/MainLayout';
import { AuthProvider } from './context/AuthContext';
import LoginPage from './pages/auth/LoginPage';
import UnsubscribePage from './pages/auth/UnsubscribePage';
import ActivityListPage from './pages/activities/ActivityListPage';
import ActivityDetailPage from './pages/activities/ActivityDetailPage';
import ActivityFormPage from './pages/activities/ActivityFormPage';
import WaitingRoomPage from './pages/events/WaitingRoomPage';
import EventFormPage from './pages/events/EventFormPage';
import ProfilePage from './pages/profile/ProfilePage';
import CalendarPage from './pages/calendar/CalendarPage';
import PrivateRoute from './components/auth/PrivateRoute';

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

                {/* Rutas Públicas */}
                <Route path="login" element={<LoginPage />} />
                <Route path="register" element={<Placeholder title="Registro de Usuario" />} />
                <Route path="unsubscribe" element={<UnsubscribePage />} />

                {/* Rutas Privadas */}
                <Route element={<PrivateRoute />}>
                  <Route index element={<Navigate to="/activities" replace />} />
                  <Route path="activities" element={<ActivityListPage />} />
                  <Route path="activities/create" element={<ActivityFormPage />} />
                  <Route path="activities/:code/edit" element={<ActivityFormPage />} />
                  <Route path="activities/:id" element={<ActivityDetailPage />} />
                  <Route path="activities/:code/events/create" element={<EventFormPage />} />
                  <Route path="events/:eventId/waiting-room" element={<WaitingRoomPage />} />
                  <Route path="calendar" element={<CalendarPage />} />
                  <Route path="profile" element={<ProfilePage />} />
                </Route>

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
