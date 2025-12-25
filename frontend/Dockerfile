FROM node:20-alpine

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /app

# Copy package files
COPY package.json pnpm-lock.yaml* ./

# Install dependencies
RUN pnpm install

# Copy source files
COPY . .

# Build arguments for Vite environment variables
ARG VITE_API_URL=http://localhost:8000
ARG VITE_BLOCKCHAIN_RPC=http://localhost:8545
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_BLOCKCHAIN_RPC=$VITE_BLOCKCHAIN_RPC

# Expose port
EXPOSE 3000

# Run dev server with host binding for container access
CMD ["pnpm", "run", "dev", "--host", "0.0.0.0", "--port", "3000"]
