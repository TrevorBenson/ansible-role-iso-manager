"""
Testinfra tests for ISO Manager role
Tests directory structure, ISO files, mounts, and permissions
"""

import pytest


# =============================================================================
# Directory Existence Tests
# =============================================================================


@pytest.mark.parametrize(
    "path",
    [
        "/var/lib/isos",
        "/var/lib/iso_mounts",
    ],
)
def test_directories_exist(host, path):
    """Verify all required directories exist."""
    directory = host.file(path)
    assert directory.exists, f"Directory {path} should exist"
    assert directory.is_directory, f"{path} should be a directory"


# =============================================================================
# Directory Permission Tests
# =============================================================================


@pytest.mark.parametrize(
    "path",
    [
        "/var/lib/isos",
        "/var/lib/iso_mounts",
    ],
)
def test_directory_permissions(host, path):
    """Verify directories have correct permissions."""
    directory = host.file(path)
    assert directory.mode == 0o755, f"{path} should have mode 0755"


def test_directory_ownership(host):
    """Verify directories are owned by root."""
    for path in ["/var/lib/isos", "/var/lib/iso_mounts"]:
        directory = host.file(path)
        assert directory.user == "root", f"{path} should be owned by root"
        assert directory.group == "root", f"{path} should have group root"


# =============================================================================
# ISO File Tests
# =============================================================================


def test_iso_files_exist(host):
    """Verify configured ISO file(s) were downloaded."""
    ansible_vars = host.ansible.get_variables()

    # Derive ISO directory and filenames from role variables, with safe defaults
    iso_dir = ansible_vars.get("iso_storage_path", "/var/lib/isos")

    # Try to get resolved list, fallback to what we know is enabled in converge
    iso_images = ansible_vars.get("iso_images")
    if not iso_images:
        iso_filenames = ["tinycore-17.0.iso"]
    else:
        iso_filenames = [item["name"] + ".iso" for item in iso_images]

    for iso_name in iso_filenames:
        iso = host.file(f"{iso_dir}/{iso_name}")
        assert iso.exists, f"ISO file {iso_name} should exist in {iso_dir}"
        assert iso.is_file, f"ISO {iso_name} in {iso_dir} should be a regular file"


def test_iso_file_permissions(host):
    """Verify ISO files have correct permissions (0644)."""
    ansible_vars = host.ansible.get_variables()
    iso_dir = ansible_vars.get("iso_storage_path", "/var/lib/isos")

    iso_images = ansible_vars.get("iso_images")
    if not iso_images:
        iso_filenames = ["tinycore-17.0.iso"]
    else:
        iso_filenames = [item["name"] + ".iso" for item in iso_images]

    for iso_name in iso_filenames:
        iso = host.file(f"{iso_dir}/{iso_name}")
        if iso.exists:
            assert iso.mode == 0o644, f"ISO {iso_name} should have mode 0644"


def test_iso_files_are_not_empty(host):
    """Verify ISO files are not empty (basic integrity check)."""
    ansible_vars = host.ansible.get_variables()
    iso_dir = ansible_vars.get("iso_storage_path", "/var/lib/isos")

    iso_images = ansible_vars.get("iso_images")
    if not iso_images:
        iso_filenames = ["tinycore-17.0.iso"]
    else:
        iso_filenames = [item["name"] + ".iso" for item in iso_images]

    for iso_name in iso_filenames:
        iso = host.file(f"{iso_dir}/{iso_name}")
        if iso.exists:
            assert iso.size > 0, f"ISO {iso_name} should not be empty"
            # TinyCore is ~23MB, so check for minimum reasonable size
            assert iso.size > 1000000, f"ISO {iso_name} seems too small: {iso.size} bytes"


# =============================================================================
# Mount Point Tests
# =============================================================================


def test_mount_point_directories_exist(host):
    """Verify mount point directories exist for each ISO."""
    ansible_vars = host.ansible.get_variables()
    mount_root = ansible_vars.get("iso_mount_root", "/var/lib/iso_mounts")

    iso_images = ansible_vars.get("iso_images")
    if not iso_images:
        iso_names = ["tinycore-17.0"]
    else:
        iso_names = [item["name"] for item in iso_images]

    for name in iso_names:
        mount_point = f"{mount_root}/{name}"
        mp = host.file(mount_point)
        assert mp.exists, f"Mount point directory {mount_point} should exist"
        assert mp.is_directory, f"{mount_point} should be a directory"


def test_mount_point_permissions(host):
    """Verify mount point directories have correct permissions."""
    ansible_vars = host.ansible.get_variables()
    mount_root = ansible_vars.get("iso_mount_root", "/var/lib/iso_mounts")

    iso_images = ansible_vars.get("iso_images")
    if not iso_images:
        iso_names = ["tinycore-17.0"]
    else:
        iso_names = [item["name"] for item in iso_images]

    for name in iso_names:
        mount_point = f"{mount_root}/{name}"
        mp = host.file(mount_point)
        if mp.exists:
            assert mp.mode == 0o755, f"Mount point {mount_point} should have mode 0755"


# =============================================================================
# Mount Tests - 
# =============================================================================
# TODO: Disabled due to testing inside rootless Podman/Docker. If testing shows
#       GitHub docker has no problems then uncomment in default profile, and 
#       create a profile for local rooless testing.

# def test_iso_is_mounted(host):
#     """Verify ISO is actually mounted with correct FS type and options."""
#     ansible_vars = host.ansible.get_variables()
#     mount_root = ansible_vars.get("iso_mount_root", "/var/lib/iso_mounts")

#     iso_images = ansible_vars.get("iso_images")
#     if not iso_images:
#         iso_names = ["tinycore-17.0"]
#     else:
#         iso_names = [item["name"] for item in iso_images]

#     for name in iso_names:
#         mount_point = f"{mount_root}/{name}"

#         # Check mount point existence
#         mp = host.file(mount_point)
#         assert mp.exists, f"Mount point {mount_point} should exist"
#         assert mp.is_directory, f"Mount point {mount_point} should be a directory"

#         # Check mount details
#         result = host.run(f"findmnt -no FSTYPE,OPTIONS {mount_point}")
#         assert result.rc == 0, f"ISO should be mounted at {mount_point}"

#         stdout = result.stdout.strip()
#         assert stdout, "findmnt output should not be empty"

#         fields = stdout.split(None, 1)
#         assert len(fields) == 2, f"Unexpected findmnt output format: {stdout}"

#         fstype, options = fields
#         assert fstype == "iso9660", f"Unexpected filesystem type for ISO: {fstype}"
#         option_list = options.split(",")
#         assert "ro" in option_list, f"ISO mount should be read-only, got options: {options}"


# def test_mount_contains_loop_option(host):
#     """Verify mounts use loop device."""
#     ansible_vars = host.ansible.get_variables()
#     mount_root = ansible_vars.get("iso_mount_root", "/var/lib/iso_mounts")

#     iso_images = ansible_vars.get("iso_images")
#     if not iso_images:
#         iso_names = ["tinycore-17.0"]
#     else:
#         iso_names = [item["name"] for item in iso_images]

#     for name in iso_names:
#         mount_point = f"{mount_root}/{name}"
#         result = host.run(f"findmnt -no OPTIONS {mount_point}")
#         if result.rc == 0:
#             options = result.stdout.strip().split(",")
#             assert "loop" in options, f"Mount should use loop option at {mount_point}"


# =============================================================================
# Security Tests
# =============================================================================


def test_no_world_writable_paths(host):
    """Verify no world-writable files or directories in ISO paths."""
    # Check files
    result_files = host.run("find /var/lib/isos /var/lib/iso_mounts -type f -perm -002 2>/dev/null")
    assert result_files.stdout.strip() == "", "No files should be world-writable"

    # Check directories
    result_dirs = host.run("find /var/lib/isos /var/lib/iso_mounts -type d -perm -002 2>/dev/null")
    assert result_dirs.stdout.strip() == "", "No directories should be world-writable"


def test_no_setuid_setgid_files(host):
    """Verify no setuid or setgid files exist in ISO paths."""
    result = host.run("find /var/lib/isos /var/lib/iso_mounts -type f \\( -perm -4000 -o -perm -2000 \\) 2>/dev/null")
    assert result.stdout.strip() == "", "No setuid/setgid files should exist"


# =============================================================================
# Variable and Configuration Tests
# =============================================================================


def test_ansible_variables_are_defined(host):
    """Verify required Ansible variables are defined."""
    ansible_vars = host.ansible.get_variables()

    required_vars = [
        "iso_storage_path",
        "iso_mount_root",
        "iso_mount_enabled",
    ]

    for var in required_vars:
        assert var in ansible_vars, f"Variable {var} should be defined"


def test_iso_images_fact_is_set(host):
    """Verify iso_images fact is set and contains expected structure."""
    ansible_vars = host.ansible.get_variables()

    assert "iso_images" in ansible_vars, "iso_images fact should be set"
    iso_images = ansible_vars["iso_images"]

    assert isinstance(iso_images, list), "iso_images should be a list"
    assert len(iso_images) > 0, "iso_images should not be empty"

    # Verify each image has required fields
    for image in iso_images:
        assert "name" in image, "Each image should have a name"
        assert "url" in image, "Each image should have a url"
        assert isinstance(image["name"], str), "Image name should be a string"
        assert isinstance(image["url"], str), "Image url should be a string"


# =============================================================================
# Idempotency Tests
# =============================================================================


def test_directories_can_be_listed(host):
    """Verify directories are accessible and can be listed."""
    for path in ["/var/lib/isos", "/var/lib/iso_mounts"]:
        result = host.run(f"ls -la {path}")
        assert result.rc == 0, f"Should be able to list {path}"


# =============================================================================
# Regression Tests
# =============================================================================


def test_iso_catalog_contains_tinycore(host):
    """Regression test: Verify iso_catalog contains tinycore-17.0."""
    ansible_vars = host.ansible.get_variables()

    if "iso_catalog" in ansible_vars:
        catalog = ansible_vars["iso_catalog"]
        assert "tinycore-17.0" in catalog, "Catalog should contain tinycore-17.0"
        assert "url" in catalog["tinycore-17.0"], "tinycore-17.0 should have url"


def test_mount_point_naming_matches_iso_name(host):
    """Verify mount point directory names match ISO names (without .iso extension)."""
    ansible_vars = host.ansible.get_variables()
    iso_dir = ansible_vars.get("iso_storage_path", "/var/lib/isos")
    mount_root = ansible_vars.get("iso_mount_root", "/var/lib/iso_mounts")

    iso_images = ansible_vars.get("iso_images")
    if not iso_images:
        iso_names = ["tinycore-17.0"]
    else:
        iso_names = [item["name"] for item in iso_images]

    for name in iso_names:
        iso_path = f"{iso_dir}/{name}.iso"
        mount_path = f"{mount_root}/{name}"

        iso_file = host.file(iso_path)
        mount_dir = host.file(mount_path)

        if iso_file.exists:
            assert mount_dir.exists, f"Mount point {mount_path} should exist for ISO {iso_path}"


# =============================================================================
# Edge Case Tests
# =============================================================================


def test_iso_storage_path_is_not_root(host):
    """Ensure ISO storage is not accidentally set to root directory."""
    ansible_vars = host.ansible.get_variables()
    iso_dir = ansible_vars.get("iso_storage_path", "/var/lib/isos")

    assert iso_dir != "/", "ISO storage path should not be root"
    assert iso_dir != "/tmp", "ISO storage path should not be /tmp"


def test_mount_root_is_not_root(host):
    """Ensure mount root is not accidentally set to root directory."""
    ansible_vars = host.ansible.get_variables()
    mount_root = ansible_vars.get("iso_mount_root", "/var/lib/iso_mounts")

    assert mount_root != "/", "Mount root should not be root"
    assert mount_root != "/mnt", "Mount root should not be /mnt directly"
