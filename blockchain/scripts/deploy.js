const hre = require("hardhat");

async function main() {
  console.log("Deploying PromiseThread contracts...\n");

  // Get deployer account
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying with account:", deployer.address);
  console.log("Account balance:", (await deployer.provider.getBalance(deployer.address)).toString());

  // Deploy ZKVerifier
  console.log("\n1. Deploying ZKVerifier...");
  const ZKVerifier = await hre.ethers.getContractFactory("ZKVerifier");
  const zkVerifier = await ZKVerifier.deploy();
  await zkVerifier.waitForDeployment();
  const zkVerifierAddress = await zkVerifier.getAddress();
  console.log("   ZKVerifier deployed to:", zkVerifierAddress);

  // Deploy PromiseRegistry
  console.log("\n2. Deploying PromiseRegistry...");
  const PromiseRegistry = await hre.ethers.getContractFactory("PromiseRegistry");
  const promiseRegistry = await PromiseRegistry.deploy();
  await promiseRegistry.waitForDeployment();
  const promiseRegistryAddress = await promiseRegistry.getAddress();
  console.log("   PromiseRegistry deployed to:", promiseRegistryAddress);

  console.log("\n========================================");
  console.log("Deployment Complete!");
  console.log("========================================");
  console.log("ZKVerifier:", zkVerifierAddress);
  console.log("PromiseRegistry:", promiseRegistryAddress);
  console.log("========================================\n");

  // Write deployment addresses to file
  const fs = require("fs");
  const deploymentInfo = {
    network: hre.network.name,
    timestamp: new Date().toISOString(),
    contracts: {
      ZKVerifier: zkVerifierAddress,
      PromiseRegistry: promiseRegistryAddress
    }
  };
  
  fs.writeFileSync(
    "./deployments.json",
    JSON.stringify(deploymentInfo, null, 2)
  );
  console.log("Deployment info saved to deployments.json");

  // Verify contracts on explorer (if not localhost)
  if (hre.network.name !== "hardhat" && hre.network.name !== "localhost") {
    console.log("\nWaiting for block confirmations...");
    await new Promise(resolve => setTimeout(resolve, 30000)); // Wait 30 seconds
    
    console.log("Verifying contracts on explorer...");
    
    try {
      await hre.run("verify:verify", {
        address: zkVerifierAddress,
        constructorArguments: []
      });
      console.log("ZKVerifier verified!");
    } catch (e) {
      console.log("ZKVerifier verification failed:", e.message);
    }
    
    try {
      await hre.run("verify:verify", {
        address: promiseRegistryAddress,
        constructorArguments: []
      });
      console.log("PromiseRegistry verified!");
    } catch (e) {
      console.log("PromiseRegistry verification failed:", e.message);
    }
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
