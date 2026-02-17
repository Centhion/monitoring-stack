#!/usr/bin/env python3
"""
Project Status Reporter

Provides situational awareness by showing Git status, active tasks
from PROJECT_PLAN.md, and recent session summaries from SESSION_LOG.md.

Designed for workflows with multiple parallel agents, each creating
their own handoff entries.
"""

import os
import re
import subprocess
from datetime import datetime, timedelta


def parse_session_date(session_header):
    """Extract date from session header like '## Session: 2025-12-29 21:45'.

    Returns datetime object or None if parsing fails.
    """
    # Match various date formats: YYYY-MM-DD HH:MM, YYYY-MM-DD, or descriptive
    match = re.search(r'(\d{4}-\d{2}-\d{2})\s*(\d{2}:\d{2})?', session_header)
    if match:
        date_str = match.group(1)
        time_str = match.group(2) or "00:00"
        try:
            return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        except ValueError:
            pass
    return None


def get_recent_sessions(hours=24):
    """Extract session entries from the last N hours.

    Returns all sessions within the time window to capture work from
    multiple parallel agents.
    """
    log_path = "docs/SESSION_LOG.md"
    if not os.path.exists(log_path):
        return "No SESSION_LOG.md found."

    with open(log_path, 'r') as f:
        content = f.read()

    # Find all session entries (start with ## Session:)
    session_pattern = r'(## Session:[^\n]*\n.*?)(?=\n---\s*$|\n## Session:|\Z)'
    sessions = re.findall(session_pattern, content, re.DOTALL)

    if not sessions:
        return "No session entries found in SESSION_LOG.md"

    # Filter to sessions within the time window
    cutoff = datetime.now() - timedelta(hours=hours)
    recent_sessions = []

    for session in sessions:
        first_line = session.split('\n')[0]
        session_date = parse_session_date(first_line)

        # Include if date is recent, or if we can't parse the date (be inclusive)
        if session_date is None or session_date >= cutoff:
            recent_sessions.append(session.strip())

    # If no recent sessions found, show the last one regardless of date
    if not recent_sessions and sessions:
        recent_sessions = [sessions[-1].strip()]
        return "(No sessions in last 24h - showing most recent)\n\n" + recent_sessions[0]

    # Truncate each session if too long (keep first 40 lines max per session)
    output_sessions = []
    for session in recent_sessions:
        lines = session.split('\n')
        if len(lines) > 40:
            session = '\n'.join(lines[:40]) + '\n... (truncated)'
        output_sessions.append(session)

    # Join with separator
    return "\n\n---\n\n".join(output_sessions)


def get_all_active_tasks():
    """Extract ALL active tasks from PROJECT_PLAN.md, grouped by section.

    Returns all unchecked (- [ ]) and in-progress (- [/]) tasks
    organized by their parent section headers for easier batching.
    """
    docs_path = "docs/PROJECT_PLAN.md"
    if not os.path.exists(docs_path):
        return "No PROJECT_PLAN.md found."

    with open(docs_path, 'r') as f:
        lines = f.readlines()

    # Track current section and collect tasks by section
    current_section = "Uncategorized"
    tasks_by_section = {}
    total_tasks = 0

    for line in lines:
        stripped = line.strip()

        # Detect section headers (## Level 2 headers)
        if stripped.startswith("## "):
            current_section = stripped[3:].strip()

        # Collect unchecked or in-progress tasks
        elif stripped.startswith("- [ ]") or stripped.startswith("- [/]"):
            if current_section not in tasks_by_section:
                tasks_by_section[current_section] = []
            tasks_by_section[current_section].append(stripped)
            total_tasks += 1

    if total_tasks == 0:
        return "No pending tasks found."

    # Build output grouped by section
    output_lines = [f"({total_tasks} pending tasks)"]

    for section, tasks in tasks_by_section.items():
        output_lines.append(f"\n## {section} ({len(tasks)})")
        for task in tasks:
            output_lines.append(task)

    return "\n".join(output_lines)


def get_git_status():
    """Get current Git status."""
    try:
        result = subprocess.check_output(
            ['git', 'status', '--short'],
            text=True,
            stderr=subprocess.DEVNULL
        ).strip()
        return result if result else "Clean working directory."
    except subprocess.CalledProcessError:
        return "Not a git repository."
    except FileNotFoundError:
        return "Git not installed."


def main():
    """Display project status report."""
    print("PROJECT STATUS REPORT")
    print("=" * 40)

    print("\n[RECENT SESSIONS (last 24h)]")
    print(get_recent_sessions(hours=24))

    print("\n" + "-" * 40)

    print("\n[GIT STATUS]")
    print(get_git_status())

    print("\n[ALL PENDING TASKS]")
    print(get_all_active_tasks())

    print("\n[REMINDER]")
    print("Run /handoff before ending your session to preserve context.")


if __name__ == "__main__":
    main()
