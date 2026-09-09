# FluxSentinel

FluxSentinel is a lightweight file integrity monitoring tool written in Python.

It creates a SHA-256 snapshot of files and compares future scans against the previous state to detect:

- New files
- Modified files
- Deleted files

## Why FluxSentinel?

Instead of manually checking important directories, FluxSentinel gives you a simple way to detect unexpected file changes.

It can be useful for:

- Project directories
- Configuration files
- Deployment environments
- Local security monitoring
- Backup verification
- Development workflows

## Requirements

- Python 3.8+
- No external dependencies

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/FluxSentinel.git
cd FluxSentinel
