# Rule configuration

The auditor loads `.contrib-audit.json` from the audited repository root. Pass `--config` only to override that discovery with a file path or built-in profile name.

Create a generic starter file without overwriting an existing one:

```bash
python3 -m contrib_audit init
```

## Schema

The file is JSON with this complete shape:

```json
{
  "profile": "custom-name",
  "allowed_parent_folders": ["contributions"],
  "required_files": ["README.md", ".gitignore"],
  "manifest_files": ["pyproject.toml", "requirements.txt"],
  "readme_heading_source": null,
  "generic_names": ["demo"],
  "scope": {
    "base_refs": ["origin/main"],
    "allowed_extra_paths": [],
    "max_extra_paths": 0
  }
}
```

- `allowed_parent_folders`: direct parent directory names allowed below the repository root. An empty list allows a project directly below the root.
- `required_files`: files required in every audited project.
- `manifest_files`: at least one of these dependency manifests must be present.
- `readme_heading_source`: a repository-relative Markdown file whose `##` headings are required in the project README; use `null` to avoid prescribed headings.
- `generic_names`: directory names rejected by R03.
- `scope.base_refs`: Git refs tried in order for R09.
- `scope.allowed_extra_paths`: changed paths permitted outside the audited project.
- `scope.max_extra_paths`: maximum number of permitted extra paths that may change.

Invalid JSON, wrong value types, missing fields, or an existing destination for `init` produce an error without changing the repository.

## Built-in profiles

- `generic` is the default when no configuration or legacy template is present. It requires a README, `.gitignore`, and one supported manifest, without mandated README headings.
- `legacy-template` is a compatibility profile for repositories with `template/README.md`. It is selected automatically when that template is present and can be selected explicitly with `--config legacy-template`.
