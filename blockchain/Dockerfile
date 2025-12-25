FROM node:20-alpine

WORKDIR /app

# Install curl for healthcheck (better RPC testing)
RUN apk add --no-cache curl

# Copy package files
COPY package*.json pnpm-lock.yaml* ./

# Install pnpm and dependencies
RUN corepack enable && corepack prepare pnpm@latest --activate
RUN pnpm install

# Copy source files
COPY . .

# Compile contracts during build
RUN pnpm run compile

# Expose Hardhat node port
EXPOSE 8545

# Start Hardhat node listening on all interfaces
CMD ["npx", "hardhat", "node", "--hostname", "0.0.0.0"]
