import unittest
from unittest.mock import patch, MagicMock
import subprocess
from app.services.pmd_service import run_pmd_analysis
from app.models.pmd import PmdResult, PmdViolation


class TestPmdService(unittest.TestCase):

    @patch('app.services.pmd_service.subprocess.run')
    def test_run_pmd_analysis_success_no_violations(self, mock_run):
        mock_pmd_output = {
            "formatVersion": "0",
            "pmdVersion": "6.55.0",
            "timestamp": "2023-01-01T00:00:00.000Z",
            "files": []
        }
        mock_run.return_value = MagicMock(stdout=f'{mock_pmd_output}'.replace("'", '"'))
        
        result = run_pmd_analysis('some/path')
        
        self.assertIsInstance(result, PmdResult)
        self.assertEqual(len(result.violations), 0)
        self.assertEqual(result.summary["totalViolations"], 0)
        self.assertEqual(result.summary["fileAnalyzed"], "some/path")
        self.assertEqual(result.summary["pmdVersion"], "6.55.0")

    @patch('app.services.pmd_service.subprocess.run')
    def test_run_pmd_analysis_success_with_violations(self, mock_run):
        mock_pmd_output = {
            "formatVersion": "0",
            "pmdVersion": "6.55.0",
            "timestamp": "2023-01-01T00:00:00.000Z",
            "files": [
                {
                    "filename": "test.java",
                    "violations": [
                        {
                            "beginline": 10,
                            "begincolumn": 5,
                            "endline": 10,
                            "endcolumn": 15,
                            "description": "Test violation",
                            "rule": "TestRule",
                            "ruleset": "TestRuleset",
                            "priority": 3
                        }
                    ]
                }
            ]
        }
        mock_run.return_value = MagicMock(stdout=f'{mock_pmd_output}'.replace("'", '"'))
        
        result = run_pmd_analysis('some/path')
        
        self.assertIsInstance(result, PmdResult)
        self.assertEqual(len(result.violations), 1)
        self.assertEqual(result.summary["totalViolations"], 1)
        
        violation = result.violations[0]
        self.assertEqual(violation.rule, "TestRule")
        self.assertEqual(violation.priority, 3)
        self.assertEqual(violation.message, "Test violation")
        self.assertEqual(violation.line, 10)
        self.assertEqual(violation.column, 5)

    @patch('app.services.pmd_service.subprocess.run')
    def test_run_pmd_analysis_failure(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, 'pmd', stderr='error')
        with self.assertRaises(RuntimeError):
            run_pmd_analysis('some/path')

    @patch('app.services.pmd_service.subprocess.run')
    def test_run_pmd_analysis_file_not_found(self, mock_run):
        mock_run.side_effect = FileNotFoundError()
        with self.assertRaises(RuntimeError) as context:
            run_pmd_analysis('some/path')
        self.assertIn("PMD command not found", str(context.exception))


if __name__ == '__main__':
    unittest.main()
