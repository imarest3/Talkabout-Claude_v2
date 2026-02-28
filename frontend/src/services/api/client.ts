import axios, { AxiosError } from 'axios';

const baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
    baseURL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request Interceptor: Añadir el token a cada request
apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token && config.headers) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Response Interceptor: Manejar refresco de token en 401
apiClient.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
        const originalRequest = error.config;

        // Si el error es 401, no estamos re-intentando una ruta de auth o refrescar un token
        if (
            error.response?.status === 401 &&
            originalRequest &&
            !originalRequest.url?.includes('auth/login') &&
            !originalRequest.url?.includes('auth/token/refresh') &&
            // Usamos una propiedad custom para evitar bucles infinitos
            !(originalRequest as any)._retry
        ) {
            (originalRequest as any)._retry = true;
            const refreshToken = localStorage.getItem('refresh_token');

            if (refreshToken) {
                try {
                    const response = await axios.post(`${baseURL}/users/auth/token/refresh/`, {
                        refresh: refreshToken,
                    });

                    const newAccessToken = response.data.access;
                    // Si el endpoint también devuelve un nuevo refresh token, lo guardamos
                    if (response.data.refresh) {
                        localStorage.setItem('refresh_token', response.data.refresh);
                    }

                    localStorage.setItem('access_token', newAccessToken);

                    // Re-intentar el request original con el nuevo token
                    if (originalRequest.headers) {
                        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
                    }
                    return apiClient(originalRequest);
                } catch (refreshError) {
                    // El refresh token falló (expiro o es inválido). Logout forzoso.
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('refresh_token');
                    localStorage.removeItem('user');
                    // Redirigir al usuario al login
                    window.location.href = '/login';
                    return Promise.reject(refreshError);
                }
            }
        }

        return Promise.reject(error);
    }
);

export default apiClient;
