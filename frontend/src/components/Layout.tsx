import { ReactNode } from 'react';
import { AppBar, Toolbar, Typography, Container, Box, Button } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import SportsEsportsIcon from '@mui/icons-material/SportsEsports';

interface LayoutProps {
  children: ReactNode;
}

function Layout({ children }: LayoutProps) {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <AppBar position="static">
        <Toolbar>
          <SportsEsportsIcon sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Sistema de Recomendación de Juegos - CJEI
          </Typography>
          <Button color="inherit" component={RouterLink} to="/">
            Inicio
          </Button>
          <Button color="inherit" component={RouterLink} to="/games">
            Catálogo
          </Button>
          <Button color="inherit" component={RouterLink} to="/recommendations">
            Recomendaciones
          </Button>
        </Toolbar>
      </AppBar>
      <Container component="main" sx={{ mt: 4, mb: 4, flex: 1 }}>
        {children}
      </Container>
      <Box
        component="footer"
        sx={{
          py: 3,
          px: 2,
          mt: 'auto',
          backgroundColor: (theme) =>
            theme.palette.mode === 'light'
              ? theme.palette.grey[200]
              : theme.palette.grey[800],
        }}
      >
        <Container maxWidth="sm">
          <Typography variant="body2" color="text.secondary" align="center">
            © 2026 CJEI - Pontificia Universidad Javeriana Cali
          </Typography>
          <Typography variant="body2" color="text.secondary" align="center">
            Trabajo de Grado - Cristian Carabalí
          </Typography>
        </Container>
      </Box>
    </Box>
  );
}

export default Layout;
