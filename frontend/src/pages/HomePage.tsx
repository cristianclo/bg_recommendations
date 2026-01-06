import { Link } from 'react-router-dom';
import { FileText, Gamepad2, Star, TrendingUp } from 'lucide-react';

export default function HomePage() {
  const features = [
    {
      to: '/sessions/new',
      icon: FileText,
      title: 'Nueva Sesión',
      description: 'Crear un perfil de sesión y obtener recomendaciones personalizadas',
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      to: '/games',
      icon: Gamepad2,
      title: 'Catálogo de Juegos',
      description: 'Explorar el catálogo completo de juegos disponibles',
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      to: '/skills',
      icon: Star,
      title: 'Habilidades',
      description: 'Ver la taxonomía de habilidades pedagógicas',
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
    },
  ];

  return (
    <div className="container mx-auto px-4 py-12">
      {/* Hero Section */}
      <div className="max-w-4xl mx-auto text-center mb-16">
        <div className="flex items-center justify-center mb-6">
          <Gamepad2 className="h-16 w-16 text-blue-600" />
        </div>
        <h1 className="text-5xl font-bold text-gray-900 mb-4">
          Sistema de Recomendación CJEI
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Plataforma inteligente para seleccionar juegos de mesa basados en objetivos pedagógicos
        </p>
        <Link
          to="/sessions/new"
          className="inline-flex items-center px-8 py-4 bg-blue-600 text-white text-lg font-semibold rounded-lg hover:bg-blue-700 transition-colors shadow-lg"
        >
          <FileText className="h-6 w-6 mr-2" />
          Crear Nueva Sesión
        </Link>
      </div>

      {/* Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto mb-16">
        {features.map((feature) => {
          const Icon = feature.icon;
          return (
            <Link
              key={feature.to}
              to={feature.to}
              className="group bg-white p-8 rounded-xl shadow-md hover:shadow-xl transition-all border-2 border-transparent hover:border-blue-500"
            >
              <div className={`inline-flex p-4 rounded-lg ${feature.bgColor} mb-4 group-hover:scale-110 transition-transform`}>
                <Icon className={`h-8 w-8 ${feature.color}`} />
              </div>
              <h2 className="text-2xl font-semibold text-gray-900 mb-3">
                {feature.title}
              </h2>
              <p className="text-gray-600">
                {feature.description}
              </p>
            </Link>
          );
        })}
      </div>

      {/* About Section */}
      <div className="max-w-4xl mx-auto bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-8 border border-blue-200">
        <div className="flex items-start gap-4">
          <TrendingUp className="h-8 w-8 text-blue-600 flex-shrink-0 mt-1" />
          <div>
            <h3 className="text-2xl font-bold text-gray-900 mb-3">
              ¿Cómo funciona?
            </h3>
            <div className="space-y-3 text-gray-700">
              <p>
                <strong>1. Define tu sesión:</strong> Establece los objetivos pedagógicos, habilidades a desarrollar, tiempo disponible y tamaño del grupo.
              </p>
              <p>
                <strong>2. Obtén recomendaciones:</strong> Nuestro sistema analiza tu perfil y te sugiere los juegos más adecuados.
              </p>
              <p>
                <strong>3. Proporciona feedback:</strong> Después de usar un juego, comparte tu experiencia para mejorar futuras recomendaciones.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Footer Note */}
      <div className="text-center mt-12 text-gray-500 text-sm">
        <p>
          Centro de Juegos y Experiencias Interactivas (CJEI)
        </p>
        <p>
          Pontificia Universidad Javeriana Cali
        </p>
      </div>
    </div>
  );
}
