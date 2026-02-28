import React from 'react';
import { Box, Container, Typography } from '@mui/material';

const Footer: React.FC = () => {
    return (
        <Box
            component="footer"
            sx={{
                py: 4,
                px: 2,
                mt: 'auto',
                backgroundColor: (theme) => theme.palette.grey[900],
                color: 'white',
            }}
        >
            <Container maxWidth="lg">
                <Typography variant="body2" align="center">
                    © {new Date().getFullYear()} Universitat Politècnica de València - Talkabout
                </Typography>
            </Container>
        </Box>
    );
};

export default Footer;
