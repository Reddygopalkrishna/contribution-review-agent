# License and dependency checks

The deterministic audit now checks for a recognizable repository license and exact Python dependency pins in `requirements.txt`.

- R12 accepts MIT, Apache-2.0, BSD, MPL-2.0, and GPL license text at the repository root. Missing or unrecognized text is an error.
- R13 requires every parsed `requirements.txt` dependency to use `==version`. Direct URLs, ranges, and unversioned names are reported as unpinned.
- R11 still warns when a third-party Python import is not declared in `requirements.txt`.

## Optional OSV lookup

The default audit is offline. Add `--osv` to query the OSV package-version API for pinned PyPI dependencies:

```bash
python3 -m contrib_audit check /path/to/repo/sample-project --repo-root /path/to/repo --osv
```

OSV requests are made only with this flag and include a package name, the `PyPI` ecosystem, and the exact version. A network failure is informational; a returned vulnerability is R14. The implementation follows the official [OSV package-and-version query format](https://google.github.io/osv.dev/post-v1-query/).
