FROM node:20-alpine

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /app

# Copy package files
COPY package.json ./

# Install dependencies
RUN pnpm install

# Copy source files
COPY . .

# Build the app
RUN pnpm run build

# Expose port
EXPOSE 3000

# Start the app
CMD ["node", "build"]
