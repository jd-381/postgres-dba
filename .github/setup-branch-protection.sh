#!/bin/bash
# Script to configure branch protection rules using GitHub CLI
# Requires: gh CLI (https://cli.github.com/)
# Usage: ./setup-branch-protection.sh

set -e

REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
BRANCH="main"

echo "Setting up branch protection for $REPO on branch $BRANCH..."

# Enable branch protection
gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  "/repos/$REPO/branches/$BRANCH/protection" \
  --input - <<EOF
{
  "required_status_checks": {
    "strict": true,
    "checks": [
      {"context": "Lint"},
      {"context": "Format Check"},
      {"context": "Test"},
      {"context": "Documentation"}
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": null,
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "block_creations": false,
  "required_conversation_resolution": false,
  "lock_branch": false,
  "allow_fork_syncing": false,
  "required_linear_history": false,
  "require_signed_commits": false
}
EOF

echo "✓ Branch protection configured successfully!"

# Enable automatic branch deletion on merge
echo ""
echo "Enabling automatic branch deletion on merge..."
gh api \
  --method PATCH \
  -H "Accept: application/vnd.github+json" \
  "/repos/$REPO" \
  -f delete_branch_on_merge=true

echo "✓ Automatic branch deletion enabled!"
echo ""
echo "Settings applied:"
echo "  - Require status checks to pass: Lint, Format Check, Test, Documentation"
echo "  - Enforce rules for administrators"
echo "  - Block force pushes and deletions"
echo "  - Automatically delete head branches on PR merge"
