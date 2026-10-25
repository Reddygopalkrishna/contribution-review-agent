"""JSON configuration and built-in profiles for deterministic audit rules."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


class ConfigError(ValueError):
    """Raised when a supplied audit configuration is invalid."""


@dataclass(frozen=True)
class AuditConfig:
    profile: str
    allowed_parent_folders: tuple[str, ...]
    required_files: tuple[str, ...]
    manifest_files: tuple[str, ...]
    readme_heading_source: str | None
    generic_names: tuple[str, ...]
    scope_base_refs: tuple[str, ...]
    scope_allowed_extra_paths: tuple[str, ...]
    scope_max_extra_paths: int


_PROFILE_DIRECTORY = Path(__file__).with_name("profiles")


def get_profile(name: str) -> AuditConfig:
    try:
        return BUILTIN_PROFILES[name]
    except KeyError as error:
        raise ConfigError(f"Unknown profile {name!r}. Choose one of: {', '.join(BUILTIN_PROFILES)}.") from error


def _strings(data: dict[str, object], key: str) -> tuple[str, ...]:
    value = data.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ConfigError(f"{key} must be an array of strings.")
    return tuple(value)


def _parse(data: dict[str, object]) -> AuditConfig:
    scope = data.get("scope")
    if not isinstance(scope, dict):
        raise ConfigError("scope must be an object.")
    heading_source = data.get("readme_heading_source")
    if heading_source is not None and not isinstance(heading_source, str):
        raise ConfigError("readme_heading_source must be a string or null.")
    max_extra_paths = scope.get("max_extra_paths")
    if not isinstance(max_extra_paths, int) or isinstance(max_extra_paths, bool) or max_extra_paths < 0:
        raise ConfigError("scope.max_extra_paths must be a non-negative integer.")
    profile = data.get("profile", "custom")
    if not isinstance(profile, str):
        raise ConfigError("profile must be a string.")
    return AuditConfig(
        profile,
        _strings(data, "allowed_parent_folders"),
        _strings(data, "required_files"),
        _strings(data, "manifest_files"),
        heading_source,
        _strings(data, "generic_names"),
        _strings(scope, "base_refs"),
        _strings(scope, "allowed_extra_paths"),
        max_extra_paths,
    )


def _load_builtin_profiles() -> dict[str, AuditConfig]:
    profiles: dict[str, AuditConfig] = {}
    for path in _PROFILE_DIRECTORY.glob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ConfigError(f"Built-in profile {path} must contain an object.")
        config = _parse(data)
        profiles[config.profile] = config
    return profiles


BUILTIN_PROFILES = _load_builtin_profiles()


def load_config(source: str | None) -> AuditConfig:
    """Load a built-in profile name or a complete JSON configuration file."""
    if source is None:
        return get_profile("legacy-template")
    if source in BUILTIN_PROFILES:
        return get_profile(source)
    path = Path(source)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as error:
        raise ConfigError(f"Could not read configuration {path}: {error.strerror or error}.") from error
    except json.JSONDecodeError as error:
        raise ConfigError(f"Invalid JSON in {path}: {error.msg}.") from error
    if not isinstance(data, dict):
        raise ConfigError("The configuration root must be an object.")
    return _parse(data)


def starter_config(profile: str) -> str:
    config = get_profile(profile)
    return json.dumps({
        "profile": config.profile,
        "allowed_parent_folders": list(config.allowed_parent_folders),
        "required_files": list(config.required_files),
        "manifest_files": list(config.manifest_files),
        "readme_heading_source": config.readme_heading_source,
        "generic_names": list(config.generic_names),
        "scope": {
            "base_refs": list(config.scope_base_refs),
            "allowed_extra_paths": list(config.scope_allowed_extra_paths),
            "max_extra_paths": config.scope_max_extra_paths,
        },
    }, indent=2) + "\n"


def write_starter_config(path: Path, profile: str) -> None:
    if path.exists():
        raise ConfigError(f"Refusing to overwrite existing configuration: {path}.")
    path.write_text(starter_config(profile), encoding="utf-8")
