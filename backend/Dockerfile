# Basic Node.js backend Dockerfile
FROM node:18-alpine

WORKDIR /app

# Install dependencies (copy package files first to leverage layer caching)
COPY package*.json ./
RUN npm ci --only=production

# Copy application source
COPY . .

EXPOSE 3000
ENV NODE_ENV=production

# Adjust command to your app's entrypoint if different
CMD ["node", "index.js"]