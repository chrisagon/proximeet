# Étape 1: Build
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json ./
RUN npm install

COPY . ./
RUN npm run build

# Étape 2: Production
FROM node:20-alpine

WORKDIR /app

# Copie seulement le build de production
COPY --from=builder /app/.output ./.output

EXPOSE 3000

# Lance le serveur Nitro en production (pas de HMR/WebSocket)
CMD ["node", ".output/server/index.mjs"]
