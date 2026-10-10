# ---------- Stage 1: build the React app ----------
FROM node:22-alpine AS frontend-build
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ---------- Stage 2: Python backend + the built frontend ----------
FROM python:3.12-slim
WORKDIR /app/backend

ENV PYTHONUNBUFFERED=1 \
    MPLCONFIGDIR=/app/.cache/matplotlib

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Build matplotlib's font cache now, so the first chart is not slow
RUN python -c "import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt; plt.figure(); plt.close()"

COPY backend/app ./app
COPY backend/sample_data ./data/uploads
COPY --from=frontend-build /frontend/dist ./static
RUN mkdir -p data/charts

EXPOSE 7860
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-7860} --proxy-headers --forwarded-allow-ips='*'"]