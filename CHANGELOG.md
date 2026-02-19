# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [1.0.5](https://github.com/TrevorBenson/ansible-role-iso-manager/compare/v1.0.4...v1.0.5) (2026-02-19)

### Bug Fixes

* Update Ansible Galaxy namespace and role references from 'trevorbenson' to 'TrevorBenson'. ([6d29966](https://github.com/TrevorBenson/ansible-role-iso-manager/commit/6d299661f80e22ffa399e7e58f9ec91a65b65c88))

## [1.0.4](https://github.com/TrevorBenson/ansible-role-iso-manager/compare/v1.0.3...v1.0.4) (2026-02-19)

### Bug Fixes

* empty version bump ([#13](https://github.com/TrevorBenson/ansible-role-iso-manager/issues/13)) ([86c21e2](https://github.com/TrevorBenson/ansible-role-iso-manager/commit/86c21e202958c6bdbe7f4a7c28f831bfb33b7f0c))

## [1.0.3](https://github.com/TrevorBenson/ansible-role-iso-manager/compare/v1.0.2...v1.0.3) (2026-02-19)

### Bug Fixes

* version bump ([fa19c4c](https://github.com/TrevorBenson/ansible-role-iso-manager/commit/fa19c4c6b4a6fb7352d4b97b87f67c88e7726941))

### Maintenance

* Fix items that yaml lint and ansible lint did not catch, but that the galaxy-action lists as issues ([#12](https://github.com/TrevorBenson/ansible-role-iso-manager/issues/12)) ([112f9aa](https://github.com/TrevorBenson/ansible-role-iso-manager/commit/112f9aa3343a610083ac184968cffb65f1f915f9))

## [1.0.2](https://github.com/TrevorBenson/ansible-role-iso-manager/compare/v1.0.1...v1.0.2) (2026-02-19)

### Bug Fixes

* Remove version from galaxy info metadata, it causes failures in ansible-lint and prevents the galaxy publishing and role importing from suceeding. ([#11](https://github.com/TrevorBenson/ansible-role-iso-manager/issues/11)) ([5169ed9](https://github.com/TrevorBenson/ansible-role-iso-manager/commit/5169ed970f04e3cc9ad4a50645565dee424d91a5))

## [1.0.1](https://github.com/TrevorBenson/ansible-role-iso-manager/compare/v1.0.0...v1.0.1) (2026-02-18)

### Bug Fixes

* Set correct branch name for galaxy publishing ([#9](https://github.com/TrevorBenson/ansible-role-iso-manager/issues/9)) ([5afecba](https://github.com/TrevorBenson/ansible-role-iso-manager/commit/5afecbaec860647585b0ac2f516c770557097d9e))

## 1.0.0 (2026-02-18)

### Features

* add script to automate publishing Ansible roles to Galaxy ([#5](https://github.com/TrevorBenson/ansible-role-iso-manager/issues/5)) ([921e2a0](https://github.com/TrevorBenson/ansible-role-iso-manager/commit/921e2a010a15d5f17b92457107a2b4f0a7dedcd3))
* Automate publishing Ansible roles to Galaxy ([#7](https://github.com/TrevorBenson/ansible-role-iso-manager/issues/7)) ([510e718](https://github.com/TrevorBenson/ansible-role-iso-manager/commit/510e7189fd9095d386e3f550523bc724f30333ca))

### Bug Fixes

* Resolve final CI fixes so PR checks can be a gate. ([#4](https://github.com/TrevorBenson/ansible-role-iso-manager/issues/4)) ([24083a0](https://github.com/TrevorBenson/ansible-role-iso-manager/commit/24083a0c9226c484f9485c97967029801902ef0a))

### CI/CD

* remove --branches flag that overrides semantic-release config ([#8](https://github.com/TrevorBenson/ansible-role-iso-manager/issues/8)) ([27d98e7](https://github.com/TrevorBenson/ansible-role-iso-manager/commit/27d98e7eb9b32020b007d818016fa2311d50125e))
