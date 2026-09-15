# Contributing to Netrava

We welcome contributions from engineers, researchers, and public safety specialists to help build the open-source standard for government video intelligence.

## Development Workflow

1. **Prerequisites**:
   - Python 3.11+ (managed via `uv` or `venv`)
   - Node.js 20+ & `pnpm`
   - Docker & Docker Compose
   - FFmpeg 6.0+

2. **Quick Start**:
   ```bash
   # Clone the repository
   git clone https://github.com/SH20RAJ/Netrava.git
   cd Netrava

   # Setup environment and dependencies
   make setup

   # Start infrastructure (Postgres/PostGIS, Redis, MediaMTX, MinIO)
   make up

   # Seed database with Gujarat reference dataset
   make seed

   # Launch services in development mode
   make dev
   ```

3. **Code Standards**:
   - Backend: Python code must pass `ruff check` and `mypy` typechecking. Use asynchronous SQLAlchemy 2.0 and Pydantic v2 schemas.
   - Frontend: TypeScript strict mode. Clean component boundaries using Tailwind CSS and shadcn/ui.
   - Commits: Use Conventional Commits (`feat:`, `fix:`, `docs:`, `perf:`, `test:`, `refactor:`).

4. **Testing**:
   ```bash
   make test
   ```
