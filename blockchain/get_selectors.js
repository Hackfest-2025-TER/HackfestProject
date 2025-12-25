const { ethers } = require("hardhat");

async function main() {
  // Function signatures
  const functions = [
    "registerPolitician(uint256)",
    "isPoliticianWallet(uint256,address)",
    "getPolitician(uint256)",
    "submitManifesto(uint256,bytes32)",
    "verifyManifesto(uint256,bytes32)",
    "lookupHash(bytes32)",
    "getManifesto(bytes32)",
    "getPoliticianManifestos(uint256)",
    "updateWallet(uint256,address)",
    "computeHash(string)"
  ];

  console.log("Function Selectors for ManifestoRegistry:\n");
  console.log("Function Name                              | Selector");
  console.log("-------------------------------------------|----------");

  for (const func of functions) {
    const selector = ethers.utils.id(func).slice(0, 10);
    console.log(`${func.padEnd(43)}| ${selector}`);
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
