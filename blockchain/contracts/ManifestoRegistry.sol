// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title ManifestoRegistry
 * @author PromiseThread Team
 * @notice Immutable registry for political manifesto commitments
 * @dev Separates manifesto storage from voting logic for security and simplicity
 * 
 * Architecture:
 * - Frontend hashes manifesto content (SHA256)
 * - Politician submits hash to blockchain (commitment)
 * - Anyone can verify a manifesto by hashing and comparing
 * - Backend stores full text but has NO authority over blockchain state
 * 
 * Security Properties:
 * - Immutable: Once submitted, manifesto hashes cannot be changed
 * - Timestamped: Block timestamp proves when commitment was made
 * - Verifiable: Anyone can independently verify authenticity
 * - Minimal: No admin functions, no upgradability, no backdoors
 */
contract ManifestoRegistry {
    
    // ============= Data Structures =============
    
    struct Manifesto {
        bytes32 contentHash;      // SHA256 hash of manifesto content
        uint256 submittedAt;      // Block timestamp when submitted
        uint256 blockNumber;      // Block number for additional verification
        bool exists;              // Whether this manifesto exists
    }
    
    struct Politician {
        address wallet;           // Politician's signing wallet
        uint256 manifestoCount;   // Number of manifestos submitted
        bool registered;          // Whether politician is registered
    }
    
    // ============= State Variables =============
    
    // Politician ID => Politician data
    mapping(uint256 => Politician) public politicians;
    
    // Politician ID => Manifesto Index => Manifesto data
    mapping(uint256 => mapping(uint256 => Manifesto)) public manifestos;
    
    // Quick lookup: hash => (politicianId, manifestoIndex)
    mapping(bytes32 => uint256) public hashToPolitician;
    mapping(bytes32 => uint256) public hashToIndex;
    mapping(bytes32 => bool) public hashExists;
    
    // Global stats
    uint256 public totalManifestos;
    uint256 public totalPoliticians;
    
    // ============= Events =============
    
    event PoliticianRegistered(
        uint256 indexed politicianId,
        address indexed wallet,
        uint256 timestamp
    );
    
    event ManifestoSubmitted(
        uint256 indexed politicianId,
        uint256 indexed manifestoIndex,
        bytes32 indexed contentHash,
        uint256 timestamp,
        uint256 blockNumber
    );
    
    event WalletUpdated(
        uint256 indexed politicianId,
        address indexed oldWallet,
        address indexed newWallet,
        uint256 timestamp
    );
    
    // ============= Errors =============
    
    error PoliticianNotRegistered(uint256 politicianId);
    error PoliticianAlreadyRegistered(uint256 politicianId);
    error NotPoliticianWallet(uint256 politicianId, address caller);
    error ManifestoAlreadyExists(bytes32 contentHash);
    error ManifestoNotFound(uint256 politicianId, uint256 index);
    error InvalidHash();
    error InvalidAddress();
    
    // ============= Modifiers =============
    
    modifier onlyPolitician(uint256 politicianId) {
        if (!politicians[politicianId].registered) {
            revert PoliticianNotRegistered(politicianId);
        }
        if (politicians[politicianId].wallet != msg.sender) {
            revert NotPoliticianWallet(politicianId, msg.sender);
        }
        _;
    }
    
    // ============= Registration =============
    
    /**
     * @notice Register a new politician with their wallet address
     * @param politicianId Unique identifier for the politician (from off-chain DB)
     * @dev Anyone can register once - the msg.sender becomes the politician's wallet
     */
    function registerPolitician(uint256 politicianId) external {
        if (politicians[politicianId].registered) {
            revert PoliticianAlreadyRegistered(politicianId);
        }
        
        politicians[politicianId] = Politician({
            wallet: msg.sender,
            manifestoCount: 0,
            registered: true
        });
        
        totalPoliticians++;
        
        emit PoliticianRegistered(politicianId, msg.sender, block.timestamp);
    }
    
    /**
     * @notice Update politician's wallet address (key rotation)
     * @param politicianId The politician's ID
     * @param newWallet The new wallet address
     * @dev Only the current wallet can update to a new one
     */
    function updateWallet(uint256 politicianId, address newWallet) 
        external 
        onlyPolitician(politicianId) 
    {
        if (newWallet == address(0)) {
            revert InvalidAddress();
        }
        
        address oldWallet = politicians[politicianId].wallet;
        politicians[politicianId].wallet = newWallet;
        
        emit WalletUpdated(politicianId, oldWallet, newWallet, block.timestamp);
    }
    
    // ============= Manifesto Submission =============
    
    /**
     * @notice Submit a manifesto hash commitment
     * @param politicianId The politician's ID
     * @param contentHash SHA256 hash of the manifesto content
     * @dev Hash is computed off-chain: keccak256(abi.encodePacked(manifestoText))
     * @return manifestoIndex The index of this manifesto for the politician
     */
    function submitManifesto(uint256 politicianId, bytes32 contentHash) 
        external 
        onlyPolitician(politicianId) 
        returns (uint256 manifestoIndex)
    {
        if (contentHash == bytes32(0)) {
            revert InvalidHash();
        }
        
        if (hashExists[contentHash]) {
            revert ManifestoAlreadyExists(contentHash);
        }
        
        manifestoIndex = politicians[politicianId].manifestoCount;
        
        manifestos[politicianId][manifestoIndex] = Manifesto({
            contentHash: contentHash,
            submittedAt: block.timestamp,
            blockNumber: block.number,
            exists: true
        });
        
        // Update lookup mappings
        hashToPolitician[contentHash] = politicianId;
        hashToIndex[contentHash] = manifestoIndex;
        hashExists[contentHash] = true;
        
        // Update counts
        politicians[politicianId].manifestoCount++;
        totalManifestos++;
        
        emit ManifestoSubmitted(
            politicianId,
            manifestoIndex,
            contentHash,
            block.timestamp,
            block.number
        );
        
        return manifestoIndex;
    }
    
    // ============= Verification Functions =============
    
    /**
     * @notice Verify if a manifesto hash was submitted by a politician
     * @param politicianId The politician's ID
     * @param contentHash The hash to verify
     * @return valid True if the hash matches a submitted manifesto
     * @return submittedAt Timestamp when the manifesto was submitted (0 if not found)
     * @return blockNumber Block number when submitted (0 if not found)
     */
    function verifyManifesto(uint256 politicianId, bytes32 contentHash) 
        external 
        view 
        returns (bool valid, uint256 submittedAt, uint256 blockNumber) 
    {
        if (!hashExists[contentHash]) {
            return (false, 0, 0);
        }
        
        if (hashToPolitician[contentHash] != politicianId) {
            return (false, 0, 0);
        }
        
        uint256 index = hashToIndex[contentHash];
        Manifesto storage m = manifestos[politicianId][index];
        
        return (true, m.submittedAt, m.blockNumber);
    }
    
    /**
     * @notice Verify a hash exists and get its author
     * @param contentHash The hash to look up
     * @return exists True if hash exists in registry
     * @return politicianId The politician who submitted it
     * @return submittedAt Timestamp when submitted
     */
    function lookupHash(bytes32 contentHash) 
        external 
        view 
        returns (bool exists, uint256 politicianId, uint256 submittedAt) 
    {
        if (!hashExists[contentHash]) {
            return (false, 0, 0);
        }
        
        politicianId = hashToPolitician[contentHash];
        uint256 index = hashToIndex[contentHash];
        submittedAt = manifestos[politicianId][index].submittedAt;
        
        return (true, politicianId, submittedAt);
    }
    
    // ============= View Functions =============
    
    /**
     * @notice Get manifesto details by politician ID and index
     * @param politicianId The politician's ID
     * @param index The manifesto index
     * @return contentHash The manifesto's content hash
     * @return submittedAt Timestamp when submitted
     * @return blockNumber Block number when submitted
     */
    function getManifesto(uint256 politicianId, uint256 index) 
        external 
        view 
        returns (bytes32 contentHash, uint256 submittedAt, uint256 blockNumber) 
    {
        if (!manifestos[politicianId][index].exists) {
            revert ManifestoNotFound(politicianId, index);
        }
        
        Manifesto storage m = manifestos[politicianId][index];
        return (m.contentHash, m.submittedAt, m.blockNumber);
    }
    
    /**
     * @notice Get all manifesto hashes for a politician
     * @param politicianId The politician's ID
     * @return hashes Array of content hashes
     * @return timestamps Array of submission timestamps
     */
    function getPoliticianManifestos(uint256 politicianId) 
        external 
        view 
        returns (bytes32[] memory hashes, uint256[] memory timestamps) 
    {
        uint256 count = politicians[politicianId].manifestoCount;
        hashes = new bytes32[](count);
        timestamps = new uint256[](count);
        
        for (uint256 i = 0; i < count; i++) {
            hashes[i] = manifestos[politicianId][i].contentHash;
            timestamps[i] = manifestos[politicianId][i].submittedAt;
        }
        
        return (hashes, timestamps);
    }
    
    /**
     * @notice Get politician info
     * @param politicianId The politician's ID
     * @return wallet The politician's wallet address
     * @return manifestoCount Number of manifestos submitted
     * @return registered Whether the politician is registered
     */
    function getPolitician(uint256 politicianId) 
        external 
        view 
        returns (address wallet, uint256 manifestoCount, bool registered) 
    {
        Politician storage p = politicians[politicianId];
        return (p.wallet, p.manifestoCount, p.registered);
    }
    
    /**
     * @notice Check if an address is the wallet for a politician
     * @param politicianId The politician's ID
     * @param wallet The address to check
     * @return True if the address is the politician's wallet
     */
    function isPoliticianWallet(uint256 politicianId, address wallet) 
        external 
        view 
        returns (bool) 
    {
        return politicians[politicianId].registered && 
               politicians[politicianId].wallet == wallet;
    }
    
    // ============= Helper Functions =============
    
    /**
     * @notice Compute hash of manifesto text (helper for frontend)
     * @param manifestoText The manifesto text to hash
     * @return The keccak256 hash
     * @dev This is a convenience function - hashing should be done off-chain
     */
    function computeHash(string calldata manifestoText) 
        external 
        pure 
        returns (bytes32) 
    {
        return keccak256(abi.encodePacked(manifestoText));
    }
}
