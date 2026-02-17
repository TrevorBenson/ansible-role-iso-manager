#!/bin/bash
# Publish Ansible role to Galaxy
set -euo pipefail

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Ansible Galaxy Publishing Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Validate inputs
if [ ! -f "VERSION" ]; then
    echo -e "${RED}ERROR: VERSION file not found${NC}"
    exit 1
fi

VERSION=$(cat VERSION)
echo -e "${GREEN}Version: ${VERSION}${NC}"

if [ -z "${GALAXY_API_KEY:-}" ]; then
    echo -e "${RED}ERROR: GALAXY_API_KEY environment variable not set${NC}"
    exit 1
fi

# Extract repository info from git (supports both HTTPS and SSH URLs)
REMOTE_URL=$(git config --get remote.origin.url)

if [ -z "$REMOTE_URL" ]; then
    echo -e "${RED}ERROR: Git remote URL not found${NC}"
    echo -e "${RED}Run: git remote add origin <repository-url>${NC}"
    exit 1
fi

REPO_OWNER=$(echo "$REMOTE_URL" | sed -n 's#.*[:/]\([^/]*\)/[^/]*$#\1#p')
REPO_NAME=$(echo "$REMOTE_URL" | sed -n 's#.*/\([^/]*\)$#\1#p' | sed 's/\.git$//')

echo -e "${BLUE}GitHub Repository: ${REPO_OWNER}/${REPO_NAME}${NC}"

# Extract Galaxy role name from meta/main.yml
if [ -f "meta/main.yml" ]; then
    GALAXY_ROLE_NAME=$(grep -A1 'galaxy_info:' meta/main.yml | grep 'role_name:' | sed 's/.*role_name: *\([^ ]*\).*/\1/' || true)
    if [ -n "$GALAXY_ROLE_NAME" ]; then
        echo -e "${BLUE}Galaxy Role Name: ${REPO_OWNER,,}/${GALAXY_ROLE_NAME}${NC}"
    fi
fi
echo ""

# Install ansible-core if not present
if ! command -v ansible-galaxy &> /dev/null; then
    echo -e "${YELLOW}Installing ansible-core...${NC}"
    pip install ansible-core
    echo -e "${GREEN}ansible-core installed${NC}"
    echo ""
fi

# Verify meta/main.yml exists
if [ ! -f "meta/main.yml" ]; then
    echo -e "${RED}ERROR: meta/main.yml not found${NC}"
    exit 1
fi

# Display role metadata
echo -e "${BLUE}Role Metadata:${NC}"
grep -E "^(galaxy_info:|  author:|  description:|  company:|  license:|  min_ansible_version:|  role_name:|  namespace:|version:)" meta/main.yml || true
echo ""

# Import/publish to Galaxy
echo -e "${BLUE}Publishing to Ansible Galaxy...${NC}"
echo ""

# Configure ansible-galaxy to use the API key via environment variable
# This prevents the secret from appearing in process listings (ps aux)
export ANSIBLE_GALAXY_SERVER_LIST="galaxy"
export ANSIBLE_GALAXY_SERVER_GALAXY_URL="https://galaxy.ansible.com/"
export ANSIBLE_GALAXY_SERVER_GALAXY_TOKEN="${GALAXY_API_KEY}"

# Use ansible-galaxy role import command
# Format: ansible-galaxy role import github_user github_repo
if ansible-galaxy role import \
    "${REPO_OWNER,,}" \
    "${REPO_NAME}"; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}✅ Successfully published to Galaxy!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "${BLUE}View on Galaxy:${NC}"
    if [ -n "${GALAXY_ROLE_NAME:-}" ]; then
        echo -e "${BLUE}https://galaxy.ansible.com/${REPO_OWNER,,}/${GALAXY_ROLE_NAME}${NC}"
    else
        echo -e "${BLUE}https://galaxy.ansible.com/${REPO_OWNER,,}/${REPO_NAME}${NC}"
    fi
    echo ""
else
    echo ""
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}❌ Failed to publish to Galaxy${NC}"
    echo -e "${RED}========================================${NC}"
    echo ""
    exit 1
fi
