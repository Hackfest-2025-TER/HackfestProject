// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title PromiseRegistry
 * @dev Stores promise hashes and vote aggregates on-chain for immutability
 */
contract PromiseRegistry {
    
    struct Promise {
        bytes32 promiseHash;
        address politician;
        uint256 createdAt;
        uint256 gracePeriodEnd;
        uint256 votesKept;
        uint256 votesBroken;
        Status status;
        bytes32 merkleRoot;
    }
    
    enum Status { Pending, Kept, Broken, Disputed }
    
    // Promise ID => Promise data
    mapping(bytes32 => Promise) public promises;
    
    // Nullifier tracking to prevent double voting
    mapping(bytes32 => bool) public usedNullifiers;
    
    // Merkle roots for vote batches
    mapping(bytes32 => bytes32) public voteMerkleRoots;
    
    // Events
    event PromiseCreated(
        bytes32 indexed promiseId,
        bytes32 promiseHash,
        address indexed politician,
        uint256 gracePeriodEnd
    );
    
    event VotesAggregated(
        bytes32 indexed promiseId,
        uint256 votesKept,
        uint256 votesBroken,
        bytes32 merkleRoot
    );
    
    event StatusChanged(
        bytes32 indexed promiseId,
        Status oldStatus,
        Status newStatus
    );
    
    // Modifiers
    modifier onlyAfterGracePeriod(bytes32 promiseId) {
        require(
            block.timestamp >= promises[promiseId].gracePeriodEnd,
            "Grace period not ended"
        );
        _;
    }
    
    /**
     * @dev Register a new promise on-chain
     * @param promiseId Unique identifier for the promise
     * @param promiseHash Hash of the promise content
     * @param gracePeriodDays Number of days before voting opens
     */
    function registerPromise(
        bytes32 promiseId,
        bytes32 promiseHash,
        uint256 gracePeriodDays
    ) external {
        require(promises[promiseId].createdAt == 0, "Promise already exists");
        
        promises[promiseId] = Promise({
            promiseHash: promiseHash,
            politician: msg.sender,
            createdAt: block.timestamp,
            gracePeriodEnd: block.timestamp + (gracePeriodDays * 1 days),
            votesKept: 0,
            votesBroken: 0,
            status: Status.Pending,
            merkleRoot: bytes32(0)
        });
        
        emit PromiseCreated(
            promiseId,
            promiseHash,
            msg.sender,
            block.timestamp + (gracePeriodDays * 1 days)
        );
    }
    
    /**
     * @dev Submit aggregated votes with Merkle root
     * @param promiseId Promise being voted on
     * @param votesKept Number of "kept" votes in this batch
     * @param votesBroken Number of "broken" votes in this batch
     * @param merkleRoot Merkle root of all individual votes
     * @param nullifiers Array of nullifier hashes to mark as used
     */
    function submitVoteAggregate(
        bytes32 promiseId,
        uint256 votesKept,
        uint256 votesBroken,
        bytes32 merkleRoot,
        bytes32[] calldata nullifiers
    ) external onlyAfterGracePeriod(promiseId) {
        require(promises[promiseId].createdAt != 0, "Promise not found");
        
        // Mark nullifiers as used
        for (uint i = 0; i < nullifiers.length; i++) {
            require(!usedNullifiers[nullifiers[i]], "Nullifier already used");
            usedNullifiers[nullifiers[i]] = true;
        }
        
        // Update vote counts
        promises[promiseId].votesKept += votesKept;
        promises[promiseId].votesBroken += votesBroken;
        promises[promiseId].merkleRoot = merkleRoot;
        
        emit VotesAggregated(
            promiseId,
            promises[promiseId].votesKept,
            promises[promiseId].votesBroken,
            merkleRoot
        );
    }
    
    /**
     * @dev Finalize promise status based on vote consensus
     * @param promiseId Promise to finalize
     */
    function finalizeStatus(bytes32 promiseId) external onlyAfterGracePeriod(promiseId) {
        Promise storage p = promises[promiseId];
        require(p.status == Status.Pending, "Already finalized");
        
        uint256 totalVotes = p.votesKept + p.votesBroken;
        require(totalVotes > 0, "No votes cast");
        
        Status oldStatus = p.status;
        
        // 60% consensus threshold
        if (p.votesKept * 100 >= totalVotes * 60) {
            p.status = Status.Kept;
        } else if (p.votesBroken * 100 >= totalVotes * 60) {
            p.status = Status.Broken;
        } else {
            p.status = Status.Disputed;
        }
        
        emit StatusChanged(promiseId, oldStatus, p.status);
    }
    
    /**
     * @dev Verify a vote was included in a batch using Merkle proof
     * @param promiseId Promise the vote was for
     * @param voteHash Hash of the individual vote
     * @param proof Merkle proof path
     * @return bool Whether the vote was included
     */
    function verifyVoteInclusion(
        bytes32 promiseId,
        bytes32 voteHash,
        bytes32[] calldata proof
    ) external view returns (bool) {
        bytes32 computedHash = voteHash;
        
        for (uint i = 0; i < proof.length; i++) {
            if (computedHash <= proof[i]) {
                computedHash = keccak256(abi.encodePacked(computedHash, proof[i]));
            } else {
                computedHash = keccak256(abi.encodePacked(proof[i], computedHash));
            }
        }
        
        return computedHash == promises[promiseId].merkleRoot;
    }
    
    /**
     * @dev Check if a nullifier has been used
     * @param nullifier Nullifier hash to check
     */
    function isNullifierUsed(bytes32 nullifier) external view returns (bool) {
        return usedNullifiers[nullifier];
    }
    
    /**
     * @dev Get promise details
     * @param promiseId Promise ID
     */
    function getPromise(bytes32 promiseId) external view returns (
        bytes32 promiseHash,
        address politician,
        uint256 createdAt,
        uint256 gracePeriodEnd,
        uint256 votesKept,
        uint256 votesBroken,
        Status status,
        bytes32 merkleRoot
    ) {
        Promise storage p = promises[promiseId];
        return (
            p.promiseHash,
            p.politician,
            p.createdAt,
            p.gracePeriodEnd,
            p.votesKept,
            p.votesBroken,
            p.status,
            p.merkleRoot
        );
    }
    
    /**
     * @dev Calculate consensus percentage
     * @param promiseId Promise ID
     */
    function getConsensusPercentage(bytes32 promiseId) external view returns (
        uint256 keptPercentage,
        uint256 brokenPercentage
    ) {
        Promise storage p = promises[promiseId];
        uint256 total = p.votesKept + p.votesBroken;
        
        if (total == 0) {
            return (0, 0);
        }
        
        return (
            (p.votesKept * 100) / total,
            (p.votesBroken * 100) / total
        );
    }
}
