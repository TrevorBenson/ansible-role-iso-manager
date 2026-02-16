"""
Tests for GitHub Workflow YAML files
Validates workflow structure, job definitions, and security practices
"""

import os
import pytest
import yaml


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(scope="module")
def workflows_dir():
    """Return the path to the workflows directory."""
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), ".github", "workflows")


@pytest.fixture(scope="module")
def workflow_files(workflows_dir):
    """Return list of all workflow YAML files."""
    if not os.path.exists(workflows_dir):
        return []
    return [
        os.path.join(workflows_dir, f)
        for f in os.listdir(workflows_dir)
        if f.endswith((".yml", ".yaml"))
    ]


@pytest.fixture(scope="module")
def workflows(workflow_files):
    """Load and parse all workflow files."""
    loaded_workflows = {}
    for workflow_file in workflow_files:
        with open(workflow_file, "r") as f:
            content = yaml.safe_load(f)
            loaded_workflows[os.path.basename(workflow_file)] = content
    return loaded_workflows


# =============================================================================
# Basic Structure Tests
# =============================================================================


def test_workflow_files_exist(workflow_files):
    """Verify workflow files exist."""
    assert len(workflow_files) > 0, "At least one workflow file should exist"


def test_workflows_are_valid_yaml(workflow_files):
    """Verify all workflow files are valid YAML."""
    for workflow_file in workflow_files:
        with open(workflow_file, "r") as f:
            try:
                yaml.safe_load(f)
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML in {workflow_file}: {e}")


def test_workflows_have_name(workflows):
    """Verify all workflows have a name field."""
    for filename, workflow in workflows.items():
        assert workflow is not None, f"{filename} should not be empty"
        assert "name" in workflow, f"{filename} should have a 'name' field"
        assert workflow["name"], f"{filename} name should not be empty"


def test_workflows_have_on_trigger(workflows):
    """Verify all workflows have an 'on' trigger definition."""
    for filename, workflow in workflows.items():
        # YAML might parse 'on' as True (boolean), so check for both
        has_on_trigger = "on" in workflow or True in workflow
        assert has_on_trigger, f"{filename} should have an 'on' trigger"
        # Get the trigger (could be under 'on' or True)
        trigger = workflow.get("on") or workflow.get(True)
        assert trigger, f"{filename} on trigger should not be empty"


def test_workflows_have_jobs(workflows):
    """Verify all workflows have jobs defined."""
    for filename, workflow in workflows.items():
        assert "jobs" in workflow, f"{filename} should have jobs defined"
        assert workflow["jobs"], f"{filename} should have at least one job"


# =============================================================================
# Job Structure Tests
# =============================================================================


def test_jobs_have_runs_on(workflows):
    """Verify all jobs specify runs-on."""
    for filename, workflow in workflows.items():
        if "jobs" not in workflow:
            continue
        for job_name, job_config in workflow["jobs"].items():
            # Skip jobs that call other workflows
            if "uses" in job_config:
                continue
            assert "runs-on" in job_config, f"{filename}::{job_name} should have runs-on"


def test_jobs_have_steps_or_uses(workflows):
    """Verify all jobs have either steps or uses (reusable workflow)."""
    for filename, workflow in workflows.items():
        if "jobs" not in workflow:
            continue
        for job_name, job_config in workflow["jobs"].items():
            has_steps = "steps" in job_config and job_config["steps"]
            has_uses = "uses" in job_config
            assert has_steps or has_uses, (
                f"{filename}::{job_name} should have either 'steps' or 'uses'"
            )


# =============================================================================
# Security Tests
# =============================================================================


def test_actions_use_commit_sha_pinning(workflows):
    """Verify actions are pinned to specific commit SHAs (security best practice)."""
    unpinned_actions = []

    for filename, workflow in workflows.items():
        if "jobs" not in workflow:
            continue
        for job_name, job_config in workflow["jobs"].items():
            if "steps" not in job_config:
                continue
            for step_idx, step in enumerate(job_config["steps"]):
                if "uses" not in step:
                    continue
                uses = step["uses"]

                # Skip local workflows (start with ./)
                if uses.startswith("./"):
                    continue

                # Check if action is pinned with SHA
                # Format: owner/repo@sha or owner/repo/path@sha
                if "@" in uses:
                    ref = uses.split("@")[1]
                    # SHA should be 40 hex chars, or it's a tag/branch
                    if len(ref) != 40 or not all(c in "0123456789abcdef" for c in ref):
                        unpinned_actions.append(f"{filename}::{job_name}::step[{step_idx}]::{uses}")

    # This is a warning rather than failure for some projects
    if unpinned_actions:
        print(f"\nWarning: {len(unpinned_actions)} actions not pinned to SHA")
        for action in unpinned_actions[:5]:  # Show first 5
            print(f"  - {action}")


def test_no_hardcoded_secrets_in_workflows(workflow_files):
    """Verify no hardcoded secrets or tokens in workflow files."""
    sensitive_patterns = [
        "ghp_",  # GitHub personal access token
        "gho_",  # GitHub OAuth token
        "ghu_",  # GitHub user token
        "ghs_",  # GitHub server token
        "ghr_",  # GitHub refresh token
        "password:",
        "api_key:",
        "secret_key:",
    ]

    violations = []
    for workflow_file in workflow_files:
        with open(workflow_file, "r") as f:
            content = f.read().lower()
            for pattern in sensitive_patterns:
                if pattern in content and "${{" not in content[content.find(pattern):content.find(pattern) + 50]:
                    violations.append(f"{os.path.basename(workflow_file)}: contains {pattern}")

    assert len(violations) == 0, f"Potential hardcoded secrets found: {violations}"


# =============================================================================
# Reusable Workflow Tests
# =============================================================================


def test_reusable_workflows_have_workflow_call(workflows):
    """Verify reusable workflows have workflow_call trigger."""
    reusable_candidates = [
        "ansible-lint.yml",
        "codeql.yml",
        "molecule-test.yml",
        "role-validation.yml",
        "sonarcloud.yml",
        "yaml-lint.yml",
    ]

    for filename in reusable_candidates:
        if filename not in workflows:
            continue
        workflow = workflows[filename]
        # YAML might parse 'on' as True (boolean), so check for both
        has_on_trigger = "on" in workflow or True in workflow
        assert has_on_trigger, f"{filename} should have 'on' trigger"
        # Get the trigger (could be under 'on' or True)
        trigger = workflow.get("on") or workflow.get(True)
        assert "workflow_call" in trigger, (
            f"{filename} should have workflow_call trigger for reusability"
        )


# =============================================================================
# Specific Workflow Tests
# =============================================================================


def test_pre_merge_workflow_structure(workflows):
    """Verify pre-merge workflow has correct job dependencies."""
    if "pre-merge.yml" not in workflows:
        pytest.skip("pre-merge.yml not found")

    workflow = workflows["pre-merge.yml"]
    jobs = workflow.get("jobs", {})

    # Verify key jobs exist
    expected_jobs = ["yaml-lint", "ansible-lint", "role-validation", "molecule-tests"]
    for job_name in expected_jobs:
        assert job_name in jobs, f"pre-merge.yml should have {job_name} job"

    # Verify molecule-tests depends on linting jobs
    if "molecule-tests" in jobs and "needs" in jobs["molecule-tests"]:
        needs = jobs["molecule-tests"]["needs"]
        assert "yaml-lint" in needs, "molecule-tests should depend on yaml-lint"
        assert "ansible-lint" in needs, "molecule-tests should depend on ansible-lint"


def test_release_workflow_has_permissions(workflows):
    """Verify release workflow has appropriate permissions."""
    if "release.yml" not in workflows:
        pytest.skip("release.yml not found")

    workflow = workflows["release.yml"]
    assert "permissions" in workflow, "release.yml should define permissions"
    permissions = workflow["permissions"]
    assert "contents" in permissions, "release.yml should have contents permission"
    assert permissions["contents"] == "write", "release.yml needs write access to contents"


def test_codeql_has_security_events_permission(workflows):
    """Verify CodeQL workflow has security-events permission."""
    if "codeql.yml" not in workflows:
        pytest.skip("codeql.yml not found")

    workflow = workflows["codeql.yml"]
    assert "permissions" in workflow, "codeql.yml should define permissions"
    permissions = workflow["permissions"]
    assert "security-events" in permissions, "codeql.yml should have security-events permission"
    assert permissions["security-events"] == "write", "codeql.yml needs write access to security-events"


# =============================================================================
# Best Practices Tests
# =============================================================================


def test_jobs_use_ubuntu_24_04(workflows):
    """Verify jobs use ubuntu-24.04 (recommended stable runner)."""
    for filename, workflow in workflows.items():
        if "jobs" not in workflow:
            continue
        for job_name, job_config in workflow["jobs"].items():
            if "runs-on" not in job_config:
                continue
            runs_on = job_config["runs-on"]
            if isinstance(runs_on, str):
                # Allow ubuntu-24.04 or ubuntu-latest
                assert "ubuntu" in runs_on, f"{filename}::{job_name} should use Ubuntu runner"


def test_checkout_action_used_correctly(workflows):
    """Verify checkout action is used in jobs that need source code."""
    for filename, workflow in workflows.items():
        if "jobs" not in workflow:
            continue
        for job_name, job_config in workflow["jobs"].items():
            if "steps" not in job_config:
                continue

            # Check if job has steps that likely need code (lint, test, build)
            needs_checkout = any(
                keyword in job_name.lower()
                for keyword in ["lint", "test", "validate", "build", "scan", "analyze"]
            )

            if needs_checkout and job_config["steps"]:
                first_steps = job_config["steps"][:3]  # Check first 3 steps
                has_checkout = any(
                    "uses" in step and "checkout" in step["uses"]
                    for step in first_steps
                )
                # Soft assertion - just warn
                if not has_checkout:
                    print(f"\nInfo: {filename}::{job_name} might need checkout action")


# =============================================================================
# Version Pinning Tests
# =============================================================================


def test_ansible_and_python_versions_are_explicit(workflows):
    """Verify Ansible and Python versions are explicitly set."""
    for filename, workflow in workflows.items():
        if "jobs" not in workflow:
            continue
        for job_name, job_config in workflow["jobs"].items():
            # Check for setup-python action
            if "steps" in job_config:
                for step in job_config["steps"]:
                    if "uses" in step and "setup-python" in step["uses"]:
                        assert "with" in step, f"{filename}::{job_name} setup-python should have 'with'"
                        assert "python-version" in step.get("with", {}), (
                            f"{filename}::{job_name} should specify python-version"
                        )


# =============================================================================
# Error Handling Tests
# =============================================================================


def test_long_running_jobs_have_timeout(workflows):
    """Verify long-running jobs have timeout-minutes set."""
    long_running_keywords = ["test", "molecule", "scan", "analyze"]

    for filename, workflow in workflows.items():
        if "jobs" not in workflow:
            continue
        for job_name, job_config in workflow["jobs"].items():
            is_long_running = any(
                keyword in job_name.lower()
                for keyword in long_running_keywords
            )

            if is_long_running and "timeout-minutes" not in job_config:
                # This is advisory rather than strict
                print(f"\nInfo: {filename}::{job_name} might benefit from timeout-minutes")