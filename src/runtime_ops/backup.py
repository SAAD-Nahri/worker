from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import json
from pathlib import Path, PurePosixPath
import zipfile

from source_engine.runtime import RUNTIME_ARTIFACT_PATHS


REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = REPO_ROOT / "config"
BACKUPS_DIR = REPO_ROOT / "backups"
BACKUP_MANIFEST_NAME = "backup_manifest.json"
DEFAULT_RUNTIME_ARTIFACT_RELATIVE_PATHS = tuple(
    path.resolve().relative_to(REPO_ROOT.resolve()).as_posix() for path in RUNTIME_ARTIFACT_PATHS
)
EXPECTED_LOCAL_CONFIG_FILENAMES = (
    "wordpress_rest_config.local.json",
    "facebook_graph_config.local.json",
    "openai_provider_config.local.json",
    "operator_api.local.json",
)


@dataclass(frozen=True)
class RuntimeBackupPlan:
    repo_root: Path
    backup_root: Path
    bundle_path: Path
    created_at: str
    include_config: bool
    data_files: list[Path]
    missing_data_files: list[Path]
    config_files: list[Path]
    missing_config_files: list[Path]


@dataclass(frozen=True)
class RuntimeBackupResult:
    bundle_path: Path
    created_at: str
    include_config: bool
    written_members: tuple[str, ...]
    data_files: tuple[str, ...]
    missing_data_files: tuple[str, ...]
    config_files: tuple[str, ...]
    missing_config_files: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "backup_path": str(self.bundle_path),
            "created_at": self.created_at,
            "include_config": self.include_config,
            "written_members": list(self.written_members),
            "data_files": list(self.data_files),
            "missing_data_files": list(self.missing_data_files),
            "config_files": list(self.config_files),
            "missing_config_files": list(self.missing_config_files),
            "data_file_count": len(self.data_files),
            "config_file_count": len(self.config_files),
        }


@dataclass(frozen=True)
class RuntimeRestoreAction:
    archive_member: str
    target_path: Path
    file_group: str
    will_overwrite: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "archive_member": self.archive_member,
            "target_path": str(self.target_path),
            "file_group": self.file_group,
            "will_overwrite": self.will_overwrite,
        }


def build_runtime_backup_plan(
    *,
    backup_root: Path | None = None,
    artifact_paths: list[Path] | tuple[Path, ...] | None = None,
    include_config: bool = False,
    config_paths: list[Path] | tuple[Path, ...] | None = None,
    repo_root: Path | None = None,
) -> RuntimeBackupPlan:
    active_repo_root = (repo_root or REPO_ROOT).resolve()
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    active_backup_root = (backup_root or BACKUPS_DIR).resolve()
    data_candidates = list(artifact_paths or _default_artifact_paths(active_repo_root))
    config_candidates = list(config_paths or _default_config_paths(active_repo_root / "config"))

    data_files, missing_data_files = _partition_existing_paths(data_candidates)
    if include_config:
        config_files, missing_config_files = _partition_existing_paths(config_candidates)
    else:
        config_files, missing_config_files = [], []

    bundle_path = active_backup_root / f"runtime_backup_{timestamp}.zip"
    return RuntimeBackupPlan(
        repo_root=active_repo_root,
        backup_root=active_backup_root,
        bundle_path=bundle_path,
        created_at=datetime.now(UTC).isoformat(),
        include_config=include_config,
        data_files=data_files,
        missing_data_files=missing_data_files,
        config_files=config_files,
        missing_config_files=missing_config_files,
    )


def create_runtime_backup(plan: RuntimeBackupPlan) -> RuntimeBackupResult:
    plan.backup_root.mkdir(parents=True, exist_ok=True)
    manifest = _build_manifest(plan)
    written_members: list[str] = []
    with zipfile.ZipFile(plan.bundle_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for source_path in [*plan.data_files, *plan.config_files]:
            relative_path = _relative_repo_path(source_path, plan.repo_root)
            archive.write(source_path, arcname=relative_path.as_posix())
            written_members.append(relative_path.as_posix())
        archive.writestr(BACKUP_MANIFEST_NAME, json.dumps(manifest, indent=2, sort_keys=True))
        written_members.append(BACKUP_MANIFEST_NAME)
    return RuntimeBackupResult(
        bundle_path=plan.bundle_path,
        created_at=plan.created_at,
        include_config=plan.include_config,
        written_members=tuple(written_members),
        data_files=tuple(_stringify_repo_paths(plan.data_files, plan.repo_root)),
        missing_data_files=tuple(_stringify_repo_paths(plan.missing_data_files, plan.repo_root)),
        config_files=tuple(_stringify_repo_paths(plan.config_files, plan.repo_root)),
        missing_config_files=tuple(_stringify_repo_paths(plan.missing_config_files, plan.repo_root)),
    )


def read_runtime_backup_manifest(bundle_path: Path) -> dict[str, object]:
    active_bundle_path = bundle_path.resolve()
    if not active_bundle_path.exists():
        raise ValueError(f"Runtime backup bundle does not exist: {bundle_path}")
    with zipfile.ZipFile(active_bundle_path, "r") as archive:
        try:
            payload = json.loads(archive.read(BACKUP_MANIFEST_NAME).decode("utf-8"))
        except KeyError as exc:
            raise ValueError("Runtime backup bundle is missing backup_manifest.json.") from exc
    if not isinstance(payload, dict):
        raise ValueError("Runtime backup manifest root must be a JSON object.")
    return payload


def build_runtime_restore_actions(
    bundle_path: Path,
    *,
    target_root: Path | None = None,
    restore_data: bool = True,
    restore_config: bool = False,
    allow_overwrite: bool = False,
) -> list[RuntimeRestoreAction]:
    if not restore_data and not restore_config:
        raise ValueError("Runtime restore must include data and/or config paths.")

    active_bundle_path = bundle_path.resolve()
    if not active_bundle_path.exists():
        raise ValueError(f"Runtime backup bundle does not exist: {bundle_path}")

    active_target_root = (target_root or REPO_ROOT).resolve()
    actions: list[RuntimeRestoreAction] = []
    with zipfile.ZipFile(active_bundle_path, "r") as archive:
        for member_name in archive.namelist():
            if member_name == BACKUP_MANIFEST_NAME or member_name.endswith("/"):
                continue
            file_group = _member_group(member_name)
            if file_group == "data" and not restore_data:
                continue
            if file_group == "config" and not restore_config:
                continue
            target_path = _build_restore_target_path(active_target_root, member_name)
            will_overwrite = target_path.exists()
            if will_overwrite and not allow_overwrite:
                raise ValueError(f"Restore target already exists: {target_path}")
            actions.append(
                RuntimeRestoreAction(
                    archive_member=member_name,
                    target_path=target_path,
                    file_group=file_group,
                    will_overwrite=will_overwrite,
                )
            )
    return actions


def restore_runtime_backup(
    bundle_path: Path,
    *,
    target_root: Path | None = None,
    restore_data: bool = True,
    restore_config: bool = False,
    allow_overwrite: bool = False,
    dry_run: bool = False,
) -> list[RuntimeRestoreAction]:
    actions = build_runtime_restore_actions(
        bundle_path,
        target_root=target_root,
        restore_data=restore_data,
        restore_config=restore_config,
        allow_overwrite=allow_overwrite,
    )
    if dry_run:
        return actions

    with zipfile.ZipFile(bundle_path.resolve(), "r") as archive:
        for action in actions:
            action.target_path.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(action.archive_member, "r") as source_handle:
                action.target_path.write_bytes(source_handle.read())
    return actions


def _build_manifest(plan: RuntimeBackupPlan) -> dict[str, object]:
    return {
        "version": 1,
        "created_at": plan.created_at,
        "include_config": plan.include_config,
        "backup_filename": plan.bundle_path.name,
        "data_files": _stringify_repo_paths(plan.data_files, plan.repo_root),
        "missing_data_files": _stringify_repo_paths(plan.missing_data_files, plan.repo_root),
        "config_files": _stringify_repo_paths(plan.config_files, plan.repo_root),
        "missing_config_files": _stringify_repo_paths(plan.missing_config_files, plan.repo_root),
    }


def _default_config_paths(config_dir: Path) -> list[Path]:
    return [config_dir / filename for filename in EXPECTED_LOCAL_CONFIG_FILENAMES]


def _default_artifact_paths(repo_root: Path) -> list[Path]:
    return [repo_root / relative_path for relative_path in DEFAULT_RUNTIME_ARTIFACT_RELATIVE_PATHS]


def _partition_existing_paths(paths: list[Path] | tuple[Path, ...]) -> tuple[list[Path], list[Path]]:
    existing: list[Path] = []
    missing: list[Path] = []
    for path in paths:
        if path.exists():
            existing.append(path.resolve())
        else:
            missing.append(path.resolve())
    return existing, missing


def _relative_repo_path(path: Path, repo_root: Path) -> Path:
    resolved_path = path.resolve()
    resolved_root = repo_root.resolve()
    if resolved_root not in (resolved_path, *resolved_path.parents):
        raise ValueError(f"Backup path is outside the repo root: {path}")
    return resolved_path.relative_to(resolved_root)


def _stringify_repo_paths(paths: list[Path], repo_root: Path) -> list[str]:
    values: list[str] = []
    for path in paths:
        try:
            values.append(_relative_repo_path(path, repo_root).as_posix())
        except ValueError:
            values.append(str(path))
    return values


def _member_group(member_name: str) -> str:
    pure_path = PurePosixPath(member_name)
    if pure_path.parts[:1] == ("data",):
        return "data"
    if pure_path.parts[:1] == ("config",):
        return "config"
    raise ValueError(f"Unsupported restore member outside data/ or config/: {member_name}")


def _build_restore_target_path(target_root: Path, member_name: str) -> Path:
    pure_path = PurePosixPath(member_name)
    if pure_path.is_absolute() or ".." in pure_path.parts:
        raise ValueError(f"Unsafe backup member path: {member_name}")
    file_group = _member_group(member_name)
    target_path = (target_root / Path(*pure_path.parts)).resolve()
    allowed_root = (target_root / file_group).resolve()
    if allowed_root not in (target_path, *target_path.parents):
        raise ValueError(f"Restore target escaped the allowed directory: {member_name}")
    return target_path
