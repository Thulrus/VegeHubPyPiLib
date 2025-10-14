# Changelog

All notable changes to the VegeHub PyPI package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.25] - 2025-10-14

### Added
- New endpoint handling in configuration
- Enhanced test coverage for endpoint modifications

### Changed
- Bumped version to 0.1.25

## [0.1.24] - 2025-06-24

### Changed
- Removed pytest as a runtime dependency

## [Unreleased] - 2025-06-12

### Changed
- Added to walkthrough.md documentation

## [Unreleased] - 2025-05-16

### Added
- Function to process update data for Home Assistant with clearer keys

### Fixed
- HA data converter issues

## [Unreleased] - 2025-02-21

### Changed
- Significantly improved error catching
- Updated tests and documentation

## [Unreleased] - 2025-02-20

### Added
- Exception catch for timeouts

## [Unreleased] - 2025-01-31

### Added
- Function to process updates into a dictionary of sensor values

### Changed
- Changed how info is stored

## [Unreleased] - 2025-01-09

### Added
- Ability to pass in info in the initialization

## [Unreleased] - 2025-01-03

### Added
- Properties to retrieve the device URL and software version
- Additional command to walkthrough documentation

## [Unreleased] - 2024-12-19

### Added
- Retry capability to all hub interactions

## [Unreleased] - 2024-12-18

### Added
- Properties to make it easier to pull out number of sensors and actuators

### Changed
- Updated the walkthrough file

## [Unreleased] - 2024-11-20

### Changed
- Expanded VegeHub class to allow storage of entities and unique_id

## [Unreleased] - 2024-11-18

### Added
- Helper file for data transforms with tests
- Transform for THERM200 sensor
- Import of new transform into __init__.py

## [Unreleased] - 2024-11-11

### Added
- Added walkthrough.md documentation file

## [Unreleased] - 2024-11-07

### Added
- Created python-package.yml for GitHub Actions
- Testing GitHub Actions workflow

## [0.1.7] - 2024-11-06

### Fixed
- File extension issue

## [0.1.5] - 2024-11-05

### Changed
- Version bump to 0.1.5

## [0.1.4] - 2024-11-05

### Changed
- Version bump to 0.1.4

## [0.1.3] - 2024-11-05

### Changed
- Version bump to 0.1.3

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
