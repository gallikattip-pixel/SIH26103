"""Tests for ML dataset foundation."""

import pytest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

from app.ml.data_validator import (
    validate_snapshot,
    validate_snapshot_collection,
    detect_duplicate_snapshots,
    check_temporal_consistency,
)
from app.ml.feature_engineering import (
    extract_safe_features,
    extract_temporal_features,
    encode_categorical_feature,
    prepare_categorical_encodings,
    apply_categorical_encoding,
    build_feature_matrix,
    get_feature_schema,
)
from app.ml.dataset_report import (
    analyze_field_completeness,
    analyze_categorical_distributions,
    analyze_numeric_distributions,
    analyze_target_feasibility,
    assess_ml_readiness,
)


class TestDataValidator:
    """Tests for snapshot data validation."""

    def test_validate_snapshot_valid(self):
        """Test validation passes for valid snapshot."""
        snapshot = {
            "project_id": "P01",
            "snapshot_period": "2026-10",
            "recorded_at": "2026-10-05T10:30:00+00:00",
            "progress": 78.0,
            "planned_progress": 75.0,
            "delay_days": 0,
            "budget_used": 72.0,
            "budget_total_crore": 120.0,
            "contractor": "Aarav Infra Ltd",
            "sector": "Roads",
            "location": "Madhya Pradesh",
        }
        is_valid, errors = validate_snapshot(snapshot)
        assert is_valid
        assert errors == []

    def test_validate_snapshot_missing_required(self):
        """Test validation fails for missing required fields."""
        snapshot = {
            "project_id": "P01",
            # Missing snapshot_period, recorded_at, etc.
        }
        is_valid, errors = validate_snapshot(snapshot)
        assert not is_valid
        assert len(errors) > 0
        assert any("Missing required field" in e for e in errors)

    def test_validate_snapshot_invalid_period(self):
        """Test validation fails for invalid period format."""
        snapshot = self._get_valid_snapshot()
        snapshot["snapshot_period"] = "2026/10"  # Invalid format
        is_valid, errors = validate_snapshot(snapshot)
        assert not is_valid
        assert any("Invalid snapshot_period" in e for e in errors)

    def test_validate_snapshot_invalid_progress(self):
        """Test validation fails for out-of-range progress."""
        snapshot = self._get_valid_snapshot()
        snapshot["progress"] = 150.0  # Out of range
        is_valid, errors = validate_snapshot(snapshot)
        assert not is_valid
        assert any("Progress out of range" in e for e in errors)

    def test_validate_snapshot_invalid_delay(self):
        """Test validation fails for negative delay."""
        snapshot = self._get_valid_snapshot()
        snapshot["delay_days"] = -5
        is_valid, errors = validate_snapshot(snapshot)
        assert not is_valid
        assert any("Delay days out of range" in e for e in errors)

    def test_validate_snapshot_invalid_budget(self):
        """Test validation fails for out-of-range budget."""
        snapshot = self._get_valid_snapshot()
        snapshot["budget_used"] = 150.0
        is_valid, errors = validate_snapshot(snapshot)
        assert not is_valid
        assert any("Budget used out of range" in e for e in errors)

    def test_validate_snapshot_invalid_recorded_at(self):
        """Test validation fails for invalid timestamp."""
        snapshot = self._get_valid_snapshot()
        snapshot["recorded_at"] = "not-a-timestamp"
        is_valid, errors = validate_snapshot(snapshot)
        assert not is_valid
        assert any("Invalid recorded_at" in e for e in errors)

    def test_validate_snapshot_empty_categorical(self):
        """Test validation fails for empty categorical fields."""
        snapshot = self._get_valid_snapshot()
        snapshot["sector"] = ""
        is_valid, errors = validate_snapshot(snapshot)
        assert not is_valid
        assert any("Invalid sector" in e for e in errors)

    def _get_valid_snapshot(self):
        return {
            "project_id": "P01",
            "snapshot_period": "2026-10",
            "recorded_at": "2026-10-05T10:30:00+00:00",
            "progress": 78.0,
            "planned_progress": 75.0,
            "delay_days": 0,
            "budget_used": 72.0,
            "budget_total_crore": 120.0,
            "contractor": "Aarav Infra Ltd",
            "sector": "Roads",
            "location": "Madhya Pradesh",
        }

    def test_validate_snapshot_collection(self):
        """Test collection validation separates valid/invalid."""
        valid = self._get_valid_snapshot()
        invalid = self._get_valid_snapshot()
        invalid["progress"] = 150.0

        valid_snaps, invalid_snaps = validate_snapshot_collection([valid, invalid])

        assert len(valid_snaps) == 1
        assert len(invalid_snaps) == 1
        assert invalid_snaps[0]["errors"]

    def test_detect_duplicate_snapshots(self):
        """Test duplicate detection."""
        snap1 = self._get_valid_snapshot()
        snap1["snapshot_period"] = "2026-10"
        snap2 = self._get_valid_snapshot()
        snap2["snapshot_period"] = "2026-10"  # Same period
        snap3 = self._get_valid_snapshot()
        snap3["snapshot_period"] = "2026-11"

        duplicates = detect_duplicate_snapshots([snap1, snap2, snap3])
        assert ("P01", "2026-10") in duplicates

    def test_check_temporal_consistency(self):
        """Test temporal consistency check."""
        snap1 = self._get_valid_snapshot()
        snap1["snapshot_period"] = "2026-10"
        snap1["recorded_at"] = "2026-10-05T10:30:00+00:00"

        snap2 = self._get_valid_snapshot()
        snap2["snapshot_period"] = "2026-09"  # Earlier period
        snap2["recorded_at"] = "2026-10-06T10:30:00+00:00"  # But later recorded_at

        warnings = check_temporal_consistency([snap1, snap2])
        assert len(warnings) > 0
        assert "goes backwards" in warnings[0]


class TestFeatureEngineering:
    """Tests for feature engineering."""

    def test_extract_safe_features(self):
        """Test extraction of leakage-safe features."""
        snapshot = {
            "project_id": "P01",
            "snapshot_period": "2026-10",
            "recorded_at": "2026-10-05T10:30:00+00:00",
            "progress": 78.0,
            "planned_progress": 75.0,
            "delay_days": 0,
            "budget_used": 72.0,
            "budget_total_crore": 120.0,
            "contractor": "Aarav Infra Ltd",
            "sector": "Roads",
            "location": "Madhya Pradesh",
            "risk_snapshot": {"overall_score": 10, "overall_level": "LOW"},  # Should be excluded
        }

        features = extract_safe_features(snapshot)

        # Check safe fields included
        assert features["progress"] == 78.0
        assert features["planned_progress"] == 75.0
        assert features["delay_days"] == 0
        assert features["budget_used"] == 72.0
        assert features["budget_total_crore"] == 120.0
        assert features["sector"] == "Roads"
        assert features["location"] == "Madhya Pradesh"
        assert features["contractor"] == "Aarav Infra Ltd"

        # Check derived safe features
        assert features["progress_gap"] == -3.0  # 75 - 78
        assert features["spend_ahead_of_work"] == 0.0  # max(0, 72-78)

        # Check leakage fields EXCLUDED
        assert "risk_snapshot" not in features
        assert "overall_score" not in features
        assert "overall_level" not in features

    def test_extract_temporal_features(self):
        """Test temporal feature extraction from sequential snapshots."""
        snapshots = [
            {
                "project_id": "P01",
                "snapshot_period": "2026-08",
                "progress": 40.0,
                "planned_progress": 50.0,
                "delay_days": 10,
                "budget_used": 45.0,
                "budget_total_crore": 120.0,
                "sector": "Roads",
                "location": "Madhya Pradesh",
                "contractor": "Test",
            },
            {
                "project_id": "P01",
                "snapshot_period": "2026-10",
                "progress": 55.0,
                "planned_progress": 60.0,
                "delay_days": 5,
                "budget_used": 55.0,
                "budget_total_crore": 120.0,
                "sector": "Roads",
                "location": "Madhya Pradesh",
                "contractor": "Test",
            },
        ]

        temporal = extract_temporal_features(snapshots, min_periods=2)

        assert "P01" in temporal
        enhanced = temporal["P01"]
        assert len(enhanced) == 2

        # First snapshot - no temporal features
        assert "progress_change" not in enhanced[0]

        # Second snapshot - has temporal features
        assert enhanced[1]["progress_change"] == 15.0  # 55 - 40
        assert enhanced[1]["planned_progress_change"] == 10.0  # 60 - 50
        assert enhanced[1]["delay_change"] == -5  # 5 - 10
        assert enhanced[1]["budget_used_change"] == 10.0  # 55 - 45
        # progress_gap_change requires progress_gap to be computed first
        # progress_gap = planned_progress - progress
        # snap1: 50-40=10, snap2: 60-55=5, change = 5-10 = -5
        assert "progress_gap_change" in enhanced[1]

    def test_encode_categorical_feature(self):
        """Test categorical label encoding."""
        values = ["Roads", "Health", "Roads", "Water", "Roads", "Education"]
        encoding = encode_categorical_feature(values, max_categories=10)

        assert "Roads" in encoding
        assert "Health" in encoding
        assert "Water" in encoding
        assert "Education" in encoding
        assert "OTHER" in encoding
        assert "UNKNOWN" in encoding
        assert encoding["Roads"] == 0  # Most common

    def test_prepare_categorical_encodings(self):
        """Test encoding preparation from snapshots."""
        snapshots = [
            {"sector": "Roads", "location": "MP", "contractor": "A"},
            {"sector": "Health", "location": "Bihar", "contractor": "B"},
            {"sector": "Roads", "location": "MP", "contractor": "A"},
        ]

        encodings = prepare_categorical_encodings(snapshots)

        assert "sector" in encodings
        assert "location" in encodings
        assert "contractor" in encodings
        assert encodings["sector"]["Roads"] == 0  # Most common

    def test_apply_categorical_encoding(self):
        """Test applying encodings to snapshots."""
        snapshots = [
            {"sector": "Roads", "location": "MP", "contractor": "A"},
            {"sector": "Health", "location": "Bihar", "contractor": "B"},
        ]
        encodings = prepare_categorical_encodings(snapshots)
        encoded = apply_categorical_encoding(snapshots, encodings)

        assert "sector_encoded" in encoded[0]
        assert "location_encoded" in encoded[0]
        assert "contractor_encoded" in encoded[0]
        assert encoded[0]["sector_encoded"] == 0  # Roads

    def test_build_feature_matrix_unsupervised(self):
        """Test building feature matrix without target."""
        snapshots = [
            {
                "project_id": "P01",
                "snapshot_period": "2026-10",
                "progress": 78.0,
                "planned_progress": 75.0,
                "delay_days": 0,
                "budget_used": 72.0,
                "budget_total_crore": 120.0,
                "sector": "Roads",
                "location": "MP",
                "contractor": "Test",
            }
        ]

        features, targets, feature_names = build_feature_matrix(snapshots)

        assert targets is None
        assert len(features) == 1
        assert len(feature_names) > 0
        assert "progress" in feature_names
        assert "sector_encoded" in feature_names

    def test_get_feature_schema(self):
        """Test feature schema documentation."""
        schema = get_feature_schema()

        assert "safe_raw_features" in schema
        assert "safe_derived_features" in schema
        assert "temporal_features" in schema
        assert "excluded_leakage_features" in schema
        assert "categorical_encodings" in schema

        # Verify leakage features are documented
        assert "risk_score / overall_score" in schema["excluded_leakage_features"]
        assert "progress_risk" in schema["excluded_leakage_features"]


class TestDatasetReport:
    """Tests for dataset audit reporting."""

    def test_analyze_field_completeness(self):
        """Test field completeness analysis."""
        snapshots = [
            {"progress": 50, "planned_progress": 60, "sector": "Roads"},
            {"progress": 70, "delay_days": 5, "sector": "Health"},
        ]
        completeness = analyze_field_completeness(snapshots)

        assert "progress" in completeness
        assert completeness["progress"]["present"] == 2
        assert completeness["progress"]["completeness_pct"] == 100.0
        assert completeness["delay_days"]["present"] == 1
        assert completeness["delay_days"]["completeness_pct"] == 50.0

    def test_analyze_categorical_distributions(self):
        """Test categorical distribution analysis."""
        snapshots = [
            {"sector": "Roads", "location": "MP"},
            {"sector": "Roads", "location": "Bihar"},
            {"sector": "Health", "location": "MP"},
        ]
        dist = analyze_categorical_distributions(snapshots)

        assert dist["sector"]["unique_count"] == 2
        assert dist["sector"]["top_categories"]["Roads"] == 2
        assert dist["location"]["unique_count"] == 2

    def test_analyze_numeric_distributions(self):
        """Test numeric distribution analysis."""
        snapshots = [
            {"progress": 50, "delay_days": 10},
            {"progress": 70, "delay_days": 20},
            {"progress": 90, "delay_days": 0},
        ]
        dist = analyze_numeric_distributions(snapshots)

        assert dist["progress"]["count"] == 3
        assert dist["progress"]["min"] == 50
        assert dist["progress"]["max"] == 90
        assert dist["progress"]["mean"] == 70.0

    def test_analyze_target_feasibility(self):
        """Test target feasibility analysis."""
        # No completed projects, no temporal data
        snapshots = [
            {"project_id": "P01", "progress": 50},
            {"project_id": "P02", "progress": 70},
        ]
        feasibility = analyze_target_feasibility(snapshots)

        assert not feasibility["delay_prediction"]["feasible"]
        assert not feasibility["cost_overrun_prediction"]["feasible"]
        assert not feasibility["risk_classification"]["feasible"]
        assert feasibility["temporal_features"]["projects_with_2plus_snapshots"] == 0

    def test_analyze_target_feasibility_with_temporal(self):
        """Test feasibility with temporal data but no outcomes."""
        snapshots = [
            {"project_id": "P01", "progress": 50, "snapshot_period": "2026-08"},
            {"project_id": "P01", "progress": 60, "snapshot_period": "2026-10"},
        ]
        feasibility = analyze_target_feasibility(snapshots)

        assert feasibility["temporal_features"]["feasible"]
        assert feasibility["temporal_features"]["projects_with_2plus_snapshots"] == 1

    def test_assess_ml_readiness_no_data(self):
        """Test ML readiness with no data."""
        stats = {"total_snapshots": 0, "projects_with_multiple_snapshots": 0}
        readiness = assess_ml_readiness(stats, [], {})

        assert readiness["status"] == "NO_DATA"
        assert "Implement monthly snapshot collection" in readiness["recommended_next_step"]

    def test_assess_ml_readiness_insufficient(self):
        """Test ML readiness with insufficient data."""
        stats = {"total_snapshots": 5, "projects_with_multiple_snapshots": 2}
        readiness = assess_ml_readiness(stats, [], {"delay_prediction": {"feasible": False}})

        assert readiness["status"] == "INSUFFICIENT_DATA"
        assert "50+ completed projects" in readiness["recommended_next_step"]


class TestLeakagePrevention:
    """Tests to ensure leakage-prone features are excluded."""

    def test_risk_snapshot_excluded_from_features(self):
        """Ensure risk_snapshot fields never appear in feature matrix."""
        snapshot = {
            "project_id": "P01",
            "snapshot_period": "2026-10",
            "progress": 78.0,
            "planned_progress": 75.0,
            "delay_days": 0,
            "budget_used": 72.0,
            "budget_total_crore": 120.0,
            "sector": "Roads",
            "location": "MP",
            "contractor": "Test",
            "risk_snapshot": {
                "overall_score": 50,
                "overall_level": "MEDIUM",
                "progress_risk": 20,
                "delay_risk": 30,
                "budget_risk": 40,
            },
        }

        features = extract_safe_features(snapshot)

        # Leakage fields must NOT be in features
        assert "risk_snapshot" not in features
        assert "overall_score" not in features
        assert "overall_level" not in features
        assert "progress_risk" not in features
        assert "delay_risk" not in features
        assert "budget_risk" not in features

    def test_feature_schema_excludes_leakage(self):
        """Verify schema documents excluded leakage features."""
        schema = get_feature_schema()

        leakage = schema["excluded_leakage_features"]
        assert "risk_score / overall_score" in leakage
        assert "risk_level / overall_level" in leakage
        assert "progress_risk" in leakage
        assert "delay_risk" in leakage
        assert "budget_risk" in leakage
        assert "final_delay_days (outcome)" in leakage


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