import { Typography, Box } from '@mui/material';

function GamesPage() {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Catálogo de Juegos de Mesa
      </Typography>
      <Typography color="text.secondary">
        Esta página mostrará el catálogo completo de juegos de mesa disponibles.
      </Typography>
      {/* TODO: Implement games catalog with filters and search */}
    </Box>
  );
}

export default GamesPage;
