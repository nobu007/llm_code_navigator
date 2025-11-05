import unittest
from pydantic import ValidationError
from app.models.file import FileNode, FileEdge, FileData, FileContent, FilePath
from app.models.pmd import PmdViolation, PmdResult


class TestFileModels(unittest.TestCase):
    """Test cases for file-related Pydantic models."""

    def test_file_node_valid(self):
        """Test FileNode with valid data."""
        node = FileNode(id="test_id", name="test.py", type="file")
        self.assertEqual(node.id, "test_id")
        self.assertEqual(node.name, "test.py")
        self.assertEqual(node.type, "file")
        self.assertIsNone(node.children)

    def test_file_node_with_children(self):
        """Test FileNode with children."""
        child = FileNode(id="child_id", name="child.py", type="file")
        parent = FileNode(id="parent_id", name="parent_dir", type="directory", children=[child])
        self.assertEqual(len(parent.children), 1)
        self.assertEqual(parent.children[0].id, "child_id")

    def test_file_node_invalid_type(self):
        """Test FileNode with invalid type."""
        with self.assertRaises(ValidationError):
            FileNode(id="test_id", name="test.py", type="invalid_type")

    def test_file_node_empty_id(self):
        """Test FileNode with empty ID."""
        with self.assertRaises(ValidationError):
            FileNode(id="", name="test.py", type="file")

    def test_file_node_empty_name(self):
        """Test FileNode with empty name."""
        with self.assertRaises(ValidationError):
            FileNode(id="test_id", name="", type="file")

    def test_file_edge_valid(self):
        """Test FileEdge with valid data."""
        edge = FileEdge(source="source_id", target="target_id")
        self.assertEqual(edge.source, "source_id")
        self.assertEqual(edge.target, "target_id")

    def test_file_edge_empty_source(self):
        """Test FileEdge with empty source."""
        with self.assertRaises(ValidationError):
            FileEdge(source="", target="target_id")

    def test_file_edge_empty_target(self):
        """Test FileEdge with empty target."""
        with self.assertRaises(ValidationError):
            FileEdge(source="source_id", target="")

    def test_file_data_valid(self):
        """Test FileData with valid data."""
        node = FileNode(id="test_id", name="test.py", type="file")
        edge = FileEdge(source="source_id", target="target_id")
        data = FileData(files=[node], relationships=[edge])
        self.assertEqual(len(data.files), 1)
        self.assertEqual(len(data.relationships), 1)

    def test_file_content_valid(self):
        """Test FileContent with valid data."""
        content = FileContent(content="print('hello')", path="/test/path.py")
        self.assertEqual(content.content, "print('hello')")
        self.assertEqual(content.path, "/test/path.py")
        self.assertEqual(content.encoding, "utf-8")  # default value

    def test_file_content_custom_encoding(self):
        """Test FileContent with custom encoding."""
        content = FileContent(content="test", path="/test/path.py", encoding="latin-1")
        self.assertEqual(content.encoding, "latin-1")

    def test_file_content_empty_path(self):
        """Test FileContent with empty path."""
        with self.assertRaises(ValidationError):
            FileContent(content="test", path="")

    def test_file_path_valid(self):
        """Test FilePath with valid data."""
        path = FilePath(full="/full/path", base="/base", relative="path")
        self.assertEqual(path.full, "/full/path")
        self.assertEqual(path.base, "/base")
        self.assertEqual(path.relative, "path")

    def test_file_path_empty_values(self):
        """Test FilePath with empty values."""
        with self.assertRaises(ValidationError):
            FilePath(full="", base="/base", relative="path")


class TestPmdModels(unittest.TestCase):
    """Test cases for PMD-related Pydantic models."""

    def test_pmd_violation_valid(self):
        """Test PmdViolation with valid data."""
        violation = PmdViolation(
            rule="TestRule",
            priority=3,
            message="Test violation message",
            line=10,
            column=5
        )
        self.assertEqual(violation.rule, "TestRule")
        self.assertEqual(violation.priority, 3)
        self.assertEqual(violation.message, "Test violation message")
        self.assertEqual(violation.line, 10)
        self.assertEqual(violation.column, 5)

    def test_pmd_violation_invalid_priority(self):
        """Test PmdViolation with invalid priority."""
        with self.assertRaises(ValidationError):
            PmdViolation(
                rule="TestRule",
                priority=6,  # Invalid: must be 1-5
                message="Test message",
                line=10,
                column=5
            )

    def test_pmd_violation_negative_line(self):
        """Test PmdViolation with negative line number."""
        with self.assertRaises(ValidationError):
            PmdViolation(
                rule="TestRule",
                priority=3,
                message="Test message",
                line=-1,  # Invalid: must be non-negative
                column=5
            )

    def test_pmd_violation_empty_rule(self):
        """Test PmdViolation with empty rule."""
        with self.assertRaises(ValidationError):
            PmdViolation(
                rule="",  # Invalid: cannot be empty
                priority=3,
                message="Test message",
                line=10,
                column=5
            )

    def test_pmd_result_valid(self):
        """Test PmdResult with valid data."""
        violation = PmdViolation(
            rule="TestRule",
            priority=3,
            message="Test message",
            line=10,
            column=5
        )
        result = PmdResult(
            violations=[violation],
            summary={"totalViolations": 1, "fileAnalyzed": "test.py"}
        )
        self.assertEqual(len(result.violations), 1)
        self.assertEqual(result.summary["totalViolations"], 1)

    def test_pmd_result_empty_violations(self):
        """Test PmdResult with empty violations list."""
        result = PmdResult(
            violations=[],
            summary={"totalViolations": 0}
        )
        self.assertEqual(len(result.violations), 0)

    def test_pmd_result_invalid_summary(self):
        """Test PmdResult with invalid summary."""
        with self.assertRaises(ValidationError):
            PmdResult(
                violations=[],
                summary="not a dict"  # Invalid: must be dict
            )

    def test_file_node_recursive_children(self):
        """Test FileNode with deeply nested children."""
        grandchild = FileNode(id="gc_id", name="grandchild.py", type="file")
        child = FileNode(id="c_id", name="child_dir", type="directory", children=[grandchild])
        parent = FileNode(id="p_id", name="parent_dir", type="directory", children=[child])
        
        self.assertEqual(len(parent.children), 1)
        self.assertEqual(len(parent.children[0].children), 1)
        self.assertEqual(parent.children[0].children[0].id, "gc_id")

    def test_file_node_whitespace_handling(self):
        """Test FileNode handles whitespace in id and name."""
        node = FileNode(id="  test_id  ", name="  test.py  ", type="file")
        self.assertEqual(node.id, "test_id")
        self.assertEqual(node.name, "test.py")

    def test_file_edge_whitespace_handling(self):
        """Test FileEdge handles whitespace in source and target."""
        edge = FileEdge(source="  source_id  ", target="  target_id  ")
        self.assertEqual(edge.source, "source_id")
        self.assertEqual(edge.target, "target_id")

    def test_file_content_whitespace_path(self):
        """Test FileContent handles whitespace in path."""
        content = FileContent(content="test", path="  /test/path.py  ")
        self.assertEqual(content.path, "/test/path.py")

    def test_file_path_whitespace_handling(self):
        """Test FilePath handles whitespace in all fields."""
        path = FilePath(
            full="  /full/path  ",
            base="  /base  ",
            relative="  path  "
        )
        self.assertEqual(path.full, "/full/path")
        self.assertEqual(path.base, "/base")
        self.assertEqual(path.relative, "path")

    def test_pmd_violation_whitespace_handling(self):
        """Test PmdViolation handles whitespace in rule and message."""
        violation = PmdViolation(
            rule="  TestRule  ",
            priority=3,
            message="  Test violation message  ",
            line=10,
            column=5
        )
        self.assertEqual(violation.rule, "TestRule")
        self.assertEqual(violation.message, "Test violation message")

    def test_pmd_violation_boundary_values(self):
        """Test PmdViolation with boundary priority values."""
        # Test minimum priority
        violation_min = PmdViolation(
            rule="TestRule",
            priority=1,
            message="Test message",
            line=0,
            column=0
        )
        self.assertEqual(violation_min.priority, 1)
        self.assertEqual(violation_min.line, 0)
        self.assertEqual(violation_min.column, 0)
        
        # Test maximum priority
        violation_max = PmdViolation(
            rule="TestRule",
            priority=5,
            message="Test message",
            line=1000,
            column=100
        )
        self.assertEqual(violation_max.priority, 5)

    def test_pmd_violation_invalid_boundary_values(self):
        """Test PmdViolation with invalid boundary values."""
        # Test priority too low
        with self.assertRaises(ValidationError):
            PmdViolation(
                rule="TestRule",
                priority=0,
                message="Test message",
                line=10,
                column=5
            )
        
        # Test priority too high
        with self.assertRaises(ValidationError):
            PmdViolation(
                rule="TestRule",
                priority=6,
                message="Test message",
                line=10,
                column=5
            )

    def test_file_data_empty_lists(self):
        """Test FileData with empty files and relationships lists."""
        data = FileData(files=[], relationships=[])
        self.assertEqual(len(data.files), 0)
        self.assertEqual(len(data.relationships), 0)

    def test_pmd_result_complex_summary(self):
        """Test PmdResult with complex summary dictionary."""
        complex_summary = {
            "totalViolations": 5,
            "fileAnalyzed": "test.py",
            "rulesets": ["java-quickstart"],
            "executionTime": "0.5s",
            "metadata": {
                "version": "6.55.0",
                "timestamp": "2023-01-01T00:00:00Z"
            }
        }
        
        result = PmdResult(violations=[], summary=complex_summary)
        self.assertEqual(result.summary["totalViolations"], 5)
        self.assertEqual(result.summary["metadata"]["version"], "6.55.0")


if __name__ == '__main__':
    unittest.main()