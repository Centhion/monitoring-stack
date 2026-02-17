#!/usr/bin/env python3
"""
Documentation Sync Checker

Detects gaps between codebase and documentation (README.md, ARCHITECTURE.md).
Auto-detects project type and checks appropriate directories.
Flags potential issues for human review before commit.

Supported project types:
- Flutter/Dart (pubspec.yaml)
- Python (requirements.txt, pyproject.toml)
- Node.js (package.json)
- Go (go.mod)
- Generic fallback

Usage:
    python3 doc_sync_check.py           # Run full check
    python3 doc_sync_check.py --quiet   # Only show issues (no header)
"""

import os
import re
import sys
import json
from pathlib import Path


# Project type configurations
# Each defines where to look for services, screens/routes, and dependencies
PROJECT_CONFIGS = {
    'flutter': {
        'detection': 'pubspec.yaml',
        'service_paths': ['lib/data/services', 'lib/services'],
        'screen_paths': ['lib/presentation/screens', 'lib/screens', 'lib/ui/screens'],
        'deps_file': 'pubspec.yaml',
        'deps_parser': 'pubspec',
        'ignore_patterns': ['.g.dart', '.freezed.dart'],
    },
    'python': {
        'detection': ['requirements.txt', 'pyproject.toml', 'setup.py'],
        'service_paths': ['src/services', 'app/services', 'services'],
        'screen_paths': ['src/routes', 'app/routes', 'src/views', 'app/views'],
        'deps_file': 'requirements.txt',
        'deps_parser': 'requirements',
        'ignore_patterns': ['__pycache__', '.pyc'],
    },
    'node': {
        'detection': 'package.json',
        'service_paths': ['src/services', 'lib/services', 'services'],
        'screen_paths': ['src/routes', 'src/controllers', 'src/pages', 'pages'],
        'deps_file': 'package.json',
        'deps_parser': 'package_json',
        'ignore_patterns': ['.test.js', '.spec.js', '.test.ts', '.spec.ts'],
    },
    'go': {
        'detection': 'go.mod',
        'service_paths': ['internal/services', 'pkg/services', 'services'],
        'screen_paths': ['internal/handlers', 'pkg/handlers', 'cmd'],
        'deps_file': 'go.mod',
        'deps_parser': 'go_mod',
        'ignore_patterns': ['_test.go'],
    },
    'generic': {
        'detection': None,
        'service_paths': ['src/services', 'lib/services', 'services'],
        'screen_paths': ['src/routes', 'src/screens', 'src/pages'],
        'deps_file': None,
        'deps_parser': None,
        'ignore_patterns': [],
    },
}


def get_project_root():
    """Find project root by looking for common markers."""
    current = Path.cwd()
    markers = ['.git', 'pubspec.yaml', 'package.json', 'requirements.txt', 'go.mod']

    while current != current.parent:
        for marker in markers:
            if (current / marker).exists():
                return current
        current = current.parent
    return Path.cwd()


def detect_project_type(root):
    """Detect project type based on config files present."""
    for proj_type, config in PROJECT_CONFIGS.items():
        if proj_type == 'generic':
            continue

        detection = config['detection']
        if isinstance(detection, list):
            if any((root / f).exists() for f in detection):
                return proj_type
        elif detection and (root / detection).exists():
            return proj_type

    return 'generic'


def read_file(path):
    """Read file contents, return empty string if not found."""
    try:
        with open(path, 'r') as f:
            return f.read()
    except (FileNotFoundError, PermissionError):
        return ""


def get_files_in_paths(root, paths, ignore_patterns):
    """Get list of source files in specified paths."""
    files = []

    for rel_path in paths:
        full_path = root / rel_path
        if not full_path.exists():
            continue

        for item in full_path.rglob('*'):
            if item.is_file():
                # Skip ignored patterns
                skip = False
                for pattern in ignore_patterns:
                    if pattern in item.name:
                        skip = True
                        break
                if not skip:
                    # Store relative path from the checked directory
                    rel_to_check = item.relative_to(full_path)
                    files.append(f"{rel_path}/{rel_to_check}")

    return sorted(files)


def parse_pubspec_deps(content):
    """Parse dependencies from pubspec.yaml."""
    deps = []
    in_dependencies = False

    for line in content.split('\n'):
        if line.strip() == 'dependencies:':
            in_dependencies = True
            continue

        if in_dependencies and line and not line.startswith(' ') and not line.startswith('\t'):
            if ':' in line:
                in_dependencies = False
                continue

        if in_dependencies and line.strip():
            match = re.match(r'^[ \t]+([a-z_][a-z0-9_]*):', line)
            if match:
                dep_name = match.group(1)
                if dep_name != 'flutter':
                    deps.append(dep_name)

    return sorted(deps)


def parse_requirements_deps(content):
    """Parse dependencies from requirements.txt."""
    deps = []
    for line in content.split('\n'):
        line = line.strip()
        if line and not line.startswith('#'):
            # Handle package==version, package>=version, etc.
            match = re.match(r'^([a-zA-Z0-9_-]+)', line)
            if match:
                deps.append(match.group(1).lower())
    return sorted(deps)


def parse_package_json_deps(content):
    """Parse dependencies from package.json."""
    deps = []
    try:
        data = json.loads(content)
        for section in ['dependencies', 'devDependencies']:
            if section in data:
                deps.extend(data[section].keys())
    except json.JSONDecodeError:
        pass
    return sorted(deps)


def parse_go_mod_deps(content):
    """Parse dependencies from go.mod."""
    deps = []
    in_require = False

    for line in content.split('\n'):
        line = line.strip()

        if line.startswith('require ('):
            in_require = True
            continue
        elif line == ')':
            in_require = False
            continue

        if in_require and line:
            # Extract module path
            parts = line.split()
            if parts:
                deps.append(parts[0])
        elif line.startswith('require '):
            # Single-line require
            parts = line.replace('require ', '').split()
            if parts:
                deps.append(parts[0])

    return sorted(deps)


def get_dependencies(root, config):
    """Get dependencies based on project type."""
    if not config['deps_file']:
        return []

    content = read_file(root / config['deps_file'])
    if not content:
        return []

    parser = config['deps_parser']
    if parser == 'pubspec':
        return parse_pubspec_deps(content)
    elif parser == 'requirements':
        return parse_requirements_deps(content)
    elif parser == 'package_json':
        return parse_package_json_deps(content)
    elif parser == 'go_mod':
        return parse_go_mod_deps(content)

    return []


def check_architecture_md(root, services, screens, dependencies):
    """Check if items are documented in ARCHITECTURE.md."""
    arch_content = read_file(root / 'ARCHITECTURE.md')
    if not arch_content:
        return {
            'missing_services': services,
            'missing_screens': screens,
            'missing_deps': dependencies,
            'no_file': True
        }

    arch_lower = arch_content.lower()

    missing_services = []
    for svc in services:
        # Check if service filename appears in ARCHITECTURE.md
        filename = Path(svc).name
        if filename.lower() not in arch_lower:
            missing_services.append(svc)

    missing_screens = []
    for screen in screens:
        filename = Path(screen).name
        if filename.lower() not in arch_lower:
            missing_screens.append(screen)

    missing_deps = []
    for dep in dependencies:
        # Normalize for comparison (handle underscores/hyphens)
        dep_normalized = dep.lower().replace('_', '').replace('-', '')
        arch_normalized = arch_lower.replace('_', '').replace('-', '')
        if dep_normalized not in arch_normalized:
            missing_deps.append(dep)

    return {
        'missing_services': missing_services,
        'missing_screens': missing_screens,
        'missing_deps': missing_deps,
        'no_file': False
    }


def check_readme_md(root):
    """Check if README.md exists and has basic sections."""
    readme_content = read_file(root / 'README.md')
    if not readme_content:
        return {'no_file': True, 'missing_sections': []}

    missing_sections = []
    expected_sections = ['## Features', '## Quick Start']

    for section in expected_sections:
        if section.lower() not in readme_content.lower():
            missing_sections.append(section)

    return {'no_file': False, 'missing_sections': missing_sections}


def main():
    quiet = '--quiet' in sys.argv

    root = get_project_root()
    project_type = detect_project_type(root)
    config = PROJECT_CONFIGS[project_type]

    # Gather actual files
    services = get_files_in_paths(root, config['service_paths'], config['ignore_patterns'])
    screens = get_files_in_paths(root, config['screen_paths'], config['ignore_patterns'])
    dependencies = get_dependencies(root, config)

    # Check ARCHITECTURE.md
    arch_results = check_architecture_md(root, services, screens, dependencies)

    # Check README.md
    readme_results = check_readme_md(root)

    # Report results
    has_issues = False

    if not quiet:
        print("=" * 50)
        print("DOCUMENTATION SYNC CHECK")
        print(f"Project type: {project_type}")
        print("=" * 50)

    # ARCHITECTURE.md issues
    if arch_results['no_file']:
        print("\nARCHITECTURE.md: FILE NOT FOUND")
        has_issues = True
    else:
        if arch_results['missing_services']:
            has_issues = True
            print("\nServices not in ARCHITECTURE.md:")
            for svc in arch_results['missing_services']:
                print(f"  - {svc}")

        if arch_results['missing_screens']:
            has_issues = True
            print("\nScreens/Routes not in ARCHITECTURE.md:")
            for screen in arch_results['missing_screens']:
                print(f"  - {screen}")

        if arch_results['missing_deps']:
            has_issues = True
            print("\nDependencies not in ARCHITECTURE.md:")
            for dep in arch_results['missing_deps']:
                print(f"  - {dep}")

    # README.md issues
    if readme_results['no_file']:
        print("\nREADME.md: FILE NOT FOUND")
        has_issues = True
    elif readme_results['missing_sections']:
        print("\nREADME.md missing sections:")
        for section in readme_results['missing_sections']:
            print(f"  - {section}")
        has_issues = True

    # Summary
    if not quiet:
        print()
        if has_issues:
            print("=" * 50)
            print("REVIEW: Update docs if these are impactful changes.")
            print("Skip if: bug fixes, refactors, internal files.")
            print("=" * 50)
        else:
            print("Documentation appears in sync.")

    # Exit code: 0 = allows commit to proceed (advisory, not blocking)
    sys.exit(0)


if __name__ == "__main__":
    main()
