# Stage 1: Build frontend
FROM node:20-alpine AS frontend-build

WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# Stage 2: Backend + Nginx
FROM python:3.12-slim

RUN apt-get update && apt-get install -y nginx gettext-base && rm -rf /var/lib/apt/lists/*
RUN pip install uv

WORKDIR /app

# Backend
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --no-dev
COPY backend/ .

# Frontend build output
COPY --from=frontend-build /app/frontend/dist /usr/share/nginx/html

# Nginx config (template with $PORT placeholder)
COPY nginx.conf /etc/nginx/templates/default.conf.template
RUN rm -f /etc/nginx/conf.d/default.conf

# Ensure data directory exists
RUN mkdir -p /app/data

EXPOSE 8000

# Start both nginx and uvicorn
# nginx uses /etc/nginx/templates/ which auto-substitutes $PORT via envsubst
CMD sh -c "envsubst '\$PORT' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf && nginx && uv run uvicorn app.main:app --host 127.0.0.1 --port 8000"
