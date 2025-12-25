"""
Comprehensive tests for PromiseThread API endpoints.
Run with: pytest test_api.py -v
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone
import hashlib
from sqlalchemy.orm import Session

# Import the FastAPI app and database
from main import app
from database import get_db, engine
from models import Base, Voter, ZKCredential, Politician, Manifesto, ManifestoVote, Comment

client = TestClient(app)


# ============= Test Fixtures =============

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    yield db
    db.close()
    # Clean up tables after test
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


@pytest.fixture
def sample_politician(db_session: Session):
    """Create a sample politician for testing."""
    politician = Politician(
        name="Test Politician",
        party="Independent",
        position="Mayor",
        bio="Test bio"
    )
    db_session.add(politician)
    db_session.commit()
    db_session.refresh(politician)
    return politician


@pytest.fixture
def sample_manifesto(db_session: Session, sample_politician):
    """Create a sample manifesto for testing."""
    manifesto = Manifesto(
        title="Universal Healthcare Initiative",
        description="Provide healthcare to all citizens",
        category="Healthcare",
        politician_id=sample_politician.id,
        grace_period_end=datetime.now(timezone.utc) - timedelta(days=1),  # Open for voting
        status="pending",
        promise_hash=hashlib.sha256(b"healthcare initiative").hexdigest()
    )
    db_session.add(manifesto)
    db_session.commit()
    db_session.refresh(manifesto)
    return manifesto


@pytest.fixture
def authenticated_credential(db_session: Session):
    """Create an authenticated ZK credential."""
    nullifier = hashlib.sha256(b"test_nullifier_unique").hexdigest()
    credential = ZKCredential(
        nullifier_hash=nullifier,
        credential_hash="commitment_hash_" + nullifier[:20],
        is_valid=True
    )
    db_session.add(credential)
    db_session.commit()
    db_session.refresh(credential)
    return {"nullifier": nullifier, "credential_id": credential.id}


# ============= Health Check Tests =============

class TestHealthCheck:
    """Test health check endpoint."""
    
    def test_health_check(self):
        """Test /health endpoint returns correct structure."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] in ["healthy", "degraded"]
        assert "version" in data
        assert "timestamp" in data


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
    
    def test_get_registry_stats(self):
        """Test /api/registry/stats returns statistics."""
        response = client.get("/api/registry/stats")
        assert response.status_code == 200
        data = response.json()
        
        # If registry is loaded, check structure
        if "error" not in data:
            assert "total_voters" in data
    
    def test_search_voters(self):
        """Test voter search endpoint."""
        response = client.get("/api/registry/search?query=")
        assert response.status_code == 200
        data = response.json()
        
        assert "results" in data
        assert "total" in data


# ============= ZK Proof Endpoints Tests =============

class TestZKProofEndpoints:
    """Test zero-knowledge proof endpoints."""
    
    def test_get_leaves(self):
        """Test getting ZK leaves (anonymity set)."""
        response = client.get("/api/zk/leaves")
        assert response.status_code == 200
        data = response.json()
        
        assert "leaves" in data
        assert isinstance(data["leaves"], list)
    
    def test_check_credential_invalid(self):
        """Test checking an invalid credential."""
        response = client.get("/api/zk/credential/invalid_nullifier_xyz")
        assert response.status_code == 200
        data = response.json()
        
        assert data["valid"] == False


# ============= Manifesto Endpoints Tests =============

class TestManifestoEndpoints:
    """Test manifesto CRUD endpoints."""
    
    def test_get_all_manifestos(self, sample_manifesto):
        """Test getting all manifestos."""
        response = client.get("/api/manifestos")
        assert response.status_code == 200
        data = response.json()
        
        assert "manifestos" in data
        assert isinstance(data["manifestos"], list)
    
    def test_get_manifesto_not_found(self):
        """Test getting non-existent manifesto."""
        response = client.get("/api/manifestos/999999")
        assert response.status_code == 404


# ============= Politician Endpoints Tests =============

class TestPoliticianEndpoints:
    """Test politician-related endpoints."""
    
    def test_get_all_politicians(self, sample_politician):
        """Test getting list of all politicians."""
        response = client.get("/api/politicians")
        assert response.status_code == 200
        data = response.json()
        
        assert "politicians" in data
        assert isinstance(data["politicians"], list)
    
    def test_get_politician_not_found(self):
        """Test getting non-existent politician."""
        response = client.get("/api/politicians/999999")
        assert response.status_code == 404
    
    def test_politician_registration_flow(self, db_session: Session):
        """Test complete politician registration flow (auto-verified in decentralized system)."""
        # Step 1: Create ZK credential (citizen authentication)
        test_nullifier = "0x" + hashlib.sha256(b"test_citizen_politician").hexdigest()
        credential = ZKCredential(
            nullifier_hash=test_nullifier,
            credential_hash="0x" + hashlib.sha256(b"cred_politician").hexdigest(),
            is_valid=True
        )
        db_session.add(credential)
        db_session.commit()
        
        # Step 2: Register as politician (auto-verified in decentralized system)
        registration_data = {
            "nullifier": test_nullifier,
            "name": "राम बहादुर श्रेष्ठ",
            "party": "स्वतन्त्र उम्मेदवार",
            "position": "नगर प्रमुख",
            "bio": "२० वर्षको सामुदायिक अनुभव",
            "election_commission_id": "EC-2025-TEST-001"
        }
        
        response = client.post("/api/politicians/register", json=registration_data)
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "politician" in data
        # In decentralized system, politicians are auto-approved
        assert data["politician"]["application_status"] == "approved"
        assert data["politician"]["is_verified"] == True
        politician_id = data["politician"]["id"]
        
        # Verify endpoint is still available but optional (for backwards compatibility)
        # In true decentralized system, this step would not be needed
        verify_data = {
            "admin_key": "ec_admin_2025",
            "approved": True,
            "verified_by": "Test Election Officer"
        }
        
        # This should work but not change the status (already approved)
        response = client.post(f"/api/politicians/{politician_id}/verify", json=verify_data)
        # Should fail because already approved
        assert response.status_code == 400
    
    def test_politician_registration_without_credential(self):
        """Test that registration fails without valid ZK credential."""
        registration_data = {
            "nullifier": "0x" + hashlib.sha256(b"invalid_nullifier").hexdigest(),
            "name": "Invalid Politician",
            "party": "Test Party",
            "position": "Test Position"
        }
        
        response = client.post("/api/politicians/register", json=registration_data)
        assert response.status_code == 401
        assert "Invalid credential" in response.json()["detail"]
    
    def test_politician_rejection_flow(self, db_session: Session):
        """Test that politicians are auto-approved in decentralized system.
        
        In a truly decentralized system, there is no rejection mechanism.
        All verified citizens can register as politicians.
        This test now verifies auto-approval instead of rejection.
        """
        # Create credential
        test_nullifier = "0x" + hashlib.sha256(b"test_rejected_politician").hexdigest()
        credential = ZKCredential(
            nullifier_hash=test_nullifier,
            credential_hash="0x" + hashlib.sha256(b"cred_rejected").hexdigest(),
            is_valid=True
        )
        db_session.add(credential)
        db_session.commit()
        
        # Register (should auto-approve)
        registration_data = {
            "nullifier": test_nullifier,
            "name": "Auto-Approved Candidate",
            "party": "Test Party",
            "position": "Test Position"
        }
        
        response = client.post("/api/politicians/register", json=registration_data)
        assert response.status_code == 200
        data = response.json()
        
        # Verify auto-approval
        assert data["politician"]["application_status"] == "approved"
        assert data["politician"]["is_verified"] == True
    
    def test_unverified_politician_cannot_post_manifesto(self, db_session: Session):
        """Test manifesto creation (in decentralized system, all registered politicians are verified)."""
        # Create credential
        test_nullifier = "0x" + hashlib.sha256(b"unverified_politician").hexdigest()
        credential = ZKCredential(
            nullifier_hash=test_nullifier,
            credential_hash="0x" + hashlib.sha256(b"cred_unverified").hexdigest(),
            is_valid=True
        )
        db_session.add(credential)
        db_session.commit()
        
        registration_data = {
            "nullifier": test_nullifier,
            "name": "Verified Politician",
            "party": "Test Party",
            "position": "Test Position"
        }
        
        response = client.post("/api/politicians/register", json=registration_data)
        politician_id = response.json()["politician"]["id"]
        
        # In decentralized system, politician is auto-verified, so manifesto should succeed
        manifesto_data = {
            "title": "Test Promise",
            "description": "This should succeed",
            "category": "infrastructure",
            "politician_id": politician_id,
            "deadline": (datetime.now(timezone.utc) + timedelta(days=365)).isoformat()
        }
        
        response = client.post("/api/manifestos", json=manifesto_data)
        # Should now succeed because politician is auto-verified
        assert response.status_code == 200
    
    def test_get_pending_politicians(self, db_session: Session):
        """Test getting list of pending politician applications.
        
        In decentralized system, this should return empty list since all
        politicians are auto-verified on registration.
        """
        # Create credential and register politician
        test_nullifier = "0x" + hashlib.sha256(b"pending_politician").hexdigest()
        credential = ZKCredential(
            nullifier_hash=test_nullifier,
            credential_hash="0x" + hashlib.sha256(b"cred_pending").hexdigest(),
            is_valid=True
        )
        db_session.add(credential)
        db_session.commit()
        
        registration_data = {
            "nullifier": test_nullifier,
            "name": "Auto-Verified Politician",
            "party": "Test Party",
            "position": "Test Position"
        }
        
        client.post("/api/politicians/register", json=registration_data)
        
        # Get pending applications (should be empty in decentralized system)
        response = client.get("/api/politicians/pending")
        assert response.status_code == 200
        data = response.json()
        
        assert "pending_count" in data
        # Should be 0 since politicians are auto-approved
        assert data["pending_count"] == 0
        assert isinstance(data["applications"], list)
    
    def test_double_registration_prevention(self, db_session: Session):
        """Test that same nullifier cannot register twice."""
        test_nullifier = "0x" + hashlib.sha256(b"double_registration").hexdigest()
        credential = ZKCredential(
            nullifier_hash=test_nullifier,
            credential_hash="0x" + hashlib.sha256(b"cred_double").hexdigest(),
            is_valid=True
        )
        db_session.add(credential)
        db_session.commit()
        
        registration_data = {
            "nullifier": test_nullifier,
            "name": "First Registration",
            "party": "Test Party",
            "position": "Test Position"
        }
        
        # First registration should succeed
        response = client.post("/api/politicians/register", json=registration_data)
        assert response.status_code == 200
        
        # Second registration should fail
        registration_data["name"] = "Second Registration"
        response = client.post("/api/politicians/register", json=registration_data)
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    def test_invalid_admin_key(self, db_session: Session):
        """Test that invalid admin key cannot verify politicians."""
        # Create politician application
        test_nullifier = "0x" + hashlib.sha256(b"admin_test_politician").hexdigest()
        credential = ZKCredential(
            nullifier_hash=test_nullifier,
            credential_hash="0x" + hashlib.sha256(b"cred_admin_test").hexdigest(),
            is_valid=True
        )
        db_session.add(credential)
        db_session.commit()
        
        registration_data = {
            "nullifier": test_nullifier,
            "name": "Admin Test Politician",
            "party": "Test Party",
            "position": "Test Position"
        }
        
        response = client.post("/api/politicians/register", json=registration_data)
        politician_id = response.json()["politician"]["id"]
        
        # Try to verify with invalid admin key
        verify_data = {
            "admin_key": "wrong_admin_key",
            "approved": True,
            "verified_by": "Fake Officer"
        }
        
        response = client.post(f"/api/politicians/{politician_id}/verify", json=verify_data)
        assert response.status_code == 403
        assert "Unauthorized" in response.json()["detail"]


# ============= Blockchain/Audit Endpoints Tests =============

class TestBlockchainEndpoints:
    """Test blockchain and audit functionality."""
    


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
