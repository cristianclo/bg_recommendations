import { Typography, Box } from '@mui/material';

function RecommendationsPage() {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Recomendaciones Personalizadas
      </Typography>
      <Typography color="text.secondary">
        Esta página mostrará recomendaciones personalizadas de juegos con explicaciones.
      </Typography>
      {/* TODO: Implement recommendations display with explanations and feedback options */}
    </Box>
  );
}

export default RecommendationsPage;
