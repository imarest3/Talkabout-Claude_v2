import { createTheme } from '@mui/material/styles';

// Colores Institucionales UPV
const UPV_RED = '#d3003b'; // Rojo principal
const UPV_DARK_RED = '#a3002d'; // Rojo oscuro para hovers
const UPV_GRAY = '#f5f5f5'; // Fondo gris claro

const theme = createTheme({
    palette: {
        primary: {
            main: UPV_RED,
            dark: UPV_DARK_RED,
        },
        secondary: {
            main: '#424242', // Gris oscuro para buenos contrastes
        },
        background: {
            default: UPV_GRAY,
            paper: '#ffffff',
        },
    },
    typography: {
        fontFamily: [
            'Roboto',
            '"Helvetica Neue"',
            'Arial',
            'sans-serif',
        ].join(','),
        h1: {
            fontWeight: 600,
        },
        h2: {
            fontWeight: 600,
        },
        h3: {
            fontWeight: 600,
            fontSize: '2rem',
        },
        h4: {
            fontWeight: 600,
        },
    },
    components: {
        MuiButton: {
            styleOverrides: {
                root: {
                    textTransform: 'none', // Estilo más amigable y moderno
                    fontWeight: 600,
                    borderRadius: 8, // Bordes ligeramente redondeados
                },
            },
        },
        MuiAppBar: {
            styleOverrides: {
                root: {
                    backgroundColor: '#ffffff',
                    color: '#333333',
                },
            },
        },
    },
});

export default theme;
