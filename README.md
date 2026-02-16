# Ansible Role: ISO Manager

[![Ansible Galaxy](https://img.shields.io/badge/galaxy-trevorbenson.iso__manager-blue.svg)](https://galaxy.ansible.com/trevorbenson/iso_manager)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

Downloads and loop-mounts ISO images for PXE network boot environments. Provides a predefined catalog of known images and supports custom image definitions.

## Requirements

- Ansible >= 2.14
- `ansible.posix` collection (for `mount` module)
- Root access (`become: true`)

```bash
ansible-galaxy collection install ansible.posix
```

## Role Variables

### Storage Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `iso_storage_path` | `/var/lib/isos` | Directory where ISO files are stored |
| `iso_mount_root`     | `/var/lib/iso_mounts` | Directory where ISOs are loop-mounted |

### Image Selection

| Variable             | Default | Description |
|----------------------|---------|-------------|
| `iso_enabled_images` | `{{ enabled_images \| default([]) }}` | List of catalog key names to enable (falls back to shared `enabled_images`) |
| `iso_custom_images`  | `[]`    | List of custom image definitions (each with `name` and `url`) |

### Built-in Catalog

The role includes a predefined catalog (`iso_catalog`) with URLs for the following images:

| Key            | Distribution     |
|----------------|------------------|
| `alpine-3.23`  | Alpine 3.23      |
| `ubuntu-18.04` | Ubuntu 18.04 LTS |
| `ubuntu-20.04` | Ubuntu 20.04 LTS |
| `ubuntu-22.04` | Ubuntu 22.04 LTS |
| `ubuntu-24.04` | Ubuntu 24.04 LTS |
| `rocky-8.4` — `rocky-8.10` | Rocky Linux 8.x (full and `-minimal` variants) |
| `rocky-9.0` — `rocky-9.4` | Rocky Linux 9.x (full and `-minimal` variants) |
| `rocky-10.0` — `rocky-10.1` | Rocky Linux 10.x (full and `-minimal` variants) |

## Example Playbooks

### Basic Usage — Select from Catalog

```yaml
- hosts: pxe_servers
  become: true
  roles:
    - role: trevorbenson.iso_manager
      vars:
        iso_enabled_images:
          - ubuntu-24.04
          - rocky-9.4
```

### Custom Images

```yaml
- hosts: pxe_servers
  become: true
  roles:
    - role: trevorbenson.iso_manager
      vars:
        iso_enabled_images:
          - ubuntu-24.04
        iso_custom_images:
          - name: ubuntu-26.04
            url: https://releases.ubuntu.com/26.04/ubuntu-26.04-live-server-amd64.iso
```

### Integration with PXE Server and Menu

When combining all three roles, set the shared `enabled_images` and `custom_images` variables at the play level. Each role derives what it needs:

```yaml
- hosts: pxe_servers
  become: true
  vars:
    enabled_images:
      - ubuntu-24.04
      - rocky-9.4
    custom_images:
      - name: ubuntu-26.04
        url: https://releases.ubuntu.com/26.04/ubuntu-26.04-live-server-amd64.iso
        kernel_path: casper/vmlinuz
        initrd_path: casper/initrd
  roles:
    - iso_manager    # downloads + mounts ISOs (uses url)
    - pxe_server     # installs services
    - pxe_menu       # renders boot menus (uses kernel_path, initrd_path)
```

## Output

After running the role, each enabled image will be:

1. **Downloaded** to `{{ iso_storage_path }}/{{ name }}.iso`
2. **Mounted** (read-only, loop) at `{{ iso_mount_root }}/{{ name }}/`

The `iso_images` fact is set and available to subsequent roles (e.g., `pxe_menu`) containing the merged list of catalog + custom images.

## Testing

### Run Molecule Tests

```bash
# Install dependencies
uv pip install -r requirements-dev.txt
ansible-galaxy collection install ansible.posix community.docker

# Run tests
molecule test
```

### Test Matrix

| Platform         | Image                                |
|------------------|--------------------------------------|
| Rocky Linux 9    | `geerlingguy/docker-rockylinux9-ansible` |
| Ubuntu 22.04     | `geerlingguy/docker-ubuntu2204-ansible`  |
| Ubuntu 24.04     | `geerlingguy/docker-ubuntu2404-ansible`  |

## License

Apache 2.0

## Author Information

This role was created by [Trevor Benson](https://github.com/TrevorBenson).
