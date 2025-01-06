#!/bin/bash

# Get current version
CURRENT_TAG=$(git describe --tags --abbrev=0 2>/dev/null)

if [ -z "$CURRENT_TAG" ]; then
  echo "No existing tags found. Starting with v0.0.1"
  CURRENT_TAG="v0.0.1"
fi

# Parse version numbers
IFS='.' read -r -a VERSION <<< "${CURRENT_TAG#v}"
MAJOR=${VERSION[0]}
MINOR=${VERSION[1]}
PATCH=${VERSION[2]}

# Increment patch version
NEW_PATCH=$((PATCH + 1))
NEW_TAG="v${MAJOR}.${MINOR}.${NEW_PATCH}"

# Verify clean working directory
if ! git diff-index --quiet HEAD --; then
  echo "Error: Working directory is not clean. Commit or stash changes before tagging."
  exit 1
fi

# Create and push tag
echo "Creating new tag: ${NEW_TAG}"
git tag -a ${NEW_TAG} -m "Release ${NEW_TAG}"
git push origin ${NEW_TAG}

if [ $? -eq 0 ]; then
  echo "Successfully created and pushed tag ${NEW_TAG}"
else
  echo "Error: Failed to create or push tag"
  exit 1
fi
