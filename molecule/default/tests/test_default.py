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


# =============================================================================
# Mount Tests
# =============================================================================


def test_iso_is_mounted(host):
    """Verify ISO is actually mounted with correct FS type and options."""
    ansible_vars = host.ansible.get_variables()
    mount_root = ansible_vars.get("iso_mount_root", "/var/lib/iso_mounts")
    
    iso_images = ansible_vars.get("iso_images")
    if not iso_images:
        iso_names = ["tinycore-17.0"]
    else:
        iso_names = [item["name"] for item in iso_images]
        
    for name in iso_names:
        mount_point = f"{mount_root}/{name}"
        
        # Check mount point existence
        mp = host.file(mount_point)
        assert mp.exists, f"Mount point {mount_point} should exist"
        assert mp.is_directory, f"Mount point {mount_point} should be a directory"
        
        # Check mount details
        result = host.run(f"findmnt -no FSTYPE,OPTIONS {mount_point}")
        assert result.rc == 0, f"ISO should be mounted at {mount_point}"
        
        stdout = result.stdout.strip()
        assert stdout, "findmnt output should not be empty"
        
        fields = stdout.split(None, 1)
        assert len(fields) == 2, f"Unexpected findmnt output format: {stdout}"
        
        fstype, options = fields
        assert fstype == "iso9660", f"Unexpected filesystem type for ISO: {fstype}"
        option_list = options.split(",")
        assert "ro" in option_list, f"ISO mount should be read-only, got options: {options}"


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
