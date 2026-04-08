from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
import zipfile


REPO_ROOT = Path(__file__).resolve().parents[2]
WORDPRESS_PLUGIN_DIR = REPO_ROOT / "wordpress-plugin"
DEFAULT_APPROVAL_UI_SOURCE_DIR = WORDPRESS_PLUGIN_DIR / "content-ops-approval-ui"
DEFAULT_APPROVAL_UI_PACKAGE_PATH = WORDPRESS_PLUGIN_DIR / "content-ops-approval-ui.zip"


@dataclass(frozen=True)
class PluginPackageResult:
    plugin_slug: str
    source_dir: Path
    output_path: Path
    file_count: int
    size_bytes: int
    sha256: str

    def to_dict(self) -> dict[str, object]:
        return {
            "plugin_slug": self.plugin_slug,
            "source_dir": str(self.source_dir),
            "output_path": str(self.output_path),
            "file_count": self.file_count,
            "size_bytes": self.size_bytes,
            "sha256": self.sha256,
        }


def build_wordpress_plugin_package(
    *,
    source_dir: Path = DEFAULT_APPROVAL_UI_SOURCE_DIR,
    output_path: Path = DEFAULT_APPROVAL_UI_PACKAGE_PATH,
) -> PluginPackageResult:
    active_source_dir = Path(source_dir).resolve()
    active_output_path = Path(output_path).resolve()

    if not active_source_dir.exists() or not active_source_dir.is_dir():
        raise ValueError(f"Plugin source directory does not exist: {active_source_dir}")
    if active_source_dir in active_output_path.parents:
        raise ValueError("Plugin package output_path must not be created inside the plugin source directory.")

    plugin_slug = active_source_dir.name
    plugin_bootstrap = active_source_dir / f"{plugin_slug}.php"
    if not plugin_bootstrap.exists():
        raise ValueError(
            f"Plugin source directory must contain bootstrap file '{plugin_slug}.php'."
        )

    plugin_files = sorted(path for path in active_source_dir.rglob("*") if path.is_file())
    if not plugin_files:
        raise ValueError(f"Plugin source directory does not contain any files: {active_source_dir}")

    active_output_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(active_output_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_path in plugin_files:
            archive_name = (Path(plugin_slug) / file_path.relative_to(active_source_dir)).as_posix()
            archive.write(file_path, arcname=archive_name)

    digest = hashlib.sha256(active_output_path.read_bytes()).hexdigest()
    return PluginPackageResult(
        plugin_slug=plugin_slug,
        source_dir=active_source_dir,
        output_path=active_output_path,
        file_count=len(plugin_files),
        size_bytes=active_output_path.stat().st_size,
        sha256=digest,
    )
