# Publishing to PyPI via GitHub Actions

Uses PyPI's **Trusted Publishers (OIDC)** — no API tokens required.

## Step 1 — Add a Trusted Publisher on PyPI

Go to: https://pypi.org/manage/account/publishing/

Under **"Add a new pending publisher"**, fill in:

| Field | Value |
|---|---|
| PyPI Project Name | `minit-cli` |
| Owner | `vamsi-ehc` |
| Repository name | `minit-cli` |
| Workflow filename | `publish.yml` |
| Environment name | `pypi` |

Click **Add**.

## Step 2 — Create a `pypi` GitHub Environment

Go to: https://github.com/vamsi-ehc/minit-cli → Settings → Environments → New environment

Name it exactly `pypi` and save. No secrets needed.

## Step 3 — Push the workflow and tag a release

```bash
git add .github/workflows/publish.yml
git commit -m "Add PyPI publish workflow"
git push origin main

# Tag the release to trigger publishing
git tag v0.1.0
git push origin v0.1.0
```

Pushing a `v*` tag triggers the workflow, builds the package, and publishes it to PyPI.

Once published, the package will be available at https://pypi.org/project/minit-cli/ and installable via:

```bash
pip install minit-cli
```
