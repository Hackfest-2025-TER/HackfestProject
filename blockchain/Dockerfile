FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source files
COPY . .

# Compile contracts
RUN npx hardhat compile

# Expose Hardhat node port
EXPOSE 8545

# Start Hardhat node
CMD ["npx", "hardhat", "node"]
