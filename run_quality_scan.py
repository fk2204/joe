#!/usr/bin/env python3
"""
Quality baseline scan tool.
Runs flake8 and mypy on src/ and generates a report.
"""

import subprocess
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

def run_flake8() -> Tuple[str, Dict[str, int]]:
    """Run flake8 and extract statistics."""
    try:
        result = subprocess.run(
            [
                "python",
                "-m",
                "flake8",
                "src/",
                "--max-line-length=100",
                "--ignore=E203,W503",
                "--statistics",
            ],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent),
        )
        output = result.stdout + result.stderr

        # Parse statistics from output
        stats = {}
        for line in output.split('\n'):
            if line and any(c.isdigit() for c in line):
                # Lines with stats look like: "123 E501 line too long"
                parts = line.split()
                if len(parts) >= 2 and parts[0].isdigit():
                    try:
                        count = int(parts[0])
                        code = parts[1]
                        stats[code] = count
                    except (ValueError, IndexError):
                        pass

        return output, stats
    except FileNotFoundError:
        return "flake8 not installed. Run: pip install flake8", {}
    except Exception as e:
        return f"Error running flake8: {e}", {}


def run_mypy() -> Tuple[str, Dict[str, int]]:
    """Run mypy and extract statistics."""
    try:
        result = subprocess.run(
            [
                "python",
                "-m",
                "mypy",
                "src/",
                "--ignore-missing-imports",
                "--statistics",
            ],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent),
        )
        output = result.stdout + result.stderr

        # Parse statistics from output
        stats = {}
        for line in output.split('\n'):
            if 'error:' in line.lower():
                # Count error types
                if 'no redef' in line.lower():
                    stats['error: no redef'] = stats.get('error: no redef', 0) + 1
                elif 'arg-type' in line.lower():
                    stats['error: arg-type'] = stats.get('error: arg-type', 0) + 1
                elif 'return-value' in line.lower():
                    stats['error: return-value'] = stats.get('error: return-value', 0) + 1
                elif 'assignment' in line.lower():
                    stats['error: assignment'] = stats.get('error: assignment', 0) + 1
                else:
                    stats['error: other'] = stats.get('error: other', 0) + 1
            elif 'warning:' in line.lower():
                stats['warning: other'] = stats.get('warning: other', 0) + 1

        # Try to extract summary stats
        for line in output.split('\n'):
            if 'found' in line.lower() and 'error' in line.lower():
                # Line like "Found X errors in Y files"
                parts = line.split()
                for i, part in enumerate(parts):
                    if part.lower() == 'found' and i + 1 < len(parts):
                        try:
                            count = int(parts[i + 1])
                            stats['total_errors'] = count
                        except ValueError:
                            pass

        return output, stats
    except FileNotFoundError:
        return "mypy not installed. Run: pip install mypy", {}
    except Exception as e:
        return f"Error running mypy: {e}", {}


def generate_report(flake8_output: str, flake8_stats: Dict[str, int],
                   mypy_output: str, mypy_stats: Dict[str, int]) -> str:
    """Generate the quality baseline report."""
    timestamp = datetime.now().isoformat()

    # Calculate totals
    flake8_total = sum(flake8_stats.values())
    mypy_total = mypy_stats.get('total_errors', sum(
        v for k, v in mypy_stats.items() if k != 'total_errors'
    ))

    # Build report
    lines = [
        "=" * 80,
        "QUALITY BASELINE REPORT",
        "=" * 80,
        f"Generated: {timestamp}",
        "",
        "=" * 80,
        "FLAKE8 REPORT (PEP8 Linting)",
        "=" * 80,
        "",
        "Violations by Code:",
    ]

    # Sort by count descending
    sorted_flake8 = sorted(flake8_stats.items(), key=lambda x: x[1], reverse=True)
    for code, count in sorted_flake8:
        lines.append(f"  {code:8s}: {count:4d} violations")

    lines.extend([
        "",
        f"Total Flake8 Violations: {flake8_total}",
        "",
        "=" * 80,
        "MYPY REPORT (Type Checking)",
        "=" * 80,
        "",
        "Violations by Type:",
    ])

    sorted_mypy = sorted(mypy_stats.items(), key=lambda x: x[1], reverse=True)
    for error_type, count in sorted_mypy:
        if error_type != 'total_errors':
            lines.append(f"  {error_type:30s}: {count:4d}")

    lines.extend([
        "",
        f"Total Mypy Errors: {mypy_total}",
        "",
        "=" * 80,
        "SUMMARY",
        "=" * 80,
        f"Total Code Quality Violations: {flake8_total + mypy_total}",
        "",
        "Breakdown by Category:",
        f"  Linting (flake8):     {flake8_total:6d} ({100*flake8_total/(flake8_total+mypy_total or 1):.1f}%)",
        f"  Type Errors (mypy):   {mypy_total:6d} ({100*mypy_total/(flake8_total+mypy_total or 1):.1f}%)",
        "",
        "Top Issues (Flake8):",
    ])

    for code, count in sorted_flake8[:5]:
        lines.append(f"  {code:8s}: {count:4d}")

    lines.extend([
        "",
        "=" * 80,
        "DETAILED OUTPUT",
        "=" * 80,
        "",
        "Flake8 Full Output:",
        "-" * 40,
        flake8_output if flake8_output else "(No output)",
        "",
        "Mypy Full Output:",
        "-" * 40,
        mypy_output if mypy_output else "(No output)",
        "",
    ])

    return "\n".join(lines)


def main():
    """Main execution."""
    print("Running quality baseline scan...")
    print()

    # Run scanners
    print("Running flake8...")
    flake8_output, flake8_stats = run_flake8()

    print("Running mypy...")
    mypy_output, mypy_stats = run_mypy()

    # Generate report
    report = generate_report(flake8_output, flake8_stats, mypy_output, mypy_stats)

    # Write to file
    docs_path = Path(__file__).parent / "docs" / "quality-baseline.txt"
    docs_path.parent.mkdir(parents=True, exist_ok=True)

    with open(docs_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"Report written to: {docs_path}")
    print()

    # Print to stdout
    print(report)


if __name__ == "__main__":
    main()
