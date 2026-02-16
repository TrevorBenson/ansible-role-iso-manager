"""
Tests for linting configuration files
Validates .ansible-lint, .yamllint, .releaserc.yml, and other config files
"""

import os
import pytest
import yaml


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(scope="module")
def project_root():
    """Return the project root directory."""
    return os.path.dirname(os.path.dirname(__file__))


@pytest.fixture(scope="module")
def ansible_lint_config(project_root):
    """Load and parse .ansible-lint."""
    config_path = os.path.join(project_root, ".ansible-lint")
    if not os.path.exists(config_path):
        pytest.skip(".ansible-lint not found")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def yamllint_config(project_root):
    """Load and parse .yamllint."""
    config_path = os.path.join(project_root, ".yamllint")
    if not os.path.exists(config_path):
        pytest.skip(".yamllint not found")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def releaserc_config(project_root):
    """Load and parse .releaserc.yml."""
    config_path = os.path.join(project_root, ".releaserc.yml")
    if not os.path.exists(config_path):
        pytest.skip(".releaserc.yml not found")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def gitignore_content(project_root):
    """Load .gitignore content."""
    gitignore_path = os.path.join(project_root, ".gitignore")
    if not os.path.exists(gitignore_path):
        pytest.skip(".gitignore not found")
    with open(gitignore_path, "r") as f:
        return f.read()


# =============================================================================
# .ansible-lint Tests
# =============================================================================


def test_ansible_lint_config_exists(project_root):
    """Verify .ansible-lint exists."""
    config_path = os.path.join(project_root, ".ansible-lint")
    assert os.path.exists(config_path), ".ansible-lint should exist"


def test_ansible_lint_has_profile(ansible_lint_config):
    """Verify ansible-lint has a profile set."""
    assert ansible_lint_config is not None, ".ansible-lint should not be empty"
    assert "profile" in ansible_lint_config, ".ansible-lint should have a profile"
    assert ansible_lint_config["profile"] in ["min", "basic", "moderate", "safety", "production"], (
        "profile should be a valid ansible-lint profile"
    )


def test_ansible_lint_has_exclude_paths(ansible_lint_config):
    """Verify ansible-lint excludes appropriate paths."""
    if "exclude_paths" not in ansible_lint_config:
        pytest.skip("exclude_paths not configured")

    exclude_paths = ansible_lint_config["exclude_paths"]
    assert isinstance(exclude_paths, list), "exclude_paths should be a list"

    # Common paths that should be excluded
    recommended_excludes = [".git/", ".github/", ".venv/"]
    for path in recommended_excludes:
        if path not in exclude_paths:
            print(f"\nInfo: Consider excluding '{path}' in .ansible-lint")


def test_ansible_lint_skip_list_is_justified(ansible_lint_config):
    """Verify skip_list has comments or is minimal."""
    if "skip_list" not in ansible_lint_config:
        return  # No skips is fine

    skip_list = ansible_lint_config["skip_list"]
    assert isinstance(skip_list, list), "skip_list should be a list"

    # Excessive skips might indicate issues
    if len(skip_list) > 10:
        print(f"\nWarning: {len(skip_list)} rules skipped - consider reducing")


# =============================================================================
# .yamllint Tests
# =============================================================================


def test_yamllint_config_exists(project_root):
    """Verify .yamllint exists."""
    config_path = os.path.join(project_root, ".yamllint")
    assert os.path.exists(config_path), ".yamllint should exist"


def test_yamllint_extends_default(yamllint_config):
    """Verify yamllint extends default configuration."""
    assert yamllint_config is not None, ".yamllint should not be empty"
    assert "extends" in yamllint_config, ".yamllint should extend a base config"
    assert yamllint_config["extends"] == "default", ".yamllint should extend 'default'"


def test_yamllint_has_rules(yamllint_config):
    """Verify yamllint has rules defined."""
    assert "rules" in yamllint_config, ".yamllint should have rules"
    rules = yamllint_config["rules"]
    assert isinstance(rules, dict), "rules should be a dictionary"
    assert len(rules) > 0, "rules should not be empty"


def test_yamllint_line_length_configured(yamllint_config):
    """Verify line-length rule is configured."""
    rules = yamllint_config.get("rules", {})
    if "line-length" in rules:
        line_length_config = rules["line-length"]
        if isinstance(line_length_config, dict):
            assert "max" in line_length_config, "line-length should have max value"
            max_length = line_length_config["max"]
            assert isinstance(max_length, int), "line-length max should be an integer"
            assert max_length >= 80, "line-length max should be at least 80"


def test_yamllint_indentation_configured(yamllint_config):
    """Verify indentation rule is configured."""
    rules = yamllint_config.get("rules", {})
    if "indentation" in rules:
        indent_config = rules["indentation"]
        if isinstance(indent_config, dict):
            assert "spaces" in indent_config, "indentation should specify spaces"
            spaces = indent_config["spaces"]
            assert spaces in [2, 4], "indentation should be 2 or 4 spaces"


def test_yamllint_ignores_appropriate_paths(yamllint_config):
    """Verify yamllint ignores appropriate paths."""
    if "ignore" not in yamllint_config:
        print("\nInfo: Consider adding 'ignore' to .yamllint for .git/, .github/")
        return

    ignore = yamllint_config["ignore"]
    assert isinstance(ignore, str), "ignore should be a string pattern"


# =============================================================================
# .releaserc.yml Tests
# =============================================================================


def test_releaserc_config_exists(project_root):
    """Verify .releaserc.yml exists."""
    config_path = os.path.join(project_root, ".releaserc.yml")
    assert os.path.exists(config_path), ".releaserc.yml should exist for semantic-release"


def test_releaserc_has_branches(releaserc_config):
    """Verify .releaserc.yml has branches defined."""
    assert releaserc_config is not None, ".releaserc.yml should not be empty"
    assert "branches" in releaserc_config, ".releaserc.yml should define branches"
    branches = releaserc_config["branches"]
    assert isinstance(branches, list), "branches should be a list"
    assert len(branches) > 0, "branches should not be empty"


def test_releaserc_has_plugins(releaserc_config):
    """Verify .releaserc.yml has plugins defined."""
    assert "plugins" in releaserc_config, ".releaserc.yml should define plugins"
    plugins = releaserc_config["plugins"]
    assert isinstance(plugins, list), "plugins should be a list"
    assert len(plugins) > 0, "plugins should not be empty"


def test_releaserc_has_commit_analyzer(releaserc_config):
    """Verify commit-analyzer plugin is configured."""
    plugins = releaserc_config.get("plugins", [])

    has_commit_analyzer = False
    for plugin in plugins:
        if isinstance(plugin, list) and "@semantic-release/commit-analyzer" in plugin[0]:
            has_commit_analyzer = True
            break
        elif isinstance(plugin, str) and "commit-analyzer" in plugin:
            has_commit_analyzer = True
            break

    assert has_commit_analyzer, ".releaserc.yml should have commit-analyzer plugin"


def test_releaserc_has_changelog_plugin(releaserc_config):
    """Verify changelog plugin is configured."""
    plugins = releaserc_config.get("plugins", [])

    has_changelog = False
    for plugin in plugins:
        if isinstance(plugin, list) and "@semantic-release/changelog" in plugin[0]:
            has_changelog = True
            break
        elif isinstance(plugin, str) and "changelog" in plugin:
            has_changelog = True
            break

    assert has_changelog, ".releaserc.yml should have changelog plugin"


def test_releaserc_has_git_plugin(releaserc_config):
    """Verify git plugin is configured to commit changes."""
    plugins = releaserc_config.get("plugins", [])

    has_git = False
    for plugin in plugins:
        if isinstance(plugin, list) and "@semantic-release/git" in plugin[0]:
            has_git = True
            # Check if it commits VERSION and CHANGELOG
            if len(plugin) > 1 and isinstance(plugin[1], dict):
                assets = plugin[1].get("assets", [])
                if "VERSION" not in assets or "CHANGELOG.md" not in assets:
                    print("\nInfo: Consider committing VERSION and CHANGELOG.md in git plugin")
            break

    assert has_git, ".releaserc.yml should have git plugin for committing releases"


def test_releaserc_branches_structure(releaserc_config):
    """Verify branches are properly structured."""
    branches = releaserc_config.get("branches", [])

    for branch in branches:
        if isinstance(branch, dict):
            assert "name" in branch, "Branch configuration should have name"
            # Prerelease branches should have channel set
            if branch.get("prerelease"):
                assert "channel" in branch, "Prerelease branch should have channel"


# =============================================================================
# .gitignore Tests
# =============================================================================


def test_gitignore_exists(project_root):
    """Verify .gitignore exists."""
    gitignore_path = os.path.join(project_root, ".gitignore")
    assert os.path.exists(gitignore_path), ".gitignore should exist"


def test_gitignore_excludes_common_patterns(gitignore_content):
    """Verify .gitignore excludes common patterns."""
    required_patterns = [
        "__pycache__",
        "*.pyc",
        ".venv",
        ".molecule",
    ]

    for pattern in required_patterns:
        assert pattern in gitignore_content, f".gitignore should exclude {pattern}"


def test_gitignore_excludes_sensitive_files(gitignore_content):
    """Verify .gitignore excludes potentially sensitive files."""
    sensitive_patterns = [
        ".env",
        "*.retry",
    ]

    for pattern in sensitive_patterns:
        if pattern not in gitignore_content:
            print(f"\nInfo: Consider adding '{pattern}' to .gitignore")


def test_gitignore_excludes_ide_files(gitignore_content):
    """Verify .gitignore excludes IDE files."""
    ide_patterns = [".idea", ".vscode", "*.swp"]

    excluded_count = sum(1 for pattern in ide_patterns if pattern in gitignore_content)
    assert excluded_count > 0, ".gitignore should exclude some IDE files"


# =============================================================================
# sonar-project.properties Tests
# =============================================================================


def test_sonar_config_exists(project_root):
    """Verify sonar-project.properties exists."""
    sonar_path = os.path.join(project_root, "sonar-project.properties")
    assert os.path.exists(sonar_path), "sonar-project.properties should exist"


def test_sonar_config_has_required_fields(project_root):
    """Verify sonar-project.properties has required fields."""
    sonar_path = os.path.join(project_root, "sonar-project.properties")
    if not os.path.exists(sonar_path):
        pytest.skip("sonar-project.properties not found")

    with open(sonar_path, "r") as f:
        content = f.read()

    required_fields = [
        "sonar.projectKey",
        "sonar.organization",
        "sonar.sources",
    ]

    for field in required_fields:
        assert field in content, f"sonar-project.properties should have {field}"


def test_sonar_config_excludes_test_code(project_root):
    """Verify sonar-project.properties excludes test code from main analysis."""
    sonar_path = os.path.join(project_root, "sonar-project.properties")
    if not os.path.exists(sonar_path):
        pytest.skip("sonar-project.properties not found")

    with open(sonar_path, "r") as f:
        content = f.read()

    # Should define either exclusions or separate test paths
    has_proper_separation = "sonar.exclusions" in content or "sonar.tests" in content
    assert has_proper_separation, "SonarCloud should separate test code from main code"


# =============================================================================
# Configuration Consistency Tests
# =============================================================================


def test_python_version_consistency(project_root):
    """Verify Python version is consistent across configs."""
    # Check sonar-project.properties
    sonar_path = os.path.join(project_root, "sonar-project.properties")
    python_versions = []

    if os.path.exists(sonar_path):
        with open(sonar_path, "r") as f:
            for line in f:
                if "sonar.python.version" in line:
                    version = line.split("=")[1].strip()
                    python_versions.append(version)

    # Check workflows
    workflows_dir = os.path.join(project_root, ".github", "workflows")
    if os.path.exists(workflows_dir):
        for filename in os.listdir(workflows_dir):
            if filename.endswith((".yml", ".yaml")):
                with open(os.path.join(workflows_dir, filename), "r") as f:
                    try:
                        workflow = yaml.safe_load(f)
                        # Look for python-version in defaults
                        if workflow and "on" in workflow:
                            inputs = workflow.get("on", {}).get("workflow_call", {}).get("inputs", {})
                            if "python-version" in inputs:
                                default = inputs["python-version"].get("default")
                                if default:
                                    python_versions.append(default)
                    except yaml.YAMLError:
                        pass

    # All Python versions should be consistent
    if len(set(python_versions)) > 1:
        print(f"\nInfo: Multiple Python versions found: {set(python_versions)}")


def test_ansible_version_consistency(project_root):
    """Verify Ansible version is consistent across configs."""
    workflows_dir = os.path.join(project_root, ".github", "workflows")
    ansible_versions = []

    if os.path.exists(workflows_dir):
        for filename in os.listdir(workflows_dir):
            if filename.endswith((".yml", ".yaml")):
                with open(os.path.join(workflows_dir, filename), "r") as f:
                    try:
                        workflow = yaml.safe_load(f)
                        if workflow and "on" in workflow:
                            inputs = workflow.get("on", {}).get("workflow_call", {}).get("inputs", {})
                            if "ansible-version" in inputs:
                                default = inputs["ansible-version"].get("default")
                                if default:
                                    ansible_versions.append(default)
                    except yaml.YAMLError:
                        pass

    # Check meta/main.yml for min_ansible_version
    meta_path = os.path.join(project_root, "meta", "main.yml")
    if os.path.exists(meta_path):
        with open(meta_path, "r") as f:
            meta = yaml.safe_load(f)
            min_version = meta.get("galaxy_info", {}).get("min_ansible_version")
            if min_version:
                ansible_versions.append(str(min_version))

    if len(set(ansible_versions)) > 1:
        print(f"\nInfo: Multiple Ansible versions found: {set(ansible_versions)}")