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


def test_iso_file_exists(host):
    """Verify alpine ISO file was downloaded."""
    iso = host.file("/var/lib/isos/alpine-3.23.iso")
    assert iso.exists, "Alpine ISO file should exist"
    assert iso.is_file, "Alpine ISO should be a regular file"


# =============================================================================
# Mount Tests
# =============================================================================


def test_mount_point_exists(host):
    """Verify mount point directory exists."""
    mount_dir = host.file("/var/lib/iso_mounts/alpine-3.23")
    assert mount_dir.exists, "Mount point should exist"
    assert mount_dir.is_directory, "Mount point should be a directory"


def test_iso_is_mounted(host):
    """Verify ISO is actually mounted."""
    result = host.run("findmnt -n /var/lib/iso_mounts/alpine-3.23")
    assert result.rc == 0, "ISO should be mounted at /var/lib/iso_mounts/alpine-3.23"


def test_mounted_content_accessible(host):
    """Verify boot directory is accessible via mount."""
    boot = host.file("/var/lib/iso_mounts/alpine-3.23/boot")
    assert boot.exists, "Boot directory should be accessible via mount"
    assert boot.is_directory, "Boot should be a directory"


# =============================================================================
# Security Tests
# =============================================================================


def test_no_world_writable_files(host):
    """Verify no world-writable files in ISO directories."""
    result = host.run("find /var/lib/isos /var/lib/iso_mounts -type f -perm -002 2>/dev/null")
    assert result.stdout.strip() == "", "No files should be world-writable"
