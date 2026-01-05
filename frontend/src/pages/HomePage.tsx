import { Typography, Box, Paper, Grid, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import RecommendIcon from '@mui/icons-material/Recommend';
import CategoryIcon from '@mui/icons-material/Category';
import FeedbackIcon from '@mui/icons-material/Feedback';

function HomePage() {
  const navigate = useNavigate();

  return (
    <Box>
      <Typography variant="h3" component="h1" gutterBottom align="center">
        🎲 Bienvenido al Sistema de Recomendación de Juegos de Mesa
      </Typography>
      <Typography variant="h6" align="center" color="text.secondary" paragraph>
        Sistema inteligente para asesores pedagógicos del CJEI
      </Typography>

      <Grid container spacing={3} sx={{ mt: 4 }}>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, textAlign: 'center', height: '100%' }}>
            <RecommendIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
            <Typography variant="h5" gutterBottom>
              Recomendaciones Inteligentes
            </Typography>
            <Typography color="text.secondary" paragraph>
              Motor híbrido que combina filtrado colaborativo, basado en contenido y conocimiento pedagógico
            </Typography>
            <Button 
              variant="contained" 
              onClick={() => navigate('/recommendations')}
            >
              Ver Recomendaciones
            </Button>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, textAlign: 'center', height: '100%' }}>
            <CategoryIcon sx={{ fontSize: 60, color: 'secondary.main', mb: 2 }} />
            <Typography variant="h5" gutterBottom>
              Gestión de Catálogo
            </Typography>
            <Typography color="text.secondary" paragraph>
              Administra y explora el catálogo completo de juegos de mesa del CJEI
            </Typography>
            <Button 
              variant="contained" 
              onClick={() => navigate('/games')}
            >
              Explorar Catálogo
            </Button>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, textAlign: 'center', height: '100%' }}>
            <FeedbackIcon sx={{ fontSize: 60, color: 'success.main', mb: 2 }} />
            <Typography variant="h5" gutterBottom>
              Explicabilidad y Feedback
            </Typography>
            <Typography color="text.secondary" paragraph>
              Cada recomendación incluye explicaciones claras y sistema de retroalimentación
            </Typography>
          </Paper>
        </Grid>
      </Grid>

      <Paper sx={{ p: 3, mt: 4 }}>
        <Typography variant="h5" gutterBottom>
          Características del Sistema
        </Typography>
        <Typography component="div">
          <ul>
            <li><strong>Motor Híbrido:</strong> Combina múltiples técnicas de recomendación para mayor precisión</li>
            <li><strong>Explicabilidad:</strong> Justificación pedagógica clara de cada recomendación</li>
            <li><strong>Feedback Loop:</strong> Mejora continua basada en retroalimentación de usuarios</li>
            <li><strong>Personalización:</strong> Adaptado a necesidades pedagógicas específicas</li>
          </ul>
        </Typography>
      </Paper>
    </Box>
  );
}

export default HomePage;
