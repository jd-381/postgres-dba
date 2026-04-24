# GitHub Configuration

This directory contains GitHub-specific configuration for workflows and branch protection.

## CI/CD Workflow

The [ci.yml](workflows/ci.yml) workflow runs four quality checks on every push and pull request to `main`:

- ✅ **Lint** - Code quality checks with Ruff
- ✅ **Format Check** - Ensures code is properly formatted
- ✅ **Test** - Runs the test suite with pytest
- ✅ **Documentation** - Verifies `USAGE.md` is up to date

**Triggers:**
- Push to `main` branch
- Pull requests to `main` branch

**Protection:** All checks must pass before code can be merged, preventing unformatted code, failing tests, outdated documentation, and code quality issues. Even changes made via GitHub's web editor must pass these checks through a pull request.

## Branch Protection (Optional)

Branch protection is recommended but not required. If not configured, pre-commit hooks will still enforce quality checks locally.

### Quick Setup

**Prerequisites:** [GitHub CLI](https://cli.github.com) (`gh`)

```bash
make github
```

This runs [setup-branch-protection.sh](setup-branch-protection.sh), a one-time script that configures the following rules for `main`:

- ✅ Require all CI checks to pass (lint, format, test, docs)
- ✅ Block force pushes and branch deletion
- ✅ Enable automatic branch deletion after merge

### Alternative Options

You can also:
- Configure branch protection manually in GitHub Settings → Branches
- Add it to your Infrastructure as Code setup
