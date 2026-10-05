"""Tests for project outcome functionality."""

import pytest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

from app.models.outcome import (
    ProjectOutcome,
    ProjectOutcomeCreateRequest,
    ProjectOutcomeResponse,
)
from app.services.project_service import (
    _build_outcome_from_project,
    _validate_outcome_data,
    create_project_outcome,
    get_project_outcome,
)
from app.models.project import ProjectRecord
from app.services.firebase_service import (
    save_project_outcome_to_firebase,
    fetch_project_outcome_from_firebase,
    check_outcome_exists,
)


class TestOutcomeModels:
    """Tests for outcome Pydantic models."""

    def test_project_outcome_valid(self):
        """Test creating a valid ProjectOutcome."""
        outcome = ProjectOutcome(
            project_id="P01",
            completion_status="COMPLETED",
            actual_completion_date="2026-12-31",
            planned_completion_date="2026-10-31",
            final_progress=100.0,
            final_delay_days=61,
            final_budget_used=95.0,
            final_budget_variance_percent=5.5,
            final_cost_crore=126.6,
            recorded_at=datetime.now(timezone.utc),
            recorded_by_uid="officer-123",
            notes="Project completed successfully",
        )
        assert outcome.project_id == "P01"
        assert outcome.completion_status == "COMPLETED"
        assert outcome.final_delay_days == 61

    def test_project_outcome_invalid_status(self):
        """Test that invalid completion status raises validation error."""
        with pytest.raises(ValueError, match="completion_status must be one of"):
            ProjectOutcome(
                project_id="P01",
                completion_status="INVALID",
                actual_completion_date="2026-12-31",
                final_progress=100.0,
                final_delay_days=0,
                final_budget_used=95.0,
                recorded_at=datetime.now(timezone.utc),
                recorded_by_uid="officer-123",
            )

    def test_project_outcome_invalid_date_format(self):
        """Test that invalid date format raises validation error."""
        with pytest.raises(ValueError, match="Date must be in YYYY-MM-DD format"):
            ProjectOutcome(
                project_id="P01",
                completion_status="COMPLETED",
                actual_completion_date="31-12-2026",  # Invalid format
                final_progress=100.0,
                final_delay_days=0,
                final_budget_used=95.0,
                recorded_at=datetime.now(timezone.utc),
                recorded_by_uid="officer-123",
            )

    def test_project_outcome_invalid_progress(self):
        """Test that out-of-range progress raises validation error."""
        with pytest.raises(ValueError):
            ProjectOutcome(
                project_id="P01",
                completion_status="COMPLETED",
                actual_completion_date="2026-12-31",
                final_progress=150.0,  # Out of range
                final_delay_days=0,
                final_budget_used=95.0,
                recorded_at=datetime.now(timezone.utc),
                recorded_by_uid="officer-123",
            )

    def test_outcome_create_request_valid(self):
        """Test valid outcome create request."""
        request = ProjectOutcomeCreateRequest(
            completion_status="COMPLETED",
            actual_completion_date="2026-12-31",
            planned_completion_date="2026-10-31",
            final_progress=100.0,
            final_budget_used=95.0,
            final_budget_variance_percent=5.5,
            final_cost_crore=126.6,
            notes="Completed successfully",
        )
        assert request.completion_status == "COMPLETED"
        assert request.actual_completion_date == "2026-12-31"

    def test_outcome_response(self):
        """Test outcome response model."""
        outcome = ProjectOutcome(
            project_id="P01",
            completion_status="COMPLETED",
            actual_completion_date="2026-12-31",
            final_progress=100.0,
            final_delay_days=61,
            final_budget_used=95.0,
            recorded_at=datetime.now(timezone.utc),
            recorded_by_uid="officer-123",
        )
        response = ProjectOutcomeResponse(project_id="P01", outcome=outcome)
        assert response.project_id == "P01"
        assert response.outcome is not None
        assert response.outcome.completion_status == "COMPLETED"

    def test_outcome_response_null(self):
        """Test outcome response with no outcome."""
        response = ProjectOutcomeResponse(project_id="P01", outcome=None)
        assert response.project_id == "P01"
        assert response.outcome is None


class TestOutcomeServiceHelpers:
    """Tests for internal outcome service helper functions."""

    def test_build_outcome_from_project(self):
        """Test building outcome from project and payload."""
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

        payload = {
            "completion_status": "COMPLETED",
            "actual_completion_date": "2026-12-31",
            "planned_completion_date": "2026-10-31",
            "final_progress": 100.0,
            "final_delay_days": 61,
            "final_budget_used": 95.0,
            "final_budget_variance_percent": 5.5,
            "final_cost_crore": 126.6,
            "notes": "Completed",
        }

        with patch("app.services.project_service.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 12, 31, 10, 30, 0, tzinfo=timezone.utc)
            mock_dt.timezone = timezone
            mock_dt.strptime = datetime.strptime

            outcome = _build_outcome_from_project(project, payload, "officer-123")

        assert outcome["project_id"] == "P01"
        assert outcome["completion_status"] == "COMPLETED"
        assert outcome["actual_completion_date"] == "2026-12-31"
        assert outcome["planned_completion_date"] == "2026-10-31"
        assert outcome["final_progress"] == 100.0
        assert outcome["final_budget_used"] == 95.0
        assert outcome["final_budget_variance_percent"] == 5.5
        assert outcome["final_cost_crore"] == 126.6
        assert outcome["recorded_by_uid"] == "officer-123"
        assert outcome["notes"] == "Completed"

    def test_build_outcome_from_project_with_delay_calculation(self):
        """Test that delay days are calculated from dates when both provided."""
        project = ProjectRecord(
            project_id="P01",
            name="Test",
            location="MP",
            sector="Roads",
            progress=78.0,
            planned_progress=75.0,
            delay_days=0,
            budget_used=72.0,
            budget_total_crore=120.0,
            contractor="Test",
        )

        payload = {
            "completion_status": "COMPLETED",
            "actual_completion_date": "2026-12-31",
            "planned_completion_date": "2026-10-31",
            "final_progress": 100.0,
            "final_delay_days": 0,  # Should be overridden by date calculation
            "final_budget_used": 95.0,
        }

        with patch("app.services.project_service.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 12, 31, 10, 30, 0, tzinfo=timezone.utc)
            mock_dt.timezone = timezone
            mock_dt.strptime = datetime.strptime

            outcome = _build_outcome_from_project(project, payload, "officer-123")

        # Delay should be calculated: Dec 31 - Oct 31 = 61 days
        assert outcome["final_delay_days"] == 61

    def test_build_outcome_from_project_with_budget_variance(self):
        """Test that budget variance is calculated from final cost."""
        project = ProjectRecord(
            project_id="P01",
            name="Test",
            location="MP",
            sector="Roads",
            progress=78.0,
            planned_progress=75.0,
            delay_days=0,
            budget_used=72.0,
            budget_total_crore=120.0,
            contractor="Test",
        )

        payload = {
            "completion_status": "COMPLETED",
            "actual_completion_date": "2026-12-31",
            "final_progress": 100.0,
            "final_budget_used": 95.0,
            "final_cost_crore": 126.6,  # Should calculate variance
        }

        with patch("app.services.project_service.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 12, 31, 10, 30, 0, tzinfo=timezone.utc)
            mock_dt.timezone = timezone
            mock_dt.strptime = datetime.strptime

            outcome = _build_outcome_from_project(project, payload, "officer-123")

        # Variance = (126.6 - 120) / 120 * 100 = 5.5%
        assert outcome["final_budget_variance_percent"] == 5.5

    def test_validate_outcome_data_valid(self):
        """Test validation passes for valid outcome data."""
        project = ProjectRecord(
            project_id="P01",
            name="Test",
            location="MP",
            sector="Roads",
            progress=78.0,
            planned_progress=75.0,
            delay_days=0,
            budget_used=72.0,
            budget_total_crore=120.0,
            contractor="Test",
        )

        outcome_data = {
            "completion_status": "COMPLETED",
            "actual_completion_date": "2026-12-31",
            "planned_completion_date": "2026-10-31",
            "final_progress": 100.0,
            "final_delay_days": 61,
            "final_budget_used": 95.0,
        }

        # Should not raise
        _validate_outcome_data(outcome_data, project)

    def test_validate_outcome_data_missing_completion_status(self):
        """Test validation fails for missing completion status."""
        project = ProjectRecord(
            project_id="P01", name="Test", location="MP", sector="Roads",
            progress=78.0, planned_progress=75.0, delay_days=0,
            budget_used=72.0, budget_total_crore=120.0, contractor="Test",
        )

        outcome_data = {
            "actual_completion_date": "2026-12-31",
            "final_progress": 100.0,
            "final_budget_used": 95.0,
        }

        with pytest.raises(ValueError, match="completion_status must be one of"):
            _validate_outcome_data(outcome_data, project)

    def test_validate_outcome_data_missing_actual_date(self):
        """Test validation fails for missing actual completion date."""
        project = ProjectRecord(
            project_id="P01", name="Test", location="MP", sector="Roads",
            progress=78.0, planned_progress=75.0, delay_days=0,
            budget_used=72.0, budget_total_crore=120.0, contractor="Test",
        )

        outcome_data = {
            "completion_status": "COMPLETED",
            "final_progress": 100.0,
            "final_budget_used": 95.0,
        }

        with pytest.raises(ValueError, match="actual_completion_date is required"):
            _validate_outcome_data(outcome_data, project)

    def test_validate_outcome_data_invalid_progress(self):
        """Test validation fails for invalid progress."""
        project = ProjectRecord(
            project_id="P01", name="Test", location="MP", sector="Roads",
            progress=78.0, planned_progress=75.0, delay_days=0,
            budget_used=72.0, budget_total_crore=120.0, contractor="Test",
        )

        outcome_data = {
            "completion_status": "COMPLETED",
            "actual_completion_date": "2026-12-31",
            "final_progress": 150.0,  # Invalid
            "final_budget_used": 95.0,
        }

        with pytest.raises(ValueError, match="final_progress must be between 0 and 100"):
            _validate_outcome_data(outcome_data, project)

    def test_validate_outcome_data_invalid_budget(self):
        """Test validation fails for invalid budget."""
        project = ProjectRecord(
            project_id="P01", name="Test", location="MP", sector="Roads",
            progress=78.0, planned_progress=75.0, delay_days=0,
            budget_used=72.0, budget_total_crore=120.0, contractor="Test",
        )

        outcome_data = {
            "completion_status": "COMPLETED",
            "actual_completion_date": "2026-12-31",
            "final_progress": 100.0,
            "final_budget_used": 150.0,  # Invalid
        }

        with pytest.raises(ValueError, match="final_budget_used must be between 0 and 100"):
            _validate_outcome_data(outcome_data, project)


class TestOutcomeFirebaseOperations:
    """Tests for outcome Firebase operations (mocked)."""

    @patch("app.services.project_service.get_project_by_id")
    @patch("app.services.project_service.check_outcome_exists")
    @patch("app.services.project_service.save_project_outcome_to_firebase")
    @patch("app.services.project_service.fetch_project_outcome_from_firebase")
    def test_create_project_outcome_success(
        self,
        mock_fetch_outcome,
        mock_save_outcome,
        mock_check_exists,
        mock_get_project,
    ):
        """Test successful outcome creation."""
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
        mock_save_outcome.return_value = True
        mock_fetch_outcome.return_value = {
            "project_id": "P01",
            "completion_status": "COMPLETED",
            "actual_completion_date": "2026-12-31",
            "planned_completion_date": "2026-10-31",
            "final_progress": 100.0,
            "final_delay_days": 61,
            "final_budget_used": 95.0,
            "final_budget_variance_percent": 5.5,
            "final_cost_crore": 126.6,
            "recorded_at": "2026-12-31T10:30:00+00:00",
            "recorded_by_uid": "officer-123",
            "notes": "Completed",
        }

        outcome = create_project_outcome("P01", {
            "completion_status": "COMPLETED",
            "actual_completion_date": "2026-12-31",
            "planned_completion_date": "2026-10-31",
            "final_progress": 100.0,
            "final_budget_used": 95.0,
            "final_cost_crore": 126.6,
        }, "officer-123")

        assert outcome["project_id"] == "P01"
        assert outcome["completion_status"] == "COMPLETED"
        mock_get_project.assert_called_once_with("P01")
        mock_check_exists.assert_called_once_with("P01")
        mock_save_outcome.assert_called_once()

    @patch("app.services.project_service.get_project_by_id")
    def test_create_project_outcome_project_not_found(self, mock_get_project):
        """Test outcome creation fails when project not found."""
        mock_get_project.return_value = None

        with pytest.raises(ValueError, match="Project 'P99' not found in database"):
            create_project_outcome("P99", {
                "completion_status": "COMPLETED",
                "actual_completion_date": "2026-12-31",
                "final_progress": 100.0,
                "final_budget_used": 95.0,
            }, "officer-123")

    @patch("app.services.project_service.get_project_by_id")
    @patch("app.services.project_service.check_outcome_exists")
    @patch("app.services.project_service.fetch_project_outcome_from_firebase")
    def test_create_project_outcome_duplicate(
        self,
        mock_fetch_outcome,
        mock_check_exists,
        mock_get_project,
    ):
        """Test outcome creation fails when duplicate exists."""
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
        mock_fetch_outcome.return_value = {
            "project_id": "P01",
            "completion_status": "COMPLETED",
            "actual_completion_date": "2026-12-31",
            "planned_completion_date": "2026-10-31",
            "final_progress": 100.0,
            "final_delay_days": 61,
            "final_budget_used": 95.0,
            "final_budget_variance_percent": 5.5,
            "final_cost_crore": 126.6,
            "recorded_at": "2026-12-31T10:30:00+00:00",
            "recorded_by_uid": "officer-123",
            "notes": "Completed",
        }

        with pytest.raises(ValueError, match="already exists"):
            create_project_outcome("P01", {
                "completion_status": "COMPLETED",
                "actual_completion_date": "2026-12-31",
                "final_progress": 100.0,
                "final_budget_used": 95.0,
            }, "officer-123")

    @patch("app.services.project_service.get_project_by_id")
    @patch("app.services.project_service.check_outcome_exists")
    @patch("app.services.project_service.save_project_outcome_to_firebase")
    def test_create_project_outcome_save_fails(
        self,
        mock_save_outcome,
        mock_check_exists,
        mock_get_project,
    ):
        """Test outcome creation fails when Firebase save fails."""
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
        mock_save_outcome.return_value = False

        with pytest.raises(RuntimeError, match="Failed to save outcome"):
            create_project_outcome("P01", {
                "completion_status": "COMPLETED",
                "actual_completion_date": "2026-12-31",
                "final_progress": 100.0,
                "final_budget_used": 95.0,
            }, "officer-123")

    @patch("app.services.project_service.fetch_project_outcome_from_firebase")
    def test_get_project_outcome_success(self, mock_fetch):
        """Test retrieving an outcome."""
        mock_fetch.return_value = {
            "project_id": "P01",
            "completion_status": "COMPLETED",
            "actual_completion_date": "2026-12-31",
            "planned_completion_date": "2026-10-31",
            "final_progress": 100.0,
            "final_delay_days": 61,
            "final_budget_used": 95.0,
            "final_budget_variance_percent": 5.5,
            "final_cost_crore": 126.6,
            "recorded_at": "2026-12-31T10:30:00+00:00",
            "recorded_by_uid": "officer-123",
            "notes": "Completed successfully",
        }

        outcome = get_project_outcome("P01")
        assert outcome is not None
        assert outcome["project_id"] == "P01"
        assert outcome["completion_status"] == "COMPLETED"

    @patch("app.services.project_service.fetch_project_outcome_from_firebase")
    def test_get_project_outcome_not_found(self, mock_fetch):
        """Test retrieving non-existent outcome returns None."""
        mock_fetch.return_value = None

        outcome = get_project_outcome("P01")
        assert outcome is None


class TestOutcomeAPIEndpoints:
    """Tests for outcome API endpoints (mocked)."""

    @pytest.fixture(autouse=True)
    def setup_auth(self):
        """Set up authentication mock for all tests in this class."""
        import jwt
        self.fake_token = jwt.encode(
            {"uid": "test-user-123", "role": "officer", "email": "test@example.com"},
            "fake-secret",
            algorithm="HS256"
        )
        self.auth_headers = {"Authorization": f"Bearer {self.fake_token}"}

    @patch("app.api.projects.get_project_by_id")
    @patch("app.api.projects.create_project_outcome")
    def test_create_outcome_endpoint_success(
        self,
        mock_create_outcome,
        mock_get_project,
    ):
        """Test POST /projects/{id}/outcome success."""
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
        mock_create_outcome.return_value = {
            "project_id": "P01",
            "completion_status": "COMPLETED",
            "actual_completion_date": "2026-12-31",
            "planned_completion_date": "2026-10-31",
            "final_progress": 100.0,
            "final_delay_days": 61,
            "final_budget_used": 95.0,
            "final_budget_variance_percent": 5.5,
            "final_cost_crore": 126.6,
            "recorded_at": "2026-12-31T10:30:00+00:00",
            "recorded_by_uid": "test-user-123",
            "notes": "Completed",
        }

        client = TestClient(app)
        response = client.post(
            "/projects/P01/outcome",
            json={
                "completion_status": "COMPLETED",
                "actual_completion_date": "2026-12-31",
                "planned_completion_date": "2026-10-31",
                "final_progress": 100.0,
                "final_budget_used": 95.0,
                "final_cost_crore": 126.6,
            },
            headers=self.auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["project_id"] == "P01"
        assert data["outcome"]["completion_status"] == "COMPLETED"

    @patch("app.api.projects.get_project_by_id")
    @patch("app.api.projects.create_project_outcome")
    def test_create_outcome_endpoint_duplicate(
        self,
        mock_create_outcome,
        mock_get_project,
    ):
        """Test POST /projects/{id}/outcome duplicate handling."""
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
        mock_create_outcome.side_effect = ValueError(
            "Outcome for project 'P01' already exists."
        )

        client = TestClient(app)
        response = client.post(
            "/projects/P01/outcome",
            json={
                "completion_status": "COMPLETED",
                "actual_completion_date": "2026-12-31",
                "final_progress": 100.0,
                "final_budget_used": 95.0,
            },
            headers=self.auth_headers,
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    @patch("app.api.projects.get_project_by_id")
    @patch("app.api.projects.get_project_outcome")
    def test_get_outcome_endpoint_success(
        self,
        mock_get_outcome,
        mock_get_project,
    ):
        """Test GET /projects/{id}/outcome success."""
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
        mock_get_outcome.return_value = {
            "project_id": "P01",
            "completion_status": "COMPLETED",
            "actual_completion_date": "2026-12-31",
            "planned_completion_date": "2026-10-31",
            "final_progress": 100.0,
            "final_delay_days": 61,
            "final_budget_used": 95.0,
            "final_budget_variance_percent": 5.5,
            "final_cost_crore": 126.6,
            "recorded_at": "2026-12-31T10:30:00+00:00",
            "recorded_by_uid": "test-user-123",
            "notes": "Completed",
        }

        client = TestClient(app)
        response = client.get("/projects/P01/outcome", headers=self.auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["project_id"] == "P01"
        assert data["outcome"]["completion_status"] == "COMPLETED"

    @patch("app.api.projects.get_project_by_id")
    @patch("app.api.projects.get_project_outcome")
    def test_get_outcome_endpoint_not_found(
        self,
        mock_get_outcome,
        mock_get_project,
    ):
        """Test GET /projects/{id}/outcome when not found."""
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
        mock_get_outcome.return_value = None

        client = TestClient(app)
        response = client.get("/projects/P01/outcome", headers=self.auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["project_id"] == "P01"
        assert data["outcome"] is None

    @patch("app.api.projects.get_project_by_id")
    def test_get_outcome_endpoint_project_not_found(
        self,
        mock_get_project,
    ):
        """Test GET /projects/{id}/outcome when project not found."""
        from fastapi.testclient import TestClient
        from app.main import app

        mock_get_project.return_value = None

        client = TestClient(app)
        response = client.get("/projects/P99/outcome", headers=self.auth_headers)
        assert response.status_code == 404


class TestDatasetReportWithOutcomes:
    """Tests for dataset report with outcomes."""

    def test_analyze_target_feasibility_with_outcomes(self):
        """Test feasibility analysis with completed projects."""
        from app.ml.dataset_report import analyze_target_feasibility
        
        # Create snapshots with one completed project
        snapshots = [
            {"project_id": "P01", "progress": 100.0, "snapshot_period": "2026-10"},  # Completed
            {"project_id": "P02", "progress": 50.0, "snapshot_period": "2026-10"},
            {"project_id": "P02", "progress": 70.0, "snapshot_period": "2026-11"},
        ]
        
        feasibility = analyze_target_feasibility(snapshots)
        
        # With completed project, delay/cost overrun prediction becomes feasible
        # (The current logic checks for progress >= 100 in any snapshot)
        assert feasibility["delay_prediction"]["current_observations"] >= 0
        assert feasibility["temporal_features"]["projects_with_2plus_snapshots"] == 1  # P02 has 2 snapshots


class TestOutcomeLeakagePrevention:
    """Tests to ensure outcome fields don't leak into features."""

    def test_outcome_fields_excluded_from_features(self):
        """Ensure outcome fields never appear in feature matrix."""
        from app.ml.feature_engineering import extract_safe_features
        
        snapshot = {
            "project_id": "P01",
            "snapshot_period": "2026-10",
            "progress": 100.0,
            "planned_progress": 100.0,
            "delay_days": 0,
            "budget_used": 100.0,
            "budget_total_crore": 120.0,
            "sector": "Roads",
            "location": "MP",
            "contractor": "Test",
            "completion_status": "COMPLETED",  # Should be excluded
            "actual_completion_date": "2026-12-31",  # Should be excluded
            "final_delay_days": 61,  # Should be excluded
            "final_budget_variance_percent": 5.5,  # Should be excluded
            "final_cost_crore": 126.6,  # Should be excluded
        }

        features = extract_safe_features(snapshot)

        # Leakage fields must NOT be in features
        assert "completion_status" not in features
        assert "actual_completion_date" not in features
        assert "final_delay_days" not in features
        assert "final_budget_variance_percent" not in features
        assert "final_cost_crore" not in features


class TestRiskEngineUnchanged:
    """Verify deterministic Risk Engine remains unchanged."""

    def test_risk_engine_import(self):
        from app.services.risk_engine import calculate_risk
        assert calculate_risk is not None

    def test_risk_engine_calculation(self):
        from app.services.risk_engine import calculate_risk
        from app.models.project import ProjectRecord

        project = ProjectRecord(
            project_id="P01",
            name="Test",
            location="MP",
            sector="Roads",
            progress=78.0,
            planned_progress=75.0,
            delay_days=0,
            budget_used=72.0,
            budget_total_crore=120.0,
            contractor="Test",
        )

        risk = calculate_risk(project)
        assert risk.overall_score == 10
        assert risk.overall_level == "LOW"
        assert risk.progress_risk == 0
        assert risk.delay_risk == 0
        assert risk.budget_risk == 40


if __name__ == "__main__":
    pytest.main([__file__, "-v"])