import unittest
from unittest.mock import patch, mock_open
from app.services import file_service
from app.core.config import settings
from app.models.file import FileData, FileNode, FileEdge, FilePath, FileContent

class TestFileService(unittest.TestCase):

    @patch('app.services.file_service.get_files_info')
    def test_get_file_data_file_not_found(self, mock_get_files_info):
        mock_get_files_info.side_effect = FileNotFoundError("Test file not found")
        with self.assertRaises(FileNotFoundError):
            file_service.get_file_data()

    @patch('app.services.file_service.get_files_info')
    def test_get_file_data_permission_error(self, mock_get_files_info):
        mock_get_files_info.side_effect = PermissionError("Test permission error")
        with self.assertRaises(PermissionError):
            file_service.get_file_data()

    @patch('app.services.file_service.get_files_info')
    def test_get_file_data_general_exception(self, mock_get_files_info):
        mock_get_files_info.side_effect = Exception("Test general exception")
        with self.assertRaises(Exception):
            file_service.get_file_data()

    @patch('builtins.open', new_callable=mock_open, read_data='')
    @patch('pathlib.Path.exists', return_value=True)
    @patch('app.services.file_service.logger')
    @patch('app.services.file_service.get_python_file_path_list')
    def test_get_files_info_logging(self, mock_get_python_file_path_list, mock_logger, mock_exists, mock_file):
        mock_get_python_file_path_list.return_value = [
            FilePath(full="test.py", base=".", relative="test.py")
        ]
        file_service.get_files_info()
        mock_logger.info.assert_called_with('File node list: [FileNode(id=\'0_test.py\', name=\'test.py\', type=\'file\', children=[])]')

    @patch('app.services.file_service.logger')
    @patch('app.services.file_service.get_python_file_path_list')
    def test_get_files_info_logging_error(self, mock_get_python_file_path_list, mock_logger):
        mock_get_python_file_path_list.side_effect = Exception("Test error")
        with self.assertRaises(Exception):
            file_service.get_files_info()
        mock_logger.error.assert_called_with('Error getting files: Test error')

    @patch('builtins.open', new_callable=mock_open, read_data='import imported_module')
    @patch('pathlib.Path.exists', return_value=True)
    @patch('app.services.file_service.get_python_file_path_list')
    def test_get_file_info_children(self, mock_get_python_file_path_list, mock_exists, mock_file):
        mock_get_python_file_path_list.return_value = [
            FilePath(full="test.py", base=".", relative="test.py"),
            FilePath(full="imported/module.py", base=".", relative="imported/module.py")
        ]
        file_info = file_service.get_files_info()
        self.assertIsInstance(file_info[0].children, list)
        self.assertIsInstance(file_info[0].children[0], FileNode)

    @patch('os.path.exists', return_value=False)
    def test_get_file_content_file_not_found(self, mock_exists):
        # Mock the path validation to pass, then test file not found
        with patch('app.services.file_service._validate_file_path', return_value='/app/work/non_existent_file.py'):
            with self.assertRaises(FileNotFoundError):
                file_service.get_file_content("non_existent_file.py")

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isfile', return_value=True)
    @patch('os.path.getsize', return_value=1000)
    def test_get_file_content_path_outside_backend_dir(self, mock_getsize, mock_isfile, mock_exists):
        with self.assertRaises(PermissionError):
            file_service.get_file_content("/etc/passwd")

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isfile', return_value=True)
    @patch('os.path.getsize', return_value=1000)
    @patch('builtins.open', new_callable=mock_open, read_data='print("Hello World")')
    def test_get_file_content_success(self, mock_file, mock_getsize, mock_isfile, mock_exists):
        # Mock the path validation to pass
        with patch('app.services.file_service._validate_file_path', return_value='/app/work/test.py'):
            result = file_service.get_file_content("test.py")
            self.assertIsInstance(result, file_service.FileContent)
            self.assertEqual(result.content, 'print("Hello World")')
            self.assertEqual(result.encoding, 'utf-8')

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isfile', return_value=True)
    @patch('os.path.getsize', return_value=settings.MAX_FILE_SIZE + 1)
    def test_get_file_content_file_too_large(self, mock_getsize, mock_isfile, mock_exists):
        with patch('app.services.file_service._validate_file_path', return_value='/app/work/large_file.py'):
            with self.assertRaises(PermissionError):
                file_service.get_file_content("large_file.py")

    def test_validate_file_path_empty_path(self):
        with self.assertRaises(PermissionError):
            file_service._validate_file_path("")

    def test_validate_file_path_suspicious_patterns(self):
        with self.assertRaises(PermissionError):
            file_service._validate_file_path("../etc/passwd")

    @patch('builtins.open', side_effect=[UnicodeDecodeError('utf-8', b'', 0, 1, 'test'), mock_open(read_data='content').return_value])
    def test_read_file_with_encoding_fallback(self, mock_file):
        content, encoding = file_service._read_file_with_encoding("test.py")
        self.assertEqual(content, 'content')
        self.assertEqual(encoding, 'utf-8-sig')

if __name__ == '__main__':
    unittest.main()
