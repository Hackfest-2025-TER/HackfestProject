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
 * - Representative submits hash to blockchain (commitment)
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
    
    struct Representative {
        address wallet;           // Representative's signing wallet
        uint256 manifestoCount;   // Number of manifestos submitted
        bool registered;          // Whether representative is registered
    }
    
    // ============= State Variables =============
    
    // Representative ID => Representative data
    mapping(uint256 => Representative) public representatives;
    
    // Representative ID => Manifesto Index => Manifesto data
    mapping(uint256 => mapping(uint256 => Manifesto)) public manifestos;
    
    // Quick lookup: hash => (representativeId, manifestoIndex)
    mapping(bytes32 => uint256) public hashToRepresentative;
    mapping(bytes32 => uint256) public hashToIndex;
    mapping(bytes32 => bool) public hashExists;
    
    // Global stats
    uint256 public totalManifestos;
    uint256 public totalRepresentatives;
    
    // ============= Events =============
    
    event RepresentativeRegistered(
        uint256 indexed representativeId,
        address indexed wallet,
        uint256 timestamp
    );
    
    event ManifestoSubmitted(
        uint256 indexed representativeId,
        uint256 indexed manifestoIndex,
        bytes32 indexed contentHash,
        uint256 timestamp,
        uint256 blockNumber
    );
    
    event WalletUpdated(
        uint256 indexed representativeId,
        address indexed oldWallet,
        address indexed newWallet,
        uint256 timestamp
    );
    
    // ============= Errors =============
    
    error RepresentativeNotRegistered(uint256 representativeId);
    error RepresentativeAlreadyRegistered(uint256 representativeId);
    error NotRepresentativeWallet(uint256 representativeId, address caller);
    error ManifestoAlreadyExists(bytes32 contentHash);
    error ManifestoNotFound(uint256 representativeId, uint256 index);
    error InvalidHash();
    error InvalidAddress();
    
    // ============= Modifiers =============
    
    modifier onlyRepresentative(uint256 representativeId) {
        if (!representatives[representativeId].registered) {
            revert RepresentativeNotRegistered(representativeId);
        }
        if (representatives[representativeId].wallet != msg.sender) {
            revert NotRepresentativeWallet(representativeId, msg.sender);
        }
        _;
    }
    
    // ============= Registration =============
    
    /**
     * @notice Register a new representative with their wallet address
     * @param representativeId Unique identifier for the representative (from off-chain DB)
     * @dev Anyone can register once - the msg.sender becomes the representative's wallet
     */
    function registerRepresentative(uint256 representativeId) external {
        if (representatives[representativeId].registered) {
            revert RepresentativeAlreadyRegistered(representativeId);
        }
        
        representatives[representativeId] = Representative({
            wallet: msg.sender,
            manifestoCount: 0,
            registered: true
        });
        
        totalRepresentatives++;
        
        emit RepresentativeRegistered(representativeId, msg.sender, block.timestamp);
    }
    
    /**
     * @notice Update representative's wallet address (key rotation)
     * @param representativeId The representative's ID
     * @param newWallet The new wallet address
     * @dev Only the current wallet can update to a new one
     */
    function updateWallet(uint256 representativeId, address newWallet) 
        external 
        onlyRepresentative(representativeId) 
    {
        if (newWallet == address(0)) {
            revert InvalidAddress();
        }
        
        address oldWallet = representatives[representativeId].wallet;
        representatives[representativeId].wallet = newWallet;
        
        emit WalletUpdated(representativeId, oldWallet, newWallet, block.timestamp);
    }
    
    // ============= Manifesto Submission =============
    
    /**
     * @notice Submit a manifesto hash commitment
     * @notice Submit a manifesto hash commitment
     * @param representativeId The representative's ID
     * @param contentHash SHA256 hash of the manifesto content
     * @dev Hash is computed off-chain: keccak256(abi.encodePacked(manifestoText))
     * @return manifestoIndex The index of this manifesto for the representative
     */
    function submitManifesto(uint256 representativeId, bytes32 contentHash) 
        external 
        onlyRepresentative(representativeId) 
        returns (uint256 manifestoIndex)
    {
        if (contentHash == bytes32(0)) {
            revert InvalidHash();
        }
        
        if (hashExists[contentHash]) {
            revert ManifestoAlreadyExists(contentHash);
        }
        
        manifestoIndex = representatives[representativeId].manifestoCount;
        
        manifestos[representativeId][manifestoIndex] = Manifesto({
            contentHash: contentHash,
            submittedAt: block.timestamp,
            blockNumber: block.number,
            exists: true
        });
        
        // Update lookup mappings
        hashToRepresentative[contentHash] = representativeId;
        hashToIndex[contentHash] = manifestoIndex;
        hashExists[contentHash] = true;
        
        // Update counts
        representatives[representativeId].manifestoCount++;
        totalManifestos++;
        
        emit ManifestoSubmitted(
            representativeId,
            manifestoIndex,
            contentHash,
            block.timestamp,
            block.number
        );
        
        return manifestoIndex;
    }
    
    // ============= Verification Functions =============
    
    /**
     * @notice Verify if a manifesto hash was submitted by a representative
     * @param representativeId The representative's ID
     * @param contentHash The hash to verify
     * @return valid True if the hash matches a submitted manifesto
     * @return submittedAt Timestamp when the manifesto was submitted (0 if not found)
     * @return blockNumber Block number when submitted (0 if not found)
     */
    function verifyManifesto(uint256 representativeId, bytes32 contentHash) 
        external 
        view 
        returns (bool valid, uint256 submittedAt, uint256 blockNumber) 
    {
        if (!hashExists[contentHash]) {
            return (false, 0, 0);
        }
        
        if (hashToRepresentative[contentHash] != representativeId) {
            return (false, 0, 0);
        }
        
        uint256 index = hashToIndex[contentHash];
        Manifesto storage m = manifestos[representativeId][index];
        
        return (true, m.submittedAt, m.blockNumber);
    }
    
    /**
     * @notice Verify a hash exists and get its author
     * @param contentHash The hash to look up
     * @return exists True if hash exists in registry
     * @return representativeId The representative who submitted it
     * @return submittedAt Timestamp when submitted
     */
    function lookupHash(bytes32 contentHash) 
        external 
        view 
        returns (bool exists, uint256 representativeId, uint256 submittedAt) 
    {
        if (!hashExists[contentHash]) {
            return (false, 0, 0);
        }
        
        representativeId = hashToRepresentative[contentHash];
        uint256 index = hashToIndex[contentHash];
        submittedAt = manifestos[representativeId][index].submittedAt;
        
        return (true, representativeId, submittedAt);
    }
    
    // ============= View Functions =============
    
    /**
     * @notice Get manifesto details by representative ID and index
     * @param representativeId The representative's ID
     * @param index The manifesto index
     * @return contentHash The manifesto's content hash
     * @return submittedAt Timestamp when submitted
     * @return blockNumber Block number when submitted
     */
    function getManifesto(uint256 representativeId, uint256 index) 
        external 
        view 
        returns (bytes32 contentHash, uint256 submittedAt, uint256 blockNumber) 
    {
        if (!manifestos[representativeId][index].exists) {
            revert ManifestoNotFound(representativeId, index);
        }
        
        Manifesto storage m = manifestos[representativeId][index];
        return (m.contentHash, m.submittedAt, m.blockNumber);
    }
    
    /**
     * @notice Get all manifesto hashes for a representative
     * @param representativeId The representative's ID
     * @return hashes Array of content hashes
     * @return timestamps Array of submission timestamps
     */
    function getRepresentativeManifestos(uint256 representativeId) 
        external 
        view 
        returns (bytes32[] memory hashes, uint256[] memory timestamps) 
    {
        uint256 count = representatives[representativeId].manifestoCount;
        hashes = new bytes32[](count);
        timestamps = new uint256[](count);
        
        for (uint256 i = 0; i < count; i++) {
            hashes[i] = manifestos[representativeId][i].contentHash;
            timestamps[i] = manifestos[representativeId][i].submittedAt;
        }
        
        return (hashes, timestamps);
    }
    
    /**
     * @notice Get representative info
     * @param representativeId The representative's ID
     * @return wallet The representative's wallet address
     * @return manifestoCount Number of manifestos submitted
     * @return registered Whether the representative is registered
     */
    function getRepresentative(uint256 representativeId) 
        external 
        view 
        returns (address wallet, uint256 manifestoCount, bool registered) 
    {
        Representative storage p = representatives[representativeId];
        return (p.wallet, p.manifestoCount, p.registered);
    }
    
    /**
     * @notice Check if an address is the wallet for a representative
     * @param representativeId The representative's ID
     * @param wallet The address to check
     * @return True if the address is the representative's wallet
     */
    function isRepresentativeWallet(uint256 representativeId, address wallet) 
        external 
        view 
        returns (bool) 
    {
        return representatives[representativeId].registered && 
               representatives[representativeId].wallet == wallet;
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
