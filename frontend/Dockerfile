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

# Expose port
EXPOSE 3000

# Run dev server (for demo/hackathon purposes)
CMD ["pnpm", "run", "dev"]
