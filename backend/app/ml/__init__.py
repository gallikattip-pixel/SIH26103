"""ML dataset foundation package for INFRAPLUS."""

from app.ml.data_loader import (
    load_all_snapshots_from_firebase,
    load_projects_from_firebase,
    get_snapshot_count_stats,
)
from app.ml.data_validator import (
    validate_snapshot,
    validate_snapshot_collection,
    detect_duplicate_snapshots,
    check_temporal_consistency,
    SnapshotValidationError,
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
    generate_dataset_audit,
    export_audit_report,
    print_audit_summary,
    assess_ml_readiness,
)

__all__ = [
    # Data loading
    "load_all_snapshots_from_firebase",
    "load_projects_from_firebase",
    "get_snapshot_count_stats",
    # Data validation
    "validate_snapshot",
    "validate_snapshot_collection",
    "detect_duplicate_snapshots",
    "check_temporal_consistency",
    "SnapshotValidationError",
    # Feature engineering
    "extract_safe_features",
    "extract_temporal_features",
    "encode_categorical_feature",
    "prepare_categorical_encodings",
    "apply_categorical_encoding",
    "build_feature_matrix",
    "get_feature_schema",
    # Dataset reporting
    "generate_dataset_audit",
    "export_audit_report",
    "print_audit_summary",
    "assess_ml_readiness",
]