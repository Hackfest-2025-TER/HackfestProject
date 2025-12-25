#!/bin/bash

# Test script for ManifestoRegistry contract
# ManifestoRegistry: 0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0

CONTRACT_ADDRESS="0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0"
DEPLOYER_ADDRESS="0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
POLITICIAN_ID="1"
CONTENT_HASH="0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"

echo "====================================="
echo "Testing ManifestoRegistry Contract"
echo "====================================="
echo ""

# Test 1: Register a politician
echo "Test 1: Register Politician with ID ${POLITICIAN_ID}"
echo "Calling registerPolitician(${POLITICIAN_ID})..."
curl -X POST http://localhost:8545 \
  -H "Content-Type: application/json" \
  --data '{
    "jsonrpc":"2.0",
    "method":"eth_sendTransaction",
    "params":[{
      "from":"'"${DEPLOYER_ADDRESS}"'",
      "to":"'"${CONTRACT_ADDRESS}"'",
      "data":"0x3bb937700000000000000000000000000000000000000000000000000000000000000001",
      "gas":"0x100000"
    }],
    "id":1
  }' | jq .

echo ""
echo "Waiting for transaction to be mined..."
sleep 2

# Test 2: Check if wallet is registered
echo ""
echo "Test 2: Check if wallet is registered for politician"
echo "Calling isPoliticianWallet(${POLITICIAN_ID}, ${DEPLOYER_ADDRESS})..."
curl -X POST http://localhost:8545 \
  -H "Content-Type: application/json" \
  --data '{
    "jsonrpc":"2.0",
    "method":"eth_call",
    "params":[{
      "to":"'"${CONTRACT_ADDRESS}"'",
      "data":"0xdd2a783a0000000000000000000000000000000000000000000000000000000000000001000000000000000000000000f39fd6e51aad88f6f4ce6ab8827279cfffb92266"
    }, "latest"],
    "id":2
  }' | jq .

# Test 3: Get politician info
echo ""
echo "Test 3: Get politician info"
echo "Calling getPolitician(${POLITICIAN_ID})..."
curl -X POST http://localhost:8545 \
  -H "Content-Type: application/json" \
  --data '{
    "jsonrpc":"2.0",
    "method":"eth_call",
    "params":[{
      "to":"'"${CONTRACT_ADDRESS}"'",
      "data":"0x7d8d5c9b0000000000000000000000000000000000000000000000000000000000000001"
    }, "latest"],
    "id":3
  }' | jq .

# Test 4: Submit a manifesto
echo ""
echo "Test 4: Submit Manifesto"
echo "Calling submitManifesto(${POLITICIAN_ID}, ${CONTENT_HASH})..."
curl -X POST http://localhost:8545 \
  -H "Content-Type: application/json" \
  --data '{
    "jsonrpc":"2.0",
    "method":"eth_sendTransaction",
    "params":[{
      "from":"'"${DEPLOYER_ADDRESS}"'",
      "to":"'"${CONTRACT_ADDRESS}"'",
      "data":"0xd29598a900000000000000000000000000000000000000000000000000000000000000011234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
      "gas":"0x100000"
    }],
    "id":4
  }' | jq .

echo ""
echo "Waiting for transaction to be mined..."
sleep 2

# Test 5: Verify the manifesto
echo ""
echo "Test 5: Verify Manifesto"
echo "Calling verifyManifesto(${POLITICIAN_ID}, ${CONTENT_HASH})..."
curl -X POST http://localhost:8545 \
  -H "Content-Type: application/json" \
  --data '{
    "jsonrpc":"2.0",
    "method":"eth_call",
    "params":[{
      "to":"'"${CONTRACT_ADDRESS}"'",
      "data":"0x87e0150f00000000000000000000000000000000000000000000000000000000000000011234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
    }, "latest"],
    "id":5
  }' | jq .

# Test 6: Lookup by hash
echo ""
echo "Test 6: Lookup Politician by Hash"
echo "Calling lookupHash(${CONTENT_HASH})..."
curl -X POST http://localhost:8545 \
  -H "Content-Type: application/json" \
  --data '{
    "jsonrpc":"2.0",
    "method":"eth_call",
    "params":[{
      "to":"'"${CONTRACT_ADDRESS}"'",
      "data":"0x6d6d99191234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
    }, "latest"],
    "id":6
  }' | jq .

echo ""
echo "====================================="
echo "All tests completed!"
echo "====================================="
