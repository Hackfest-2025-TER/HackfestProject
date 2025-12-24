"""
Comprehensive tests for PromiseThread API endpoints.
Run with: pytest test_api.py -v
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import hashlib

# Import the FastAPI app
from main import (
    app, 
    manifestos_db, 
    comments_db, 
    votes_db, 
    credentials_db,
    expected_nullifiers_db,
    voter_registry,
    DEMO_SECRET,
    compute_expected_nullifier,
    generate_hash
)

client = TestClient(app)


# ============= Test Fixtures =============

@pytest.fixture(autouse=True)
def reset_databases():
    """Reset in-memory databases before each test."""
    # Store original state
    original_manifestos = manifestos_db.copy()
    original_comments = comments_db.copy()
    original_votes = votes_db.copy()
    original_credentials = credentials_db.copy()
    original_expected_nullifiers = expected_nullifiers_db.copy()
    
    yield
    
    # Restore original state after test
    manifestos_db.clear()
    manifestos_db.extend(original_manifestos)
    comments_db.clear()
    comments_db.extend(original_comments)
    votes_db.clear()
    votes_db.extend(original_votes)
    credentials_db.clear()
    credentials_db.update(original_credentials)
    expected_nullifiers_db.clear()
    expected_nullifiers_db.update(original_expected_nullifiers)


@pytest.fixture
def valid_credential():
    """Create a valid credential for testing."""
    test_voter_id = "12345"
    expected_nullifier = compute_expected_nullifier(test_voter_id)
    voter_id_hash = generate_hash(test_voter_id)
    
    # Register expected nullifier (simulating lookup flow)
    expected_nullifiers_db[expected_nullifier] = {
        "voter_id_hash": voter_id_hash,
        "created_at": datetime.now().isoformat()
    }
    
    return {
        "voter_id_hash": voter_id_hash,
        "nullifier": expected_nullifier,
        "merkle_proof": [{"hash": "abc123", "position": "left"}],
        "commitment": "commitment_hash_1234567890123456"
    }


@pytest.fixture
def registered_credential(valid_credential):
    """Create and register a credential for voting tests."""
    response = client.post("/api/zk/verify", json=valid_credential)
    assert response.status_code == 200
    result = response.json()
    return {
        "nullifier": result["nullifier"],
        "credential": result["credential"]
    }


# ============= Health Check Tests =============

class TestHealthCheck:
    """Test health check endpoint."""
    
    def test_health_check(self):
        """Test /health endpoint returns correct structure."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data
        assert "block_height" in data
        assert isinstance(data["block_height"], int)


# ============= Registry Endpoints Tests =============

class TestRegistryEndpoints:
    """Test voter registry endpoints."""
    
    def test_get_merkle_root(self):
        """Test /api/registry/merkle-root returns registry info."""
        response = client.get("/api/registry/merkle-root")
        assert response.status_code == 200
        data = response.json()
        
        assert "merkle_root" in data
        assert "total_voters" in data
        assert "registry_status" in data
        assert data["mode"] == "demo"
        assert data["demo_secret"] == DEMO_SECRET
    
    def test_get_registry_stats(self):
        """Test /api/registry/stats returns statistics."""
        response = client.get("/api/registry/stats")
        assert response.status_code == 200
        data = response.json()
        
        # If registry is loaded, check structure
        if "error" not in data:
            assert "total_voters" in data
            assert "wards" in data
            assert "district" in data
            assert "municipality" in data
    
    def test_lookup_voter_not_found(self):
        """Test voter lookup with non-existent ID."""
        response = client.post("/api/registry/lookup", json={"voter_id": "999999999"})
        assert response.status_code == 200
        data = response.json()
        
        assert data["found"] == False
        assert "message" in data
    
    def test_search_voters(self):
        """Test voter search endpoint."""
        response = client.get("/api/registry/search?query=")
        assert response.status_code == 200
        data = response.json()
        
        assert "results" in data
        assert "total" in data
        assert "query" in data
    
    def test_search_voters_with_ward_filter(self):
        """Test voter search with ward filter."""
        response = client.get("/api/registry/search?query=&ward=1")
        assert response.status_code == 200
        data = response.json()
        
        assert "results" in data
        assert isinstance(data["results"], list)
    
    def test_search_voters_with_limit(self):
        """Test voter search with limit parameter."""
        response = client.get("/api/registry/search?query=&limit=5")
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["results"]) <= 5


# ============= ZK Proof Endpoints Tests =============

class TestZKProofEndpoints:
    """Test zero-knowledge proof endpoints."""
    
    def test_verify_zk_proof_success(self, valid_credential):
        """Test successful ZK proof verification."""
        response = client.post("/api/zk/verify", json=valid_credential)
        assert response.status_code == 200
        data = response.json()
        
        assert data["valid"] == True
        assert "credential" in data
        assert "nullifier" in data
        assert "nullifier_short" in data
        assert "message" in data
    
    def test_verify_zk_proof_duplicate_nullifier(self, valid_credential):
        """Test ZK proof verification fails with duplicate nullifier."""
        # First verification should succeed
        response1 = client.post("/api/zk/verify", json=valid_credential)
        assert response1.status_code == 200
        assert response1.json()["valid"] == True
        
        # Second verification with same nullifier should fail
        # Need to re-add expected nullifier since it was consumed
        expected_nullifiers_db[valid_credential["nullifier"]] = {
            "voter_id_hash": valid_credential["voter_id_hash"],
            "created_at": datetime.now().isoformat()
        }
        
        response2 = client.post("/api/zk/verify", json=valid_credential)
        assert response2.status_code == 200
        assert response2.json()["valid"] == False
        assert "already been registered" in response2.json()["message"]
    
    def test_verify_zk_proof_invalid_nullifier(self):
        """Test ZK proof verification fails with unknown nullifier."""
        invalid_proof = {
            "voter_id_hash": "0x123",
            "nullifier": "0xinvalidnullifier123456",
            "merkle_proof": [{"hash": "abc", "position": "left"}],
            "commitment": "commitment_hash_12345678901234567890"
        }
        
        response = client.post("/api/zk/verify", json=invalid_proof)
        assert response.status_code == 200
        data = response.json()
        
        assert data["valid"] == False
        assert "Invalid secret" in data["message"]
    
    def test_verify_zk_proof_invalid_merkle_proof(self, valid_credential):
        """Test ZK proof verification fails with empty merkle proof."""
        invalid_proof = valid_credential.copy()
        invalid_proof["merkle_proof"] = []
        
        response = client.post("/api/zk/verify", json=invalid_proof)
        assert response.status_code == 200
        data = response.json()
        
        assert data["valid"] == False
        assert "Invalid Merkle proof" in data["message"]
    
    def test_verify_zk_proof_short_commitment(self, valid_credential):
        """Test ZK proof verification fails with short commitment."""
        invalid_proof = valid_credential.copy()
        invalid_proof["commitment"] = "short"
        
        response = client.post("/api/zk/verify", json=invalid_proof)
        assert response.status_code == 200
        data = response.json()
        
        assert data["valid"] == False
        assert "too short" in data["message"]
    
    def test_check_credential_valid(self, registered_credential):
        """Test checking a valid credential."""
        response = client.get(f"/api/zk/credential/{registered_credential['nullifier']}")
        assert response.status_code == 200
        data = response.json()
        
        assert data["valid"] == True
        assert "used_votes" in data
        assert data["can_vote"] == True
    
    def test_check_credential_invalid(self):
        """Test checking an invalid credential."""
        response = client.get("/api/zk/credential/invalid_nullifier")
        assert response.status_code == 200
        data = response.json()
        
        assert data["valid"] == False
        assert data["can_vote"] == False


# ============= Manifesto Endpoints Tests =============

class TestManifestoEndpoints:
    """Test manifesto CRUD endpoints."""
    
    def test_get_all_manifestos(self):
        """Test getting all manifestos."""
        response = client.get("/api/manifestos")
        assert response.status_code == 200
        data = response.json()
        
        assert "manifestos" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data
        assert isinstance(data["manifestos"], list)
    
    def test_get_manifestos_with_status_filter(self):
        """Test filtering manifestos by status."""
        response = client.get("/api/manifestos?status=pending")
        assert response.status_code == 200
        data = response.json()
        
        for m in data["manifestos"]:
            assert m["status"] == "pending"
    
    def test_get_manifestos_with_category_filter(self):
        """Test filtering manifestos by category."""
        response = client.get("/api/manifestos?category=Healthcare")
        assert response.status_code == 200
        data = response.json()
        
        for m in data["manifestos"]:
            assert m["category"] == "Healthcare"
    
    def test_get_manifestos_with_politician_filter(self):
        """Test filtering manifestos by politician."""
        response = client.get("/api/manifestos?politician_id=POL-001")
        assert response.status_code == 200
        data = response.json()
        
        for m in data["manifestos"]:
            assert m["politician_id"] == "POL-001"
    
    def test_get_manifestos_with_pagination(self):
        """Test manifestos pagination."""
        response = client.get("/api/manifestos?limit=2&offset=0")
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["manifestos"]) <= 2
    
    def test_get_single_manifesto(self):
        """Test getting a single manifesto by ID."""
        response = client.get("/api/manifestos/MAN-2023-0001")
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == "MAN-2023-0001"
        assert "title" in data
        assert "description" in data
        assert "status" in data
    
    def test_get_manifesto_not_found(self):
        """Test getting non-existent manifesto."""
        response = client.get("/api/manifestos/INVALID-ID")
        assert response.status_code == 404
    
    def test_create_manifesto(self):
        """Test creating a new manifesto."""
        new_manifesto = {
            "title": "Test Manifesto",
            "description": "A test description",
            "category": "Education",
            "politician_id": "POL-001",
            "deadline": "2025-12-31",
            "promises": ["Promise 1", "Promise 2"]
        }
        
        response = client.post("/api/manifestos", json=new_manifesto)
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data
        assert data["title"] == "Test Manifesto"
        assert data["status"] == "pending"
        assert "hash" in data
        assert "grace_period_end" in data
    
    def test_get_manifesto_votes(self):
        """Test getting vote aggregates for a manifesto."""
        response = client.get("/api/manifestos/MAN-2023-0001/votes")
        assert response.status_code == 200
        data = response.json()
        
        assert data["manifesto_id"] == "MAN-2023-0001"
        assert "vote_kept" in data
        assert "vote_broken" in data
        assert "total_votes" in data
        assert "kept_percentage" in data
        assert "broken_percentage" in data
    
    def test_get_manifesto_votes_not_found(self):
        """Test getting votes for non-existent manifesto."""
        response = client.get("/api/manifestos/INVALID-ID/votes")
        assert response.status_code == 404


# ============= Vote Endpoints Tests =============

class TestVoteEndpoints:
    """Test voting endpoints."""
    
    def test_submit_vote_success(self, registered_credential):
        """Test successful vote submission."""
        # Find manifesto with passed grace period
        vote_data = {
            "manifesto_id": "MAN-2023-0001",  # Has passed grace period
            "vote_type": "kept",
            "nullifier": registered_credential["nullifier"],
            "proof": "zk_proof_placeholder"
        }
        
        response = client.post("/api/votes", json=vote_data)
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "vote_hash" in data
        assert "block_height" in data
    
    def test_submit_vote_invalid_nullifier(self):
        """Test vote submission with invalid nullifier."""
        vote_data = {
            "manifesto_id": "MAN-2023-0001",
            "vote_type": "kept",
            "nullifier": "invalid_nullifier",
            "proof": "zk_proof"
        }
        
        response = client.post("/api/votes", json=vote_data)
        assert response.status_code == 401
    
    def test_submit_vote_double_voting(self, registered_credential):
        """Test that double voting is prevented."""
        vote_data = {
            "manifesto_id": "MAN-2023-0001",
            "vote_type": "kept",
            "nullifier": registered_credential["nullifier"],
            "proof": "zk_proof"
        }
        
        # First vote should succeed
        response1 = client.post("/api/votes", json=vote_data)
        assert response1.status_code == 200
        
        # Second vote on same manifesto should fail
        response2 = client.post("/api/votes", json=vote_data)
        assert response2.status_code == 400
        assert "Already voted" in response2.json()["detail"]
    
    def test_submit_vote_manifesto_not_found(self, registered_credential):
        """Test vote on non-existent manifesto."""
        vote_data = {
            "manifesto_id": "INVALID-ID",
            "vote_type": "kept",
            "nullifier": registered_credential["nullifier"],
            "proof": "zk_proof"
        }
        
        response = client.post("/api/votes", json=vote_data)
        assert response.status_code == 404
    
    def test_verify_vote(self, registered_credential):
        """Test vote verification."""
        # First submit a vote
        vote_data = {
            "manifesto_id": "MAN-2023-0001",
            "vote_type": "kept",
            "nullifier": registered_credential["nullifier"],
            "proof": "zk_proof"
        }
        
        submit_response = client.post("/api/votes", json=vote_data)
        vote_hash = submit_response.json()["vote_hash"]
        
        # Verify the vote
        response = client.get(f"/api/votes/verify/{vote_hash}")
        assert response.status_code == 200
        data = response.json()
        
        assert data["verified"] == True
        assert "vote" in data
        assert "merkle_proof" in data
    
    def test_verify_vote_not_found(self):
        """Test verifying non-existent vote."""
        response = client.get("/api/votes/verify/invalid_hash")
        assert response.status_code == 200
        data = response.json()
        
        assert data["verified"] == False
        assert "message" in data


# ============= Comment Endpoints Tests =============

class TestCommentEndpoints:
    """Test comment/discussion endpoints."""
    
    def test_get_comments_empty(self):
        """Test getting comments for manifesto with no comments."""
        # Clear comments first
        comments_db.clear()
        
        response = client.get("/api/manifestos/MAN-2023-0001/comments")
        assert response.status_code == 200
        data = response.json()
        
        assert "comments" in data
        assert "total" in data
        assert data["total"] == 0
    
    def test_create_comment(self):
        """Test creating a new comment."""
        comment_data = {
            "manifesto_id": "MAN-2023-0001",
            "content": "This is a test comment",
            "nullifier": "0x1234567890abcdef1234567890abcdef"
        }
        
        response = client.post("/api/comments", json=comment_data)
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data
        assert data["content"] == "This is a test comment"
        assert data["manifesto_id"] == "MAN-2023-0001"
        assert "created_at" in data
        # Nullifier should be truncated
        assert data["nullifier"].endswith("...")
    
    def test_create_reply_comment(self):
        """Test creating a reply to a comment."""
        # First create parent comment
        parent_comment = {
            "manifesto_id": "MAN-2023-0001",
            "content": "Parent comment",
            "nullifier": "0x1234567890abcdef"
        }
        parent_response = client.post("/api/comments", json=parent_comment)
        parent_id = parent_response.json()["id"]
        
        # Create reply
        reply_comment = {
            "manifesto_id": "MAN-2023-0001",
            "content": "Reply comment",
            "nullifier": "0xabcdef1234567890",
            "parent_id": parent_id
        }
        
        response = client.post("/api/comments", json=reply_comment)
        assert response.status_code == 200
        data = response.json()
        
        assert data["parent_id"] == parent_id
    
    def test_get_comments_with_threads(self):
        """Test getting threaded comments."""
        # Clear and create fresh comments
        comments_db.clear()
        
        # Create parent
        parent = {"manifesto_id": "MAN-2023-0001", "content": "Parent", "nullifier": "0x1234"}
        parent_response = client.post("/api/comments", json=parent)
        parent_id = parent_response.json()["id"]
        
        # Create reply
        reply = {"manifesto_id": "MAN-2023-0001", "content": "Reply", "nullifier": "0x5678", "parent_id": parent_id}
        client.post("/api/comments", json=reply)
        
        # Get comments
        response = client.get("/api/manifestos/MAN-2023-0001/comments")
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["comments"]) == 1  # Only root comment
        assert "replies" in data["comments"][0]
        assert len(data["comments"][0]["replies"]) == 1
    
    def test_upvote_comment(self):
        """Test upvoting a comment."""
        # Create a comment first
        comment = {"manifesto_id": "MAN-2023-0001", "content": "Test", "nullifier": "0x1234"}
        comment_response = client.post("/api/comments", json=comment)
        comment_id = comment_response.json()["id"]
        
        # Upvote it
        response = client.post(f"/api/comments/{comment_id}/vote?vote_type=up")
        assert response.status_code == 200
        data = response.json()
        
        assert data["upvotes"] == 1
    
    def test_downvote_comment(self):
        """Test downvoting a comment."""
        # Create a comment first
        comment = {"manifesto_id": "MAN-2023-0001", "content": "Test", "nullifier": "0x1234"}
        comment_response = client.post("/api/comments", json=comment)
        comment_id = comment_response.json()["id"]
        
        # Downvote it
        response = client.post(f"/api/comments/{comment_id}/vote?vote_type=down")
        assert response.status_code == 200
        data = response.json()
        
        assert data["downvotes"] == 1
    
    def test_vote_comment_not_found(self):
        """Test voting on non-existent comment."""
        response = client.post("/api/comments/INVALID-ID/vote?vote_type=up")
        assert response.status_code == 404


# ============= Audit & Network Endpoints Tests =============

class TestAuditEndpoints:
    """Test audit and network statistics endpoints."""
    
    def test_get_audit_logs(self):
        """Test getting audit logs."""
        response = client.get("/api/audit/logs")
        assert response.status_code == 200
        data = response.json()
        
        assert "logs" in data
        assert "total" in data
        assert isinstance(data["logs"], list)
        
        if len(data["logs"]) > 0:
            log = data["logs"][0]
            assert "id" in log
            assert "action" in log
            assert "timestamp" in log
            assert "block_height" in log
            assert "tx_hash" in log
            assert "status" in log
    
    def test_get_audit_logs_with_limit(self):
        """Test getting audit logs with limit."""
        response = client.get("/api/audit/logs?limit=10")
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["logs"]) <= 10
    
    def test_get_network_stats(self):
        """Test getting network statistics."""
        response = client.get("/api/network/stats")
        assert response.status_code == 200
        data = response.json()
        
        assert "active_nodes" in data
        assert "total_votes" in data
        assert "total_manifestos" in data
        assert "integrity_score" in data
        assert "uptime" in data
        assert "last_block" in data
        assert "avg_block_time" in data
        assert "pending_txs" in data


# ============= Blockchain Endpoints Tests =============

class TestBlockchainEndpoints:
    """Test blockchain visualization endpoints."""
    
    def test_get_blocks(self):
        """Test getting blockchain blocks."""
        response = client.get("/api/blockchain/blocks")
        assert response.status_code == 200
        data = response.json()
        
        assert "blocks" in data
        assert isinstance(data["blocks"], list)
        
        if len(data["blocks"]) > 0:
            block = data["blocks"][0]
            assert "number" in block
            assert "hash" in block
            assert "prev_hash" in block
            assert "timestamp" in block
            assert "tx_count" in block
            assert "merkle_root" in block
    
    def test_get_blocks_with_limit(self):
        """Test getting blocks with custom limit."""
        response = client.get("/api/blockchain/blocks?limit=5")
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["blocks"]) == 5
    
    def test_blocks_are_linked(self):
        """Test that blocks are properly linked via prev_hash."""
        response = client.get("/api/blockchain/blocks?limit=3")
        blocks = response.json()["blocks"]
        
        if len(blocks) >= 2:
            # Each block's hash should match next block's prev_hash
            for i in range(len(blocks) - 1):
                current_block = blocks[i]
                next_block = blocks[i + 1]
                # Note: blocks are returned newest first
                assert current_block["prev_hash"] == next_block["hash"]


# ============= Feedback Endpoints Tests =============

class TestFeedbackEndpoints:
    """Test feedback submission endpoints."""
    
    def test_submit_feedback_bug(self):
        """Test submitting bug report."""
        feedback = {
            "type": "bug",
            "content": "I found a bug in the voting system"
        }
        
        response = client.post("/api/feedback", json=feedback)
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "message" in data
        assert "reference" in data
    
    def test_submit_feedback_suggestion(self):
        """Test submitting a suggestion."""
        feedback = {
            "type": "suggestion",
            "content": "Please add dark mode"
        }
        
        response = client.post("/api/feedback", json=feedback)
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
    
    def test_submit_feedback_general(self):
        """Test submitting general feedback."""
        feedback = {
            "type": "general",
            "content": "Great platform!"
        }
        
        response = client.post("/api/feedback", json=feedback)
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True


# ============= Politicians Endpoints Tests =============

class TestPoliticianEndpoints:
    """Test politician-related endpoints."""
    
    def test_get_all_politicians(self):
        """Test getting list of all politicians."""
        response = client.get("/api/politicians")
        assert response.status_code == 200
        data = response.json()
        
        assert "politicians" in data
        assert isinstance(data["politicians"], list)
        assert len(data["politicians"]) > 0
        
        politician = data["politicians"][0]
        assert "id" in politician
        assert "name" in politician
        assert "title" in politician
        assert "party" in politician
        assert "integrity_score" in politician
        assert "verified" in politician
    
    def test_get_politician_by_id(self):
        """Test getting a specific politician."""
        response = client.get("/api/politicians/POL-001")
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == "POL-001"
        assert "name" in data
        assert "title" in data
        assert "public_key" in data
    
    def test_get_politician_not_found(self):
        """Test getting non-existent politician."""
        response = client.get("/api/politicians/INVALID-ID")
        assert response.status_code == 404


# ============= Integration Tests =============

class TestIntegrationFlow:
    """Test complete user flows."""
    
    def test_complete_voting_flow(self):
        """Test the complete ZK authentication and voting flow."""
        # Step 1: Generate proof data (simulating client-side)
        test_voter_id = "integration_test_voter"
        expected_nullifier = compute_expected_nullifier(test_voter_id)
        voter_id_hash = generate_hash(test_voter_id)
        
        # Register expected nullifier (simulating lookup)
        expected_nullifiers_db[expected_nullifier] = {
            "voter_id_hash": voter_id_hash,
            "created_at": datetime.now().isoformat()
        }
        
        # Step 2: Verify ZK proof
        proof_data = {
            "voter_id_hash": voter_id_hash,
            "nullifier": expected_nullifier,
            "merkle_proof": [{"hash": "abc123", "position": "left"}],
            "commitment": "commitment_hash_1234567890123456"
        }
        
        verify_response = client.post("/api/zk/verify", json=proof_data)
        assert verify_response.status_code == 200
        assert verify_response.json()["valid"] == True
        
        nullifier = verify_response.json()["nullifier"]
        
        # Step 3: Vote on a manifesto
        vote_data = {
            "manifesto_id": "MAN-2023-0001",
            "vote_type": "kept",
            "nullifier": nullifier,
            "proof": "zk_proof"
        }
        
        vote_response = client.post("/api/votes", json=vote_data)
        assert vote_response.status_code == 200
        vote_hash = vote_response.json()["vote_hash"]
        
        # Step 4: Verify the vote
        verify_vote_response = client.get(f"/api/votes/verify/{vote_hash}")
        assert verify_vote_response.status_code == 200
        assert verify_vote_response.json()["verified"] == True
        
        # Step 5: Check credential shows vote was cast
        cred_response = client.get(f"/api/zk/credential/{nullifier}")
        assert cred_response.status_code == 200
        assert "MAN-2023-0001" in cred_response.json()["used_votes"]
    
    def test_discussion_flow(self):
        """Test creating and interacting with discussion threads."""
        comments_db.clear()
        
        nullifier = "0xtest_discussion_nullifier123456"
        
        # Create main comment
        main_comment = {
            "manifesto_id": "MAN-2023-0001",
            "content": "I support this healthcare initiative!",
            "nullifier": nullifier
        }
        main_response = client.post("/api/comments", json=main_comment)
        assert main_response.status_code == 200
        main_id = main_response.json()["id"]
        
        # Create reply
        reply = {
            "manifesto_id": "MAN-2023-0001",
            "content": "I agree, this is important",
            "nullifier": "0xanother_user_nullifier12345",
            "parent_id": main_id
        }
        reply_response = client.post("/api/comments", json=reply)
        assert reply_response.status_code == 200
        
        # Upvote the main comment
        upvote_response = client.post(f"/api/comments/{main_id}/vote?vote_type=up")
        assert upvote_response.status_code == 200
        assert upvote_response.json()["upvotes"] == 1
        
        # Get threaded comments
        comments_response = client.get("/api/manifestos/MAN-2023-0001/comments")
        assert comments_response.status_code == 200
        comments = comments_response.json()["comments"]
        
        assert len(comments) == 1
        assert len(comments[0]["replies"]) == 1
        assert comments[0]["upvotes"] == 1


# ============= Edge Cases Tests =============

class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_request_body(self):
        """Test endpoints handle empty request bodies."""
        response = client.post("/api/zk/verify", json={})
        assert response.status_code == 422  # Validation error
    
    def test_malformed_json(self):
        """Test endpoints handle malformed JSON."""
        response = client.post(
            "/api/zk/verify",
            content="not valid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_very_long_content(self):
        """Test handling of very long content."""
        long_content = "x" * 10000
        comment = {
            "manifesto_id": "MAN-2023-0001",
            "content": long_content,
            "nullifier": "0x1234567890abcdef"
        }
        
        response = client.post("/api/comments", json=comment)
        assert response.status_code == 200
        assert response.json()["content"] == long_content
    
    def test_special_characters_in_search(self):
        """Test search handles special characters."""
        response = client.get("/api/registry/search?query=%E0%A4%95%E0%A4%AE%E0%A4%B2")
        assert response.status_code == 200
    
    def test_negative_pagination(self):
        """Test handling of negative pagination values."""
        # Negative offset should still work (treated as 0 or error)
        response = client.get("/api/manifestos?offset=-1")
        assert response.status_code in [200, 422]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
