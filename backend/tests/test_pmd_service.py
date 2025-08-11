import unittest
from unittest.mock import patch, MagicMock
import subprocess
from app.services.pmd_service import run_pmd_analysis


class TestPmdService(unittest.TestCase):

    @patch('app.services.pmd_service.subprocess.run')
    def test_run_pmd_analysis_success(self, mock_run):
        mock_run.return_value = MagicMock(stdout='{"files": []}')
        result = run_pmd_analysis('some/path')
        self.assertEqual(result, {"files": []})

    @patch('app.services.pmd_service.subprocess.run')
    def test_run_pmd_analysis_failure(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, 'pmd', stderr='error')
        with self.assertRaises(RuntimeError):
            run_pmd_analysis('some/path')


if __name__ == '__main__':
    unittest.main()
