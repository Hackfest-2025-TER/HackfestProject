const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("ManifestoRegistry", function () {
  let registry;
  let representative1, representative2, citizen;
  const REPRESENTATIVE_ID_1 = 1;
  const REPRESENTATIVE_ID_2 = 2;

  beforeEach(async function () {
    [representative1, representative2, citizen] = await ethers.getSigners();

    const ManifestoRegistry = await ethers.getContractFactory("ManifestoRegistry");
    registry = await ManifestoRegistry.deploy();
    await registry.deployed();
  });

  describe("Representative Registration", function () {
    it("should register a new representative", async function () {
      const tx = await registry.connect(representative1).registerRepresentative(REPRESENTATIVE_ID_1);
      await tx.wait();

      const [wallet, count, registered] = await registry.getRepresentative(REPRESENTATIVE_ID_1);
      expect(wallet).to.equal(representative1.address);
      expect(count).to.equal(0);
      expect(registered).to.be.true;
    });

    it("should reject duplicate registration", async function () {
      await registry.connect(representative1).registerRepresentative(REPRESENTATIVE_ID_1);

      await expect(
        registry.connect(representative2).registerRepresentative(REPRESENTATIVE_ID_1)
      ).to.be.revertedWithCustomError(registry, "RepresentativeAlreadyRegistered");
    });

    it("should update totalRepresentatives counter", async function () {
      expect(await registry.totalRepresentatives()).to.equal(0);

      await registry.connect(representative1).registerRepresentative(REPRESENTATIVE_ID_1);
      expect(await registry.totalRepresentatives()).to.equal(1);

      await registry.connect(representative2).registerRepresentative(REPRESENTATIVE_ID_2);
      expect(await registry.totalRepresentatives()).to.equal(2);
    });
  });

  describe("Wallet Update (Key Rotation)", function () {
    beforeEach(async function () {
      await registry.connect(representative1).registerRepresentative(REPRESENTATIVE_ID_1);
    });

    it("should allow representative to update wallet", async function () {
      const tx = await registry.connect(representative1).updateWallet(REPRESENTATIVE_ID_1, representative2.address);
      await tx.wait();

      const [wallet] = await registry.getRepresentative(REPRESENTATIVE_ID_1);
      expect(wallet).to.equal(representative2.address);
    });

    it("should reject update from non-owner", async function () {
      await expect(
        registry.connect(citizen).updateWallet(REPRESENTATIVE_ID_1, citizen.address)
      ).to.be.revertedWithCustomError(registry, "NotRepresentativeWallet");
    });

    it("should reject update to zero address", async function () {
      await expect(
        registry.connect(representative1).updateWallet(REPRESENTATIVE_ID_1, ethers.constants.AddressZero)
      ).to.be.revertedWithCustomError(registry, "InvalidAddress");
    });
  });

  describe("Manifesto Submission", function () {
    const manifestoText = "I promise to build 100 schools by 2025";
    let manifestoHash;

    beforeEach(async function () {
      await registry.connect(representative1).registerRepresentative(REPRESENTATIVE_ID_1);
      manifestoHash = ethers.utils.keccak256(ethers.utils.toUtf8Bytes(manifestoText));
    });

    it("should submit a manifesto successfully", async function () {
      const tx = await registry.connect(representative1).submitManifesto(REPRESENTATIVE_ID_1, manifestoHash);
      const receipt = await tx.wait();

      expect(await registry.totalManifestos()).to.equal(1);
    });

    it("should reject submission from non-owner wallet", async function () {
      await expect(
        registry.connect(citizen).submitManifesto(REPRESENTATIVE_ID_1, manifestoHash)
      ).to.be.revertedWithCustomError(registry, "NotRepresentativeWallet");
    });

    it("should reject submission from unregistered representative", async function () {
      await expect(
        registry.connect(representative2).submitManifesto(REPRESENTATIVE_ID_2, manifestoHash)
      ).to.be.revertedWithCustomError(registry, "RepresentativeNotRegistered");
    });

    it("should reject duplicate hash", async function () {
      await registry.connect(representative1).submitManifesto(REPRESENTATIVE_ID_1, manifestoHash);

      // Same representative, same hash
      await expect(
        registry.connect(representative1).submitManifesto(REPRESENTATIVE_ID_1, manifestoHash)
      ).to.be.revertedWithCustomError(registry, "ManifestoAlreadyExists");

      // Different representative, same hash (also rejected - global uniqueness)
      await registry.connect(representative2).registerRepresentative(REPRESENTATIVE_ID_2);
      await expect(
        registry.connect(representative2).submitManifesto(REPRESENTATIVE_ID_2, manifestoHash)
      ).to.be.revertedWithCustomError(registry, "ManifestoAlreadyExists");
    });

    it("should reject zero hash", async function () {
      await expect(
        registry.connect(representative1).submitManifesto(REPRESENTATIVE_ID_1, ethers.constants.HashZero)
      ).to.be.revertedWithCustomError(registry, "InvalidHash");
    });

    it("should track multiple manifestos per representative", async function () {
      const hash1 = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("Promise 1"));
      const hash2 = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("Promise 2"));
      const hash3 = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("Promise 3"));

      await registry.connect(representative1).submitManifesto(REPRESENTATIVE_ID_1, hash1);
      await registry.connect(representative1).submitManifesto(REPRESENTATIVE_ID_1, hash2);
      await registry.connect(representative1).submitManifesto(REPRESENTATIVE_ID_1, hash3);

      const [, count] = await registry.getRepresentative(REPRESENTATIVE_ID_1);
      expect(count).to.equal(3);

      const [hashes] = await registry.getRepresentativeManifestos(REPRESENTATIVE_ID_1);
      expect(hashes.length).to.equal(3);
      expect(hashes[0]).to.equal(hash1);
      expect(hashes[1]).to.equal(hash2);
      expect(hashes[2]).to.equal(hash3);
    });
  });

  describe("Manifesto Verification", function () {
    const manifestoText = "I promise to reduce taxes by 10%";
    let manifestoHash;

    beforeEach(async function () {
      await registry.connect(representative1).registerRepresentative(REPRESENTATIVE_ID_1);
      manifestoHash = ethers.utils.keccak256(ethers.utils.toUtf8Bytes(manifestoText));
      await registry.connect(representative1).submitManifesto(REPRESENTATIVE_ID_1, manifestoHash);
    });

    it("should verify authentic manifesto", async function () {
      const [valid, submittedAt, blockNumber] = await registry.verifyManifesto(
        REPRESENTATIVE_ID_1,
        manifestoHash
      );

      expect(valid).to.be.true;
      expect(submittedAt).to.be.gt(0);
      expect(blockNumber).to.be.gt(0);
    });

    it("should reject tampered manifesto", async function () {
      const tamperedHash = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("I promise to INCREASE taxes"));

      const [valid, submittedAt, blockNumber] = await registry.verifyManifesto(
        REPRESENTATIVE_ID_1,
        tamperedHash
      );

      expect(valid).to.be.false;
      expect(submittedAt).to.equal(0);
      expect(blockNumber).to.equal(0);
    });

    it("should reject verification for wrong representative", async function () {
      await registry.connect(representative2).registerRepresentative(REPRESENTATIVE_ID_2);

      const [valid] = await registry.verifyManifesto(REPRESENTATIVE_ID_2, manifestoHash);
      expect(valid).to.be.false;
    });

    it("should lookup hash and return author", async function () {
      const [exists, representativeId, submittedAt] = await registry.lookupHash(manifestoHash);

      expect(exists).to.be.true;
      expect(representativeId).to.equal(REPRESENTATIVE_ID_1);
      expect(submittedAt).to.be.gt(0);
    });

    it("should return false for non-existent hash", async function () {
      const fakeHash = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("Never submitted"));
      const [exists] = await registry.lookupHash(fakeHash);
      expect(exists).to.be.false;
    });
  });

  describe("View Functions", function () {
    beforeEach(async function () {
      await registry.connect(representative1).registerRepresentative(REPRESENTATIVE_ID_1);
    });

    it("should get manifesto by index", async function () {
      const manifestoHash = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("Test manifesto"));
      await registry.connect(representative1).submitManifesto(REPRESENTATIVE_ID_1, manifestoHash);

      const [hash, submittedAt, blockNumber] = await registry.getManifesto(REPRESENTATIVE_ID_1, 0);

      expect(hash).to.equal(manifestoHash);
      expect(submittedAt).to.be.gt(0);
      expect(blockNumber).to.be.gt(0);
    });

    it("should revert for non-existent manifesto index", async function () {
      await expect(
        registry.getManifesto(REPRESENTATIVE_ID_1, 999)
      ).to.be.revertedWithCustomError(registry, "ManifestoNotFound");
    });

    it("should check if address is representative wallet", async function () {
      expect(await registry.isRepresentativeWallet(REPRESENTATIVE_ID_1, representative1.address)).to.be.true;
      expect(await registry.isRepresentativeWallet(REPRESENTATIVE_ID_1, citizen.address)).to.be.false;
      expect(await registry.isRepresentativeWallet(REPRESENTATIVE_ID_2, representative1.address)).to.be.false;
    });

    it("should compute hash correctly", async function () {
      const text = "Hello, blockchain!";
      const expectedHash = ethers.utils.keccak256(ethers.utils.toUtf8Bytes(text));
      const contractHash = await registry.computeHash(text);

      expect(contractHash).to.equal(expectedHash);
    });
  });

  describe("Immutability", function () {
    it("manifesto data should be permanent after submission", async function () {
      await registry.connect(representative1).registerRepresentative(REPRESENTATIVE_ID_1);
      const manifestoHash = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("Permanent promise"));

      await registry.connect(representative1).submitManifesto(REPRESENTATIVE_ID_1, manifestoHash);

      // Get initial data
      const [hash1, time1] = await registry.getManifesto(REPRESENTATIVE_ID_1, 0);

      // Mine some blocks
      await ethers.provider.send("evm_mine", []);
      await ethers.provider.send("evm_mine", []);

      // Data should be unchanged
      const [hash2, time2] = await registry.getManifesto(REPRESENTATIVE_ID_1, 0);

      expect(hash1).to.equal(hash2);
      expect(time1).to.equal(time2);
    });
  });
});
