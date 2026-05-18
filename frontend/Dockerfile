# ── Stage 1: Build ───────────────────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

# Accept build-time env vars (injected by docker-compose build args)
ARG VITE_API_URL=http://localhost:8000
ARG VITE_WS_URL=ws://localhost:8000
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_WS_URL=$VITE_WS_URL

COPY package.json ./
RUN npm install --legacy-peer-deps

COPY . .
RUN npm run build

# ── Stage 2: Serve with Nginx ─────────────────────────────────────────────────
FROM nginx:1.25-alpine

# Custom nginx config for SPA routing
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
