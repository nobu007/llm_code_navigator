import subprocess
import json
from app.core.logging import logger


def run_pmd_analysis(path: str) -> dict:
    """Run PMD analysis on the given path and return the parsed JSON result."""
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
        return json.loads(completed.stdout)
    except FileNotFoundError as e:
        logger.error("PMD command not found")
        raise RuntimeError("PMD command not found") from e
    except subprocess.CalledProcessError as e:
        logger.error(f"PMD analysis failed: {e.stderr}")
        raise RuntimeError("PMD analysis failed") from e
