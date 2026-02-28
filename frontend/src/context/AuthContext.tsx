import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, LoginResponse } from '../types';
import apiClient from '../services/api/client';

interface AuthContextType {
    user: User | null;
    isAuthenticated: boolean;
    login: (credentials: { user_code: string; password: string }) => Promise<void>;
    logout: () => void;
    isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        // Inicializar estado desde localStorage en mount
        const storedUser = localStorage.getItem('user');
        const token = localStorage.getItem('access_token');

        if (storedUser && token) {
            try {
                setUser(JSON.parse(storedUser));
            } catch (e) {
                console.error('Error parsing user from localStorage', e);
            }
        }
        setIsLoading(false);
    }, []);

    const login = async (credentials: { user_code: string; password: string }) => {
        try {
            const response = await apiClient.post<LoginResponse>('/users/auth/login/', credentials);
            const { access, refresh, user: loggedUser } = response.data;

            // Guardar en localStorage
            localStorage.setItem('access_token', access);
            localStorage.setItem('refresh_token', refresh);
            localStorage.setItem('user', JSON.stringify(loggedUser));

            // Actualizar estado
            setUser(loggedUser);
        } catch (error) {
            console.error('Login error', error);
            throw error;
        }
    };

    const logout = () => {
        // Intentar invalidar en backend (best effort)
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
            apiClient.post('/users/auth/logout/', { refresh_token: refreshToken }).catch(e => console.error(e));
        }

        // Limpiar estado
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        setUser(null);
    };

    return (
        <AuthContext.Provider
            value={{
                user,
                isAuthenticated: !!user,
                login,
                logout,
                isLoading,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};
