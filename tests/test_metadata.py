"""
Tests for Ansible role metadata files
Validates meta/main.yml, defaults/main.yml, and vars/main.yml
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
def meta_main(project_root):
    """Load and parse meta/main.yml."""
    meta_path = os.path.join(project_root, "meta", "main.yml")
    if not os.path.exists(meta_path):
        pytest.skip("meta/main.yml not found")
    with open(meta_path, "r") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def defaults_main(project_root):
    """Load and parse defaults/main.yml."""
    defaults_path = os.path.join(project_root, "defaults", "main.yml")
    if not os.path.exists(defaults_path):
        pytest.skip("defaults/main.yml not found")
    with open(defaults_path, "r") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def vars_main(project_root):
    """Load and parse vars/main.yml."""
    vars_path = os.path.join(project_root, "vars", "main.yml")
    if not os.path.exists(vars_path):
        pytest.skip("vars/main.yml not found")
    with open(vars_path, "r") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def requirements_yml(project_root):
    """Load and parse meta/requirements.yml."""
    req_path = os.path.join(project_root, "meta", "requirements.yml")
    if not os.path.exists(req_path):
        return None
    with open(req_path, "r") as f:
        return yaml.safe_load(f)


# =============================================================================
# meta/main.yml Structure Tests
# =============================================================================


def test_meta_main_exists(project_root):
    """Verify meta/main.yml exists."""
    meta_path = os.path.join(project_root, "meta", "main.yml")
    assert os.path.exists(meta_path), "meta/main.yml should exist"


def test_meta_has_galaxy_info(meta_main):
    """Verify meta/main.yml has galaxy_info section."""
    assert meta_main is not None, "meta/main.yml should not be empty"
    assert "galaxy_info" in meta_main, "meta/main.yml should have galaxy_info"


def test_galaxy_info_has_required_fields(meta_main):
    """Verify galaxy_info has all required fields."""
    galaxy_info = meta_main.get("galaxy_info", {})

    required_fields = ["author", "description", "license", "min_ansible_version"]
    for field in required_fields:
        assert field in galaxy_info, f"galaxy_info should have {field}"
        assert galaxy_info[field], f"galaxy_info.{field} should not be empty"


def test_galaxy_info_role_name(meta_main):
    """Verify galaxy_info has role_name."""
    galaxy_info = meta_main.get("galaxy_info", {})
    assert "role_name" in galaxy_info, "galaxy_info should have role_name"
    assert galaxy_info["role_name"], "role_name should not be empty"


def test_galaxy_info_namespace(meta_main):
    """Verify galaxy_info has namespace."""
    galaxy_info = meta_main.get("galaxy_info", {})
    assert "namespace" in galaxy_info, "galaxy_info should have namespace"
    assert galaxy_info["namespace"], "namespace should not be empty"


def test_license_is_valid(meta_main):
    """Verify license is a recognized SPDX identifier."""
    galaxy_info = meta_main.get("galaxy_info", {})
    license_value = galaxy_info.get("license", "")

    # Common valid licenses
    valid_licenses = [
        "Apache-2.0", "MIT", "BSD-3-Clause", "BSD-2-Clause",
        "GPL-3.0-only", "GPL-2.0-only", "LGPL-3.0-only",
    ]

    assert license_value, "License should be specified"
    # Informational: check if it's a common license
    if license_value not in valid_licenses:
        print(f"\nInfo: License '{license_value}' - ensure it's a valid SPDX identifier")


def test_min_ansible_version_format(meta_main):
    """Verify min_ansible_version is properly formatted."""
    galaxy_info = meta_main.get("galaxy_info", {})
    min_version = galaxy_info.get("min_ansible_version", "")

    assert min_version, "min_ansible_version should be specified"
    # Should be a version number like "2.14" or "2.9.10"
    assert isinstance(min_version, (str, float)), "min_ansible_version should be string or float"


def test_platforms_are_defined(meta_main):
    """Verify platforms are defined in galaxy_info."""
    galaxy_info = meta_main.get("galaxy_info", {})

    if "platforms" in galaxy_info:
        platforms = galaxy_info["platforms"]
        assert isinstance(platforms, list), "platforms should be a list"
        assert len(platforms) > 0, "platforms should not be empty"

        for platform in platforms:
            assert "name" in platform, "Each platform should have a name"
            if "versions" in platform:
                assert isinstance(platform["versions"], list), "versions should be a list"


def test_galaxy_tags_are_defined(meta_main):
    """Verify galaxy_tags are defined."""
    galaxy_info = meta_main.get("galaxy_info", {})

    if "galaxy_tags" in galaxy_info:
        tags = galaxy_info["galaxy_tags"]
        assert isinstance(tags, list), "galaxy_tags should be a list"
        assert len(tags) > 0, "galaxy_tags should not be empty"

        for tag in tags:
            assert isinstance(tag, str), "Each tag should be a string"
            assert len(tag) <= 20, f"Tag '{tag}' exceeds 20 character limit"


def test_dependencies_are_defined(meta_main):
    """Verify dependencies are defined."""
    assert "dependencies" in meta_main, "meta/main.yml should have dependencies"
    dependencies = meta_main["dependencies"]
    assert isinstance(dependencies, list), "dependencies should be a list"
    # Can be empty, that's valid


# =============================================================================
# meta/requirements.yml Tests
# =============================================================================


def test_requirements_has_collections(requirements_yml):
    """Verify requirements.yml defines collections if it exists."""
    if requirements_yml is None:
        pytest.skip("meta/requirements.yml not found")

    assert "collections" in requirements_yml, "requirements.yml should have collections"
    collections = requirements_yml["collections"]
    assert isinstance(collections, list), "collections should be a list"


def test_collections_have_version(requirements_yml):
    """Verify collections specify version constraints."""
    if requirements_yml is None:
        pytest.skip("meta/requirements.yml not found")

    collections = requirements_yml.get("collections", [])
    for collection in collections:
        assert "name" in collection, "Each collection should have a name"
        # Version is optional but recommended
        if "version" not in collection:
            print(f"\nInfo: Collection {collection['name']} has no version constraint")


# =============================================================================
# defaults/main.yml Tests
# =============================================================================


def test_defaults_main_exists(project_root):
    """Verify defaults/main.yml exists."""
    defaults_path = os.path.join(project_root, "defaults", "main.yml")
    assert os.path.exists(defaults_path), "defaults/main.yml should exist"


def test_defaults_is_valid_yaml(defaults_main):
    """Verify defaults/main.yml is valid YAML."""
    assert defaults_main is not None, "defaults/main.yml should parse as valid YAML"


def test_defaults_variables_have_sensible_values(defaults_main):
    """Verify default variables have sensible values."""
    if defaults_main is None:
        pytest.skip("defaults/main.yml is empty")

    # Check for common anti-patterns
    for key, value in defaults_main.items():
        # Variables shouldn't be null/None unless explicitly intended
        if value is None:
            print(f"\nWarning: Variable '{key}' is set to null")

        # Paths shouldn't be empty strings
        if isinstance(value, str) and "path" in key.lower() and value == "":
            print(f"\nWarning: Path variable '{key}' is empty string")


def test_iso_manager_defaults_structure(defaults_main):
    """Verify ISO manager specific defaults are properly structured."""
    if defaults_main is None:
        pytest.skip("defaults/main.yml is empty")

    # Check for expected variables
    expected_vars = ["iso_storage_path", "iso_mount_root", "iso_mount_enabled"]
    for var in expected_vars:
        if var in defaults_main:
            value = defaults_main[var]

            if "path" in var:
                assert isinstance(value, str), f"{var} should be a string path"
                assert value.startswith("/"), f"{var} should be an absolute path"

            if var == "iso_mount_enabled":
                assert isinstance(value, bool), f"{var} should be a boolean"


# =============================================================================
# vars/main.yml Tests
# =============================================================================


def test_vars_main_exists(project_root):
    """Verify vars/main.yml exists."""
    vars_path = os.path.join(project_root, "vars", "main.yml")
    assert os.path.exists(vars_path), "vars/main.yml should exist"


def test_vars_is_valid_yaml(vars_main):
    """Verify vars/main.yml is valid YAML."""
    assert vars_main is not None, "vars/main.yml should parse as valid YAML"


def test_iso_catalog_structure(vars_main):
    """Verify ISO catalog is properly structured."""
    if vars_main is None or "iso_catalog" not in vars_main:
        pytest.skip("iso_catalog not found in vars/main.yml")

    catalog = vars_main["iso_catalog"]
    assert isinstance(catalog, dict), "iso_catalog should be a dictionary"
    assert len(catalog) > 0, "iso_catalog should not be empty"

    # Verify each catalog entry
    for key, value in catalog.items():
        assert isinstance(value, dict), f"Catalog entry '{key}' should be a dictionary"
        assert "url" in value, f"Catalog entry '{key}' should have a url"
        assert isinstance(value["url"], str), f"URL for '{key}' should be a string"
        assert value["url"].startswith(("http://", "https://")), (
            f"URL for '{key}' should be a valid HTTP(S) URL"
        )


def test_iso_catalog_urls_are_well_formed(vars_main):
    """Verify ISO catalog URLs are well-formed."""
    if vars_main is None or "iso_catalog" not in vars_main:
        pytest.skip("iso_catalog not found in vars/main.yml")

    catalog = vars_main["iso_catalog"]

    for key, value in catalog.items():
        url = value.get("url", "")

        # Check for common issues
        assert " " not in url, f"URL for '{key}' contains spaces"
        assert url.endswith((".iso", ".ISO")), f"URL for '{key}' should point to an ISO file"


def test_iso_catalog_naming_convention(vars_main):
    """Verify ISO catalog keys follow naming convention."""
    if vars_main is None or "iso_catalog" not in vars_main:
        pytest.skip("iso_catalog not found in vars/main.yml")

    catalog = vars_main["iso_catalog"]

    for key in catalog.keys():
        # Keys should be lowercase with hyphens or dots
        assert key == key.lower(), f"Catalog key '{key}' should be lowercase"
        assert " " not in key, f"Catalog key '{key}' should not contain spaces"
        # Should contain version number or identifier
        assert any(char.isdigit() for char in key), (
            f"Catalog key '{key}' should contain version number"
        )


# =============================================================================
# Cross-file Consistency Tests
# =============================================================================


def test_role_name_consistency(meta_main, project_root):
    """Verify role name is consistent with directory structure."""
    galaxy_info = meta_main.get("galaxy_info", {})
    role_name = galaxy_info.get("role_name", "")

    # Check if README mentions the role name
    readme_path = os.path.join(project_root, "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r") as f:
            readme_content = f.read()
            # Role name should be mentioned in README
            if role_name:
                assert role_name in readme_content or role_name.replace("_", " ") in readme_content, (
                    f"Role name '{role_name}' should be mentioned in README"
                )


def test_version_file_exists(project_root):
    """Verify VERSION file exists."""
    version_path = os.path.join(project_root, "VERSION")
    assert os.path.exists(version_path), "VERSION file should exist"

    with open(version_path, "r") as f:
        version = f.read().strip()
        assert version, "VERSION file should not be empty"
        # Should be semantic version format
        parts = version.split(".")
        assert len(parts) >= 2, "VERSION should be in semantic versioning format (e.g., 0.1.0)"


# =============================================================================
# Security and Best Practices Tests
# =============================================================================


def test_no_sensitive_data_in_defaults(defaults_main):
    """Verify no sensitive data in defaults."""
    if defaults_main is None:
        pytest.skip("defaults/main.yml is empty")

    sensitive_keywords = ["password", "secret", "token", "key", "credential"]

    for key, value in defaults_main.items():
        key_lower = key.lower()

        for keyword in sensitive_keywords:
            if keyword in key_lower:
                # If it's a sensitive variable, it should use vault or be empty
                assert value in [None, "", "{{ vault_", "{{ lookup("], (
                    f"Sensitive variable '{key}' should not have hardcoded value"
                )


def test_paths_are_not_world_writable(defaults_main):
    """Verify default paths don't suggest world-writable locations."""
    if defaults_main is None:
        pytest.skip("defaults/main.yml is empty")

    dangerous_paths = ["/tmp", "/var/tmp"]

    for key, value in defaults_main.items():
        if isinstance(value, str) and value.startswith("/"):
            for dangerous in dangerous_paths:
                assert not value.startswith(dangerous), (
                    f"Variable '{key}' should not use world-writable path '{value}'"
                )