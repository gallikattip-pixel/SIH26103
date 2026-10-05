"""Tests for historical project snapshot functionality."""

import pytest
from datetime import datetime, timezone
from unittest.mock import Mock, patch, MagicMock

from app.models.snapshot import (
    ProjectSnapshot,
    SnapshotCreateRequest,
    SnapshotListResponse,
)
from app.services.project_service import (
    _get_current_utc_period,
    _build_snapshot_from_project,
    _validate_snapshot_data,
    create_project_snapshot,
    get_project_snapshot,
    get_project_snapshots,
)
from app.models.project import ProjectRecord


class TestSnapshotModels:
    """Tests for snapshot Pydantic models."""

    def test_project_snapshot_valid(self):
        """Test creating a valid ProjectSnapshot."""
        snapshot = ProjectSnapshot(
            project_id="P01",
            snapshot_period="2026-10",
            recorded_at=datetime.now(timezone.utc),
            progress=78.0,
            planned_progress=75.0,
            delay_days=0,
            budget_used=72.0,
            budget_total_crore=120.0,
            contractor="Aarav Infra Ltd",
            sector="Roads",
            location="Madhya Pradesh",
            risk_snapshot={"overall_score": 25, "overall_level": "LOW"},
        )
        assert snapshot.project_id == "P01"
        assert snapshot.snapshot_period == "2026-10"
        assert snapshot.progress == 78.0

    def test_project_snapshot_invalid_period_format(self):
        """Test that invalid period format raises validation error."""
        with pytest.raises(ValueError, match="YYYY-MM format"):
            ProjectSnapshot(
                project_id="P01",
                snapshot_period="2026/10",  # Invalid format
                recorded_at=datetime.now(timezone.utc),
                progress=78.0,
                planned_progress=75.0,
                delay_days=0,
                budget_used=72.0,
                budget_total_crore=120.0,
                contractor="Test",
                sector="Roads",
                location="Test",
            )

    def test_project_snapshot_invalid_progress_range(self):
        """Test that progress outside 0-100 raises validation error."""
        with pytest.raises(ValueError):
            ProjectSnapshot(
                project_id="P01",
                snapshot_period="2026-10",
                recorded_at=datetime.now(timezone.utc),
                progress=150.0,  # Invalid
                planned_progress=75.0,
                delay_days=0,
                budget_used=72.0,
                budget_total_crore=120.0,
                contractor="Test",
                sector="Roads",
                location="Test",
            )

    def test_project_snapshot_negative_delay(self):
        """Test that negative delay_days raises validation error."""
        with pytest.raises(ValueError):
            ProjectSnapshot(
                project_id="P01",
                snapshot_period="2026-10",
                recorded_at=datetime.now(timezone.utc),
                progress=78.0,
                planned_progress=75.0,
                delay_days=-5,  # Invalid
                budget_used=72.0,
                budget_total_crore=120.0,
                contractor="Test",
                sector="Roads",
                location="Test",
            )

    def test_snapshot_create_request_defaults_to_current_month(self):
        """Test SnapshotCreateRequest with None period."""
        request = SnapshotCreateRequest(snapshot_period=None)
        assert request.snapshot_period is None

    def test_snapshot_create_request_valid_period(self):
        """Test SnapshotCreateRequest with valid period."""
        request = SnapshotCreateRequest(snapshot_period="2026-10")
        assert request.snapshot_period == "2026-10"


class TestSnapshotServiceHelpers:
    """Tests for internal snapshot service helper functions."""

    def test_get_current_utc_period_format(self):
        """Test that current UTC period returns YYYY-MM format."""
        period = _get_current_utc_period()
        import re
        assert re.match(r"^\d{4}-\d{2}$", period)
        year, month = map(int, period.split("-"))
        assert 2000 <= year <= 2100
        assert 1 <= month <= 12

    def test_build_snapshot_from_project(self):
        """Test building snapshot data from ProjectRecord."""
        project = ProjectRecord(
            project_id="P01",
            name="Test Project",
            location="Madhya Pradesh",
            sector="Roads",
            progress=78.0,
            planned_progress=75.0,
            delay_days=0,
            budget_used=72.0,
            budget_total_crore=120.0,
            contractor="Aarav Infra Ltd",
        )

        with patch("app.services.project_service.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 10, 15, 10, 30, 0, tzinfo=timezone.utc)
            mock_dt.timezone = timezone

            snapshot = _build_snapshot_from_project(project, "2026-10")

        assert snapshot["project_id"] == "P01"
        assert snapshot["snapshot_period"] == "2026-10"
        assert snapshot["progress"] == 78.0
        assert snapshot["planned_progress"] == 75.0
        assert snapshot["delay_days"] == 0
        assert snapshot["budget_used"] == 72.0
        assert snapshot["budget_total_crore"] == 120.0
        assert snapshot["contractor"] == "Aarav Infra Ltd"
        assert snapshot["sector"] == "Roads"
        assert snapshot["location"] == "Madhya Pradesh"
        assert "recorded_at" in snapshot
        assert "risk_snapshot" in snapshot
        assert snapshot["risk_snapshot"]["overall_level"] in ["HIGH", "MEDIUM", "LOW"]

    def test_validate_snapshot_data_valid(self):
        """Test validation passes for valid data."""
        data = {
            "project_id": "P01",
            "snapshot_period": "2026-10",
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "progress": 78.0,
            "planned_progress": 75.0,
            "delay_days": 0,
            "budget_used": 72.0,
            "budget_total_crore": 120.0,
        }
        # Should not raise
        _validate_snapshot_data(data)

    def test_validate_snapshot_data_invalid_progress(self):
        """Test validation fails for invalid progress."""
        data = {
            "project_id": "P01",
            "snapshot_period": "2026-10",
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "progress": 150.0,  # Invalid
            "planned_progress": 75.0,
            "delay_days": 0,
            "budget_used": 72.0,
            "budget_total_crore": 120.0,
        }
        with pytest.raises(ValueError, match="progress must be between 0 and 100"):
            _validate_snapshot_data(data)

    def test_validate_snapshot_data_invalid_planned_progress(self):
        """Test validation fails for invalid planned_progress."""
        data = {
            "project_id": "P01",
            "snapshot_period": "2026-10",
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "progress": 78.0,
            "planned_progress": -10.0,  # Invalid
            "delay_days": 0,
            "budget_used": 72.0,
            "budget_total_crore": 120.0,
        }
        with pytest.raises(ValueError, match="planned_progress must be between 0 and 100"):
            _validate_snapshot_data(data)

    def test_validate_snapshot_data_negative_delay(self):
        """Test validation fails for negative delay_days."""
        data = {
            "project_id": "P01",
            "snapshot_period": "2026-10",
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "progress": 78.0,
            "planned_progress": 75.0,
            "delay_days": -5,  # Invalid
            "budget_used": 72.0,
            "budget_total_crore": 120.0,
        }
        with pytest.raises(ValueError, match="delay_days must be non-negative"):
            _validate_snapshot_data(data)

    def test_validate_snapshot_data_invalid_budget_used(self):
        """Test validation fails for invalid budget_used."""
        data = {
            "project_id": "P01",
            "snapshot_period": "2026-10",
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "progress": 78.0,
            "planned_progress": 75.0,
            "delay_days": 0,
            "budget_used": 150.0,  # Invalid
            "budget_total_crore": 120.0,
        }
        with pytest.raises(ValueError, match="budget_used must be between 0 and 100"):
            _validate_snapshot_data(data)

    def test_validate_snapshot_data_negative_budget_total(self):
        """Test validation fails for negative budget_total_crore."""
        data = {
            "project_id": "P01",
            "snapshot_period": "2026-10",
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "progress": 78.0,
            "planned_progress": 75.0,
            "delay_days": 0,
            "budget_used": 72.0,
            "budget_total_crore": -10.0,  # Invalid
        }
        with pytest.raises(ValueError, match="budget_total_crore must be non-negative"):
            _validate_snapshot_data(data)

    def test_validate_snapshot_data_missing_project_id(self):
        """Test validation fails for missing project_id."""
        data = {
            "snapshot_period": "2026-10",
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "progress": 78.0,
            "planned_progress": 75.0,
            "delay_days": 0,
            "budget_used": 72.0,
            "budget_total_crore": 120.0,
        }
        with pytest.raises(ValueError, match="project_id is required"):
            _validate_snapshot_data(data)

    def test_validate_snapshot_data_missing_period(self):
        """Test validation fails for missing snapshot_period."""
        data = {
            "project_id": "P01",
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "progress": 78.0,
            "planned_progress": 75.0,
            "delay_days": 0,
            "budget_used": 72.0,
            "budget_total_crore": 120.0,
        }
        with pytest.raises(ValueError, match="snapshot_period is required"):
            _validate_snapshot_data(data)

    def test_validate_snapshot_data_missing_recorded_at(self):
        """Test validation fails for missing recorded_at."""
        data = {
            "project_id": "P01",
            "snapshot_period": "2026-10",
            "progress": 78.0,
            "planned_progress": 75.0,
            "delay_days": 0,
            "budget_used": 72.0,
            "budget_total_crore": 120.0,
        }
        with pytest.raises(ValueError, match="recorded_at is required"):
            _validate_snapshot_data(data)


class TestSnapshotFirebaseOperations:
    """Tests for snapshot Firebase operations (mocked)."""

    @patch("app.services.project_service.get_project_by_id")
    @patch("app.services.project_service.check_snapshot_exists")
    @patch("app.services.project_service.save_project_snapshot_to_firebase")
    @patch("app.services.project_service.fetch_project_snapshot_from_firebase")
    def test_create_project_snapshot_success(
        self,
        mock_fetch_snapshot,
        mock_save_snapshot,
        mock_check_exists,
        mock_get_project,
    ):
        """Test successful snapshot creation."""
        # Setup mocks
        mock_project = ProjectRecord(
            project_id="P01",
            name="Test Project",
            location="Madhya Pradesh",
            sector="Roads",
            progress=78.0,
            planned_progress=75.0,
            delay_days=0,
            budget_used=72.0,
            budget_total_crore=120.0,
            contractor="Aarav Infra Ltd",
        )
        mock_get_project.return_value = mock_project
        mock_check_exists.return_value = False
        mock_save_snapshot.return_value = True
        mock_fetch_snapshot.return_value = {
            "project_id": "P01",
            "snapshot_period": "2026-10",
            "recorded_at": "2026-10-15T10:30:00+00:00",
            "progress": 78.0,
            "planned_progress": 75.0,
            "delay_days": 0,
            "budget_used": 72.0,
            "budget_total_crore": 120.0,
            "contractor": "Aarav Infra Ltd",
            "sector": "Roads",
            "location": "Madhya Pradesh",
            "risk_snapshot": {"overall_score": 25, "overall_level": "LOW"},
        }

        with patch("app.services.project_service._get_current_utc_period", return_value="2026-10"):
            snapshot = create_project_snapshot("P01", None)

        assert snapshot["project_id"] == "P01"
        assert snapshot["snapshot_period"] == "2026-10"
        assert snapshot["progress"] == 78.0
        mock_get_project.assert_called_once_with("P01")
        mock_check_exists.assert_called_once_with("P01", "2026-10")
        mock_save_snapshot.assert_called_once()

    @patch("app.services.project_service.get_project_by_id")
    def test_create_project_snapshot_project_not_found(self, mock_get_project):
        """Test snapshot creation fails when project not found."""
        mock_get_project.return_value = None

        with pytest.raises(ValueError, match="Project 'P99' not found in database"):
            create_project_snapshot("P99", "2026-10")

    @patch("app.services.project_service.get_project_by_id")
    @patch("app.services.project_service.check_snapshot_exists")
    @patch("app.services.project_service.fetch_project_snapshot_from_firebase")
    def test_create_project_snapshot_duplicate(
        self,
        mock_fetch_snapshot,
        mock_check_exists,
        mock_get_project,
    ):
        """Test snapshot creation fails when duplicate exists."""
        mock_project = ProjectRecord(
            project_id="P01",
            name="Test Project",
            location="Madhya Pradesh",
            sector="Roads",
            progress=78.0,
            planned_progress=75.0,
            delay_days=0,
            budget_used=72.0,
            budget_total_crore=120.0,
            contractor="Aarav Infra Ltd",
        )
        mock_get_project.return_value = mock_project
        mock_check_exists.return_value = True
        mock_fetch_snapshot.return_value = {
            "project_id": "P01",
            "snapshot_period": "2026-10",
            "recorded_at": "2026-10-15T10:30:00+00:00",
            "progress": 78.0,
            "planned_progress": 75.0,
            "delay_days": 0,
            "budget_used": 72.0,
            "budget_total_crore": 120.0,
            "contractor": "Aarav Infra Ltd",
            "sector": "Roads",
            "location": "Madhya Pradesh",
            "risk_snapshot": {"overall_score": 25, "overall_level": "LOW"},
        }

        with pytest.raises(ValueError, match="already exists"):
            create_project_snapshot("P01", "2026-10")

    @patch("app.services.project_service.get_project_by_id")
    @patch("app.services.project_service.check_snapshot_exists")
    @patch("app.services.project_service.save_project_snapshot_to_firebase")
    def test_create_project_snapshot_save_fails(
        self,
        mock_save_snapshot,
        mock_check_exists,
        mock_get_project,
    ):
        """Test snapshot creation fails when Firebase save fails."""
        mock_project = ProjectRecord(
            project_id="P01",
            name="Test Project",
            location="Madhya Pradesh",
            sector="Roads",
            progress=78.0,
            planned_progress=75.0,
            delay_days=0,
            budget_used=72.0,
            budget_total_crore=120.0,
            contractor="Aarav Infra Ltd",
        )
        mock_get_project.return_value = mock_project
        mock_check_exists.return_value = False
        mock_save_snapshot.return_value = False

        with pytest.raises(RuntimeError, match="Failed to save snapshot"):
            create_project_snapshot("P01", "2026-10")

    @patch("app.services.project_service.fetch_project_snapshot_from_firebase")
    def test_get_project_snapshot_success(self, mock_fetch):
        """Test retrieving a specific snapshot."""
        mock_fetch.return_value = {
            "project_id": "P01",
            "snapshot_period": "2026-10",
            "recorded_at": "2026-10-15T10:30:00+00:00",
            "progress": 78.0,
            "planned_progress": 75.0,
            "delay_days": 0,
            "budget_used": 72.0,
            "budget_total_crore": 120.0,
            "contractor": "Aarav Infra Ltd",
            "sector": "Roads",
            "location": "Madhya Pradesh",
            "risk_snapshot": {"overall_score": 25, "overall_level": "LOW"},
        }

        snapshot = get_project_snapshot("P01", "2026-10")
        assert snapshot is not None
        assert snapshot["project_id"] == "P01"
        assert snapshot["snapshot_period"] == "2026-10"

    @patch("app.services.project_service.fetch_project_snapshot_from_firebase")
    def test_get_project_snapshot_not_found(self, mock_fetch):
        """Test retrieving a non-existent snapshot returns None."""
        mock_fetch.return_value = None

        snapshot = get_project_snapshot("P01", "2026-10")
        assert snapshot is None

    @patch("app.services.project_service.fetch_project_snapshot_from_firebase")
    def test_get_project_snapshot_invalid_period(self, mock_fetch):
        """Test retrieving with invalid period format raises ValueError."""
        with pytest.raises(ValueError, match="period must be in YYYY-MM format"):
            get_project_snapshot("P01", "invalid-period")

    @patch("app.services.project_service.fetch_all_project_snapshots_from_firebase")
    def test_get_project_snapshots_success(self, mock_fetch_all):
        """Test retrieving all snapshots for a project."""
        mock_fetch_all.return_value = {
            "2026-08": {
                "project_id": "P01",
                "snapshot_period": "2026-08",
                "recorded_at": "2026-08-15T10:30:00+00:00",
                "progress": 60.0,
                "planned_progress": 65.0,
                "delay_days": 10,
                "budget_used": 65.0,
                "budget_total_crore": 120.0,
                "contractor": "Aarav Infra Ltd",
                "sector": "Roads",
                "location": "Madhya Pradesh",
                "risk_snapshot": {"overall_score": 35, "overall_level": "MEDIUM"},
            },
            "2026-10": {
                "project_id": "P01",
                "snapshot_period": "2026-10",
                "recorded_at": "2026-10-15T10:30:00+00:00",
                "progress": 78.0,
                "planned_progress": 75.0,
                "delay_days": 0,
                "budget_used": 72.0,
                "budget_total_crore": 120.0,
                "contractor": "Aarav Infra Ltd",
                "sector": "Roads",
                "location": "Madhya Pradesh",
                "risk_snapshot": {"overall_score": 25, "overall_level": "LOW"},
            },
        }

        snapshots = get_project_snapshots("P01")
        assert len(snapshots) == 2
        # Should be sorted chronologically
        assert snapshots[0]["snapshot_period"] == "2026-08"
        assert snapshots[1]["snapshot_period"] == "2026-10"

    @patch("app.services.project_service.fetch_all_project_snapshots_from_firebase")
    def test_get_project_snapshots_empty(self, mock_fetch_all):
        """Test retrieving snapshots when none exist."""
        mock_fetch_all.return_value = {}

        snapshots = get_project_snapshots("P01")
        assert snapshots == []

    @patch("app.services.project_service.fetch_all_project_snapshots_from_firebase")
    def test_get_project_snapshots_firebase_error(self, mock_fetch_all):
        """Test retrieving snapshots when Firebase connection fails."""
        mock_fetch_all.return_value = None

        with pytest.raises(RuntimeError, match="Unable to connect to Firebase"):
            get_project_snapshots("P01")


class TestSnapshotAPIEndpoints:
    """Tests for snapshot API endpoints (mocked)."""

    @pytest.fixture(autouse=True)
    def setup_auth(self):
        """Set up authentication mock for all tests in this class."""
        # Create a fake JWT token that passes development mode verification
        import jwt
        self.fake_token = jwt.encode(
            {"uid": "test-user-123", "role": "officer", "email": "test@example.com"},
            "fake-secret",
            algorithm="HS256"
        )
        self.auth_headers = {"Authorization": f"Bearer {self.fake_token}"}

    @patch("app.api.projects.get_project_by_id")
    @patch("app.api.projects.create_project_snapshot")
    def test_create_snapshot_endpoint_success(
        self,
        mock_create_snapshot,
        mock_get_project,
    ):
        """Test POST /projects/{id}/snapshots success."""
        from fastapi.testclient import TestClient
        from app.main import app

        mock_get_project.return_value = ProjectRecord(
            project_id="P01",
            name="Test",
            location="Test",
            sector="Test",
            progress=50.0,
            planned_progress=50.0,
            delay_days=0,
            budget_used=50.0,
            budget_total_crore=100.0,
            contractor="Test",
        )
        mock_create_snapshot.return_value = {
            "project_id": "P01",
            "snapshot_period": "2026-10",
            "recorded_at": "2026-10-15T10:30:00+00:00",
            "progress": 50.0,
            "planned_progress": 50.0,
            "delay_days": 0,
            "budget_used": 50.0,
            "budget_total_crore": 100.0,
            "contractor": "Test",
            "sector": "Test",
            "location": "Test",
            "risk_snapshot": {"overall_score": 20, "overall_level": "LOW"},
        }

        client = TestClient(app)
        response = client.post(
            "/projects/P01/snapshots",
            json={},
            headers=self.auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["project_id"] == "P01"
        assert data["snapshot_period"] == "2026-10"

    @patch("app.api.projects.get_project_by_id")
    @patch("app.api.projects.create_project_snapshot")
    def test_create_snapshot_endpoint_duplicate(
        self,
        mock_create_snapshot,
        mock_get_project,
    ):
        """Test POST /projects/{id}/snapshots duplicate handling."""
        from fastapi.testclient import TestClient
        from app.main import app

        mock_get_project.return_value = ProjectRecord(
            project_id="P01",
            name="Test",
            location="Test",
            sector="Test",
            progress=50.0,
            planned_progress=50.0,
            delay_days=0,
            budget_used=50.0,
            budget_total_crore=100.0,
            contractor="Test",
        )
        mock_create_snapshot.side_effect = ValueError(
            "Snapshot for project 'P01' period '2026-10' already exists."
        )

        client = TestClient(app)
        response = client.post(
            "/projects/P01/snapshots",
            json={"snapshot_period": "2026-10"},
            headers=self.auth_headers,
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    @patch("app.api.projects.get_project_by_id")
    @patch("app.api.projects.get_project_snapshots")
    def test_list_snapshots_endpoint_success(
        self,
        mock_get_snapshots,
        mock_get_project,
    ):
        """Test GET /projects/{id}/snapshots success."""
        from fastapi.testclient import TestClient
        from app.main import app

        mock_get_project.return_value = ProjectRecord(
            project_id="P01",
            name="Test",
            location="Test",
            sector="Test",
            progress=50.0,
            planned_progress=50.0,
            delay_days=0,
            budget_used=50.0,
            budget_total_crore=100.0,
            contractor="Test",
        )
        mock_get_snapshots.return_value = [
            {
                "project_id": "P01",
                "snapshot_period": "2026-08",
                "recorded_at": "2026-08-15T10:30:00+00:00",
                "progress": 40.0,
                "planned_progress": 50.0,
                "delay_days": 5,
                "budget_used": 45.0,
                "budget_total_crore": 100.0,
                "contractor": "Test",
                "sector": "Test",
                "location": "Test",
                "risk_snapshot": {"overall_score": 30, "overall_level": "MEDIUM"},
            },
            {
                "project_id": "P01",
                "snapshot_period": "2026-10",
                "recorded_at": "2026-10-15T10:30:00+00:00",
                "progress": 50.0,
                "planned_progress": 50.0,
                "delay_days": 0,
                "budget_used": 50.0,
                "budget_total_crore": 100.0,
                "contractor": "Test",
                "sector": "Test",
                "location": "Test",
                "risk_snapshot": {"overall_score": 20, "overall_level": "LOW"},
            },
        ]

        client = TestClient(app)
        response = client.get("/projects/P01/snapshots", headers=self.auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["project_id"] == "P01"
        assert data["total_count"] == 2
        assert len(data["snapshots"]) == 2
        assert data["snapshots"][0]["snapshot_period"] == "2026-08"
        assert data["snapshots"][1]["snapshot_period"] == "2026-10"

    @patch("app.api.projects.get_project_by_id")
    def test_list_snapshots_endpoint_project_not_found(
        self,
        mock_get_project,
    ):
        """Test GET /projects/{id}/snapshots when project not found."""
        from fastapi.testclient import TestClient
        from app.main import app

        mock_get_project.return_value = None

        client = TestClient(app)
        response = client.get("/projects/P99/snapshots", headers=self.auth_headers)
        assert response.status_code == 404

    @patch("app.api.projects.get_project_snapshot")
    def test_get_snapshot_endpoint_success(self, mock_get_snapshot):
        """Test GET /projects/{id}/snapshots/{period} success."""
        from fastapi.testclient import TestClient
        from app.main import app

        mock_get_snapshot.return_value = {
            "project_id": "P01",
            "snapshot_period": "2026-10",
            "recorded_at": "2026-10-15T10:30:00+00:00",
            "progress": 50.0,
            "planned_progress": 50.0,
            "delay_days": 0,
            "budget_used": 50.0,
            "budget_total_crore": 100.0,
            "contractor": "Test",
            "sector": "Test",
            "location": "Test",
            "risk_snapshot": {"overall_score": 20, "overall_level": "LOW"},
        }

        client = TestClient(app)
        response = client.get("/projects/P01/snapshots/2026-10", headers=self.auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["project_id"] == "P01"
        assert data["snapshot_period"] == "2026-10"

    @patch("app.api.projects.get_project_snapshot")
    def test_get_snapshot_endpoint_not_found(self, mock_get_snapshot):
        """Test GET /projects/{id}/snapshots/{period} when not found."""
        from fastapi.testclient import TestClient
        from app.main import app

        mock_get_snapshot.return_value = None

        client = TestClient(app)
        response = client.get("/projects/P01/snapshots/2026-10", headers=self.auth_headers)
        assert response.status_code == 404

    def test_get_snapshot_endpoint_invalid_period(self):
        """Test GET /projects/{id}/snapshots/{period} with invalid period format."""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)
        response = client.get("/projects/P01/snapshots/invalid", headers=self.auth_headers)
        assert response.status_code == 400
        assert "YYYY-MM" in response.json()["detail"]


class TestRiskEngineUnchanged:
    """Verify the deterministic Risk Engine remains unchanged."""

    def test_risk_engine_imports(self):
        """Test that risk engine can be imported."""
        from app.services.risk_engine import calculate_risk
        assert calculate_risk is not None

    def test_risk_engine_calculation(self):
        """Test that risk engine calculates correctly."""
        from app.services.risk_engine import calculate_risk
        from app.models.project import ProjectRecord

        project = ProjectRecord(
            project_id="P01",
            name="Test",
            location="Test",
            sector="Test",
            progress=78.0,
            planned_progress=75.0,
            delay_days=0,
            budget_used=72.0,
            budget_total_crore=120.0,
            contractor="Test",
        )

        risk = calculate_risk(project)
        assert risk.overall_score >= 0
        assert risk.overall_score <= 100
        assert risk.overall_level in ["HIGH", "MEDIUM", "LOW"]
        assert risk.progress_risk >= 0
        assert risk.delay_risk >= 0
        assert risk.budget_risk >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])