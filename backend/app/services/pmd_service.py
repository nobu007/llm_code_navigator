import subprocess
import json
from typing import Dict, List, Any
from app.core.logging import logger
from app.models.pmd import PmdResult, PmdViolation


def run_pmd_analysis(path: str) -> PmdResult:
    """Run PMD analysis on the given path and return structured PmdResult."""
    try:
        completed = subprocess.run(
            [
                "pmd",
                "-d",
                path,
                "-R",
                "rulesets/java/quickstart.xml",
                "-f",
                "json",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        
        # Parse PMD JSON output
        pmd_output = json.loads(completed.stdout)
        
        # Extract violations from PMD output structure
        violations = []
        total_violations = 0
        
        if "files" in pmd_output:
            for file_data in pmd_output["files"]:
                if "violations" in file_data:
                    for violation in file_data["violations"]:
                        violations.append(PmdViolation(
                            rule=violation.get("rule", "Unknown"),
                            priority=violation.get("priority", 3),
                            message=violation.get("description", "No description"),
                            line=violation.get("beginline", 0),
                            column=violation.get("begincolumn", 0)
                        ))
                        total_violations += 1
        
        # Create summary
        summary = {
            "totalViolations": total_violations,
            "fileAnalyzed": path,
            "pmdVersion": pmd_output.get("pmdVersion", "unknown"),
            "timestamp": pmd_output.get("timestamp", "")
        }
        
        return PmdResult(violations=violations, summary=summary)
        
    except FileNotFoundError as e:
        logger.error("PMD command not found")
        raise RuntimeError("PMD command not found") from e
    except subprocess.CalledProcessError as e:
        logger.error(f"PMD analysis failed: {e.stderr}")
        raise RuntimeError("PMD analysis failed") from e
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse PMD JSON output: {e}")
        raise RuntimeError("Failed to parse PMD output") from e
