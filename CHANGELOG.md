# Changelog

All notable changes to the VegeHub PyPI package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.25] - 2025-10-14

### Added
- New endpoint handling in configuration
- Enhanced test coverage for endpoint modifications

## [0.1.24] - 2025-06-24

### Changed
- Removed pytest as a runtime dependency

## [0.1.23] - 2025-06-12

### Changed
- Added to walkthrough.md documentation

### Fixed
- HA data converter issues

## [0.1.22] - 2025-05-16

### Added
- Function to process update data for Home Assistant with clearer keys

## [0.1.21] - 2025-02-21

### Changed
- Significantly improved error catching
- Updated tests and documentation

## [0.1.19] - 2025-02-20

### Added
- Exception catch for timeouts

## [0.1.18] - 2025-01-31

### Added
- Function to process updates into a dictionary of sensor values

### Changed
- Changed how info is stored

## [0.1.15] - 2025-01-09

### Added
- Ability to pass in info in the initialization

## [0.1.14] - 2025-01-03

### Added
- Properties to retrieve the device URL and software version
- Additional command to walkthrough documentation

## [0.1.13] - 2024-12-19

### Added
- Retry capability to all hub interactions

## [0.1.12] - 2024-12-18

### Added
- Properties to make it easier to pull out number of sensors and actuators

### Changed
- Updated the walkthrough file

## [0.1.11] - 2024-11-20

### Changed
- Expanded VegeHub class to allow storage of entities and unique_id

## [0.1.10] - 2024-11-18

### Fixed
- Import of new transform into __init__.py

## [0.1.9] - 2024-11-18

### Added
- Transform for THERM200 sensor

## [0.1.8] - 2024-11-18

### Added
- Helper file for data transforms with tests

## [0.1.7] - 2024-11-11

### Added
- walkthrough.md documentation file
- Created python-package.yml for GitHub Actions
- Testing GitHub Actions workflow

### Fixed
- File extension issue

## [0.1.5] - 2024-11-05

### Changed
- Updated aiohttp dependency to ^3.10.8

## [0.1.4] - 2024-11-05

### Added
- Support for passing MAC address to constructor

### Changed
- Simplified MAC address handling (removed separate simple_mac_address property)
- Updated documentation for setup method

## [0.1.3] - 2024-11-05

### Fixed
- False positive pylint error on fixtures

## [0.1.0] - 2024-11-05

### Added
- Initial commit for VegeHub PyPI package
- Basic VegeHub class for contacting the hub
- Support for retrieving MAC address from the hub
- Support for setting actuators
- API key and server address configuration
- Comprehensive test suite
- Poetry-based project structure
- README with basic usage instructions
- GPL-3.0 license
