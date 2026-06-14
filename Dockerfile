FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Working directory
WORKDIR /app

# Dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-cache

# Copy source
COPY . .

# Expose application port
EXPOSE 8000

# Run FastAPI
CMD ["/app/.venv/bin/fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "8000"]