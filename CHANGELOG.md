# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-05

### Added
- Initial project structure
- Backend with FastAPI, PostgreSQL, and SQLAlchemy
  - Database models for users, games, categories, mechanics, ratings, recommendations, and feedback
  - Pydantic schemas for validation
  - Core modules for configuration, database, and security
  - Hybrid recommendation engine structure
  - Docker support
- Frontend with React, TypeScript, Vite, and Material-UI
  - Basic routing and navigation
  - Layout component with header and footer
  - Home, Games, and Recommendations pages
  - API service layer
  - Docker support
- Docker Compose for full stack deployment
- Comprehensive README with project documentation
- MIT License with academic note
- .gitignore for Python and Node.js
- Contributing guidelines

### Features
- Hybrid recommendation engine architecture
  - Collaborative filtering
  - Content-based filtering
  - Knowledge-based filtering (pedagogical rules)
- Explainability system for recommendations
- Feedback loop for continuous improvement
- Catalog management capabilities

[1.0.0]: https://github.com/cristianclo/bg_recommendations/releases/tag/v1.0.0
