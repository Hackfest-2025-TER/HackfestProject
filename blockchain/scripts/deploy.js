const hre = require("hardhat");

async function main() {
  console.log("Deploying WaachaPatra contracts...\n");

  // Get deployer account
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying with account:", deployer.address);
  console.log("Account balance:", (await deployer.getBalance()).toString());

  // Deploy ZKVerifier
  console.log("\n1. Deploying ZKVerifier...");
  const ZKVerifier = await hre.ethers.getContractFactory("ZKVerifier");
  const zkVerifier = await ZKVerifier.deploy();
  await zkVerifier.deployed();
  console.log("   ZKVerifier deployed to:", zkVerifier.address);

  // Deploy ManifestoRegistry (NEW - clean manifesto contract)
  console.log("\n2. Deploying ManifestoRegistry...");
  const ManifestoRegistry = await hre.ethers.getContractFactory("ManifestoRegistry");
  const manifestoRegistry = await ManifestoRegistry.deploy();
  await manifestoRegistry.deployed();
  console.log("   ManifestoRegistry deployed to:", manifestoRegistry.address);

  // Deploy PromiseRegistry (legacy - for voting)
  console.log("\n3. Deploying PromiseRegistry (voting)...");
  const PromiseRegistry = await hre.ethers.getContractFactory("PromiseRegistry");
  const promiseRegistry = await PromiseRegistry.deploy();
  await promiseRegistry.deployed();
  console.log("   PromiseRegistry deployed to:", promiseRegistry.address);

  console.log("\n========================================");
  console.log("Deployment Complete!");
  console.log("========================================");
  console.log("ZKVerifier:", zkVerifier.address);
  console.log("ManifestoRegistry:", manifestoRegistry.address);
  console.log("PromiseRegistry:", promiseRegistry.address);
  console.log("========================================\n");

  // Write deployment addresses to file
  const fs = require("fs");
  const deploymentInfo = {
    network: hre.network.name,
    timestamp: new Date().toISOString(),
    contracts: {
      ZKVerifier: zkVerifier.address,
      ManifestoRegistry: manifestoRegistry.address,
      PromiseRegistry: promiseRegistry.address
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
        address: zkVerifier.address,
        constructorArguments: []
      });
      console.log("ZKVerifier verified!");
    } catch (e) {
      console.log("ZKVerifier verification failed:", e.message);
    }
    
    try {
      await hre.run("verify:verify", {
        address: promiseRegistry.address,
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
