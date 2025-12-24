FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json pnpm-lock.yaml* ./

# Install pnpm and dependencies
RUN corepack enable && corepack prepare pnpm@latest --activate
RUN pnpm install

# Copy source files
COPY . .

# Expose Hardhat node port
EXPOSE 8545

# Compile and start at runtime (not during build)
CMD ["sh", "-c", "pnpm run compile && pnpm run node"]
