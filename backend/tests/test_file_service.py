import unittest
from unittest.mock import patch, mock_open
from app.services import file_service
from app.core.config import settings
from app.models.file import FileData, FileNode, FileEdge, FilePath

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

    @patch('app.services.file_service.get_file_content')
    def test_get_file_content_file_not_found(self, mock_get_file_content):
        mock_get_file_content.side_effect = FileNotFoundError("Test file not found")
        with self.assertRaises(FileNotFoundError):
            file_service.get_file_content("non_existent_file.py")

    @patch('app.services.file_service.get_file_content')
    def test_get_file_content_permission_error(self, mock_get_file_content):
        mock_get_file_content.side_effect = PermissionError("Test permission error")
        with self.assertRaises(PermissionError):
            file_service.get_file_content("restricted_file.py")

    @patch('app.services.file_service.get_file_content')
    def test_get_file_content_general_exception(self, mock_get_file_content):
        mock_get_file_content.side_effect = Exception("Test general exception")
        with self.assertRaises(Exception):
            file_service.get_file_content("some_file.py")

if __name__ == '__main__':
    unittest.main()
