const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("PromiseRegistry", function () {
  let promiseRegistry;
  let owner, politician, citizen;

  beforeEach(async function () {
    [owner, politician, citizen] = await ethers.getSigners();
    
    const PromiseRegistry = await ethers.getContractFactory("PromiseRegistry");
    promiseRegistry = await PromiseRegistry.deploy();
    await promiseRegistry.deployed();
  });

  describe("Promise Registration", function () {
    it("Should register a new promise", async function () {
      const promiseId = ethers.utils.formatBytes32String("PROMISE-001");
      const promiseHash = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("Universal Healthcare Act"));
      const gracePeriodDays = 180;

      await expect(
        promiseRegistry.connect(politician).registerPromise(
          promiseId,
          promiseHash,
          gracePeriodDays
        )
      ).to.emit(promiseRegistry, "PromiseCreated");

      const promise = await promiseRegistry.getPromise(promiseId);
      expect(promise.promiseHash).to.equal(promiseHash);
      expect(promise.politician).to.equal(politician.address);
    });

    it("Should reject duplicate promise registration", async function () {
      const promiseId = ethers.utils.formatBytes32String("PROMISE-001");
      const promiseHash = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("Test Promise"));

      await promiseRegistry.connect(politician).registerPromise(
        promiseId,
        promiseHash,
        180
      );

      await expect(
        promiseRegistry.connect(politician).registerPromise(
          promiseId,
          promiseHash,
          180
        )
      ).to.be.revertedWith("Promise already exists");
    });
  });

  describe("Vote Aggregation", function () {
    let promiseId;
    let promiseHash;

    beforeEach(async function () {
      promiseId = ethers.utils.formatBytes32String("PROMISE-002");
      promiseHash = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("Test Promise"));
      
      await promiseRegistry.connect(politician).registerPromise(
        promiseId,
        promiseHash,
        0 // No grace period for testing
      );
    });

    it("Should accept vote aggregates", async function () {
      const votesKept = 100;
      const votesBroken = 20;
      const merkleRoot = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("merkle-root"));
      const nullifiers = [
        ethers.utils.keccak256(ethers.utils.toUtf8Bytes("nullifier-1")),
        ethers.utils.keccak256(ethers.utils.toUtf8Bytes("nullifier-2"))
      ];

      await expect(
        promiseRegistry.submitVoteAggregate(
          promiseId,
          votesKept,
          votesBroken,
          merkleRoot,
          nullifiers
        )
      ).to.emit(promiseRegistry, "VotesAggregated");

      const promise = await promiseRegistry.getPromise(promiseId);
      expect(promise.votesKept).to.equal(votesKept);
      expect(promise.votesBroken).to.equal(votesBroken);
    });

    it("Should prevent nullifier reuse", async function () {
      const nullifier = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("nullifier-unique"));
      const merkleRoot = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("merkle-root"));

      await promiseRegistry.submitVoteAggregate(
        promiseId,
        50,
        10,
        merkleRoot,
        [nullifier]
      );

      await expect(
        promiseRegistry.submitVoteAggregate(
          promiseId,
          50,
          10,
          merkleRoot,
          [nullifier]
        )
      ).to.be.revertedWith("Nullifier already used");
    });
  });

  describe("Status Finalization", function () {
    let promiseId;

    beforeEach(async function () {
      promiseId = ethers.utils.formatBytes32String("PROMISE-003");
      const promiseHash = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("Test Promise"));
      
      await promiseRegistry.connect(politician).registerPromise(
        promiseId,
        promiseHash,
        0
      );
    });

    it("Should finalize status as KEPT when 60%+ votes kept", async function () {
      const merkleRoot = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("merkle-root"));
      
      await promiseRegistry.submitVoteAggregate(
        promiseId,
        70,  // 70% kept
        30,  // 30% broken
        merkleRoot,
        [ethers.utils.keccak256(ethers.utils.toUtf8Bytes("nullifier-1"))]
      );

      await promiseRegistry.finalizeStatus(promiseId);
      
      const promise = await promiseRegistry.getPromise(promiseId);
      expect(promise.status).to.equal(1); // Status.Kept
    });

    it("Should finalize status as BROKEN when 60%+ votes broken", async function () {
      const merkleRoot = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("merkle-root"));
      
      await promiseRegistry.submitVoteAggregate(
        promiseId,
        20,  // 20% kept
        80,  // 80% broken
        merkleRoot,
        [ethers.utils.keccak256(ethers.utils.toUtf8Bytes("nullifier-2"))]
      );

      await promiseRegistry.finalizeStatus(promiseId);
      
      const promise = await promiseRegistry.getPromise(promiseId);
      expect(promise.status).to.equal(2); // Status.Broken
    });

    it("Should finalize status as DISPUTED when no consensus", async function () {
      const merkleRoot = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("merkle-root"));
      
      await promiseRegistry.submitVoteAggregate(
        promiseId,
        50,  // 50% kept
        50,  // 50% broken
        merkleRoot,
        [ethers.utils.keccak256(ethers.utils.toUtf8Bytes("nullifier-3"))]
      );

      await promiseRegistry.finalizeStatus(promiseId);
      
      const promise = await promiseRegistry.getPromise(promiseId);
      expect(promise.status).to.equal(3); // Status.Disputed
    });
  });

  describe("Merkle Proof Verification", function () {
    it("Should verify valid Merkle proof", async function () {
      const promiseId = ethers.utils.formatBytes32String("PROMISE-004");
      const promiseHash = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("Test Promise"));
      
      await promiseRegistry.connect(politician).registerPromise(
        promiseId,
        promiseHash,
        0
      );

      // Create a simple Merkle tree
      const leaf1 = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("vote-1"));
      const leaf2 = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("vote-2"));
      
      // Simple 2-leaf tree - root is hash of the two leaves
      const merkleRoot = leaf1 <= leaf2
        ? ethers.utils.keccak256(ethers.utils.concat([leaf1, leaf2]))
        : ethers.utils.keccak256(ethers.utils.concat([leaf2, leaf1]));

      await promiseRegistry.submitVoteAggregate(
        promiseId,
        2,
        0,
        merkleRoot,
        [ethers.utils.keccak256(ethers.utils.toUtf8Bytes("nullifier-4"))]
      );

      // Verify leaf1 is in the tree
      const proof = [leaf2];
      const isValid = await promiseRegistry.verifyVoteInclusion(
        promiseId,
        leaf1,
        proof
      );

      expect(isValid).to.be.true;
    });
  });
});
