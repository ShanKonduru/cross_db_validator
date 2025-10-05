"""
Unit tests for MarkdownReportGenerator
"""
import os
import sys
import pytest
import tempfile
from unittest.mock import patch, mock_open, MagicMock
from datetime import datetime

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.markdown_report_generator import MarkdownReportGenerator


@pytest.mark.unit
class TestMarkdownReportGenerator:
    """Test class for MarkdownReportGenerator"""

    def test_initialization_with_defaults(self):
        """Test proper initialization with default parameters"""
        with patch('src.markdown_report_generator.datetime') as mock_datetime:
            mock_datetime.datetime.now.return_value.strftime.return_value = "2025-10-05 12:00:00"
            
            generator = MarkdownReportGenerator()
            
            assert generator.title == "Report"
            assert generator.output_file == "report.md"
            assert len(generator.content) >= 3  # Header, timestamp, separator
            assert generator.content[0] == "# Report\n"
            assert "**Generated On:** 2025-10-05 12:00:00\n" in generator.content
            assert "---\n" in generator.content

    def test_initialization_with_custom_parameters(self):
        """Test initialization with custom parameters"""
        with patch('src.markdown_report_generator.datetime') as mock_datetime:
            mock_datetime.datetime.now.return_value.strftime.return_value = "2025-10-05 15:30:45"
            
            generator = MarkdownReportGenerator(
                title="Custom Test Report",
                output_file="custom_report.md"
            )
            
            assert generator.title == "Custom Test Report"
            assert generator.output_file == "custom_report.md"
            assert generator.content[0] == "# Custom Test Report\n"
            assert "**Generated On:** 2025-10-05 15:30:45\n" in generator.content

    def test_add_header(self):
        """Test adding headers with different levels"""
        generator = MarkdownReportGenerator()
        initial_content_length = len(generator.content)
        
        generator.add_heading("Level 2 Header", level=2)
        generator.add_heading("Level 3 Header", level=3)
        generator.add_heading("Level 1 Header", level=1)
        
        assert len(generator.content) == initial_content_length + 3
        assert "## Level 2 Header\n" in generator.content
        assert "### Level 3 Header\n" in generator.content
        assert "# Level 1 Header\n" in generator.content

    def test_add_heading_with_invalid_levels(self):
        """Test add_heading with invalid level values"""
        generator = MarkdownReportGenerator()
        initial_content_length = len(generator.content)
        
        # Test invalid levels (should not add anything)
        generator.add_heading("Invalid Level 0", level=0)
        generator.add_heading("Invalid Level 7", level=7)
        generator.add_heading("Invalid Level -1", level=-1)
        
        assert len(generator.content) == initial_content_length

    def test_add_paragraph(self):
        """Test adding paragraphs"""
        generator = MarkdownReportGenerator()
        initial_content_length = len(generator.content)
        
        generator.add_paragraph("This is a test paragraph.")
        generator.add_paragraph("This is another paragraph with **bold** text.")
        
        assert len(generator.content) == initial_content_length + 2
        assert "This is a test paragraph.\n" in generator.content
        assert "This is another paragraph with **bold** text.\n" in generator.content

    def test_add_list_item_unordered(self):
        """Test adding unordered list items"""
        generator = MarkdownReportGenerator()
        initial_content_length = len(generator.content)
        
        generator.add_list_item("First item")
        generator.add_list_item("Second item")
        generator.add_list_item("Third item")
        
        assert len(generator.content) == initial_content_length + 3
        assert "* First item\n" in generator.content
        assert "* Second item\n" in generator.content
        assert "* Third item\n" in generator.content

    def test_add_list_item_ordered(self):
        """Test adding ordered list items"""
        generator = MarkdownReportGenerator()
        initial_content_length = len(generator.content)
        
        generator.add_list_item("First item", ordered=True)
        generator.add_list_item("Second item", ordered=True)
        generator.add_list_item("Third item", ordered=True)
        
        assert len(generator.content) == initial_content_length + 3
        assert "1. First item\n" in generator.content
        assert "1. Second item\n" in generator.content
        assert "1. Third item\n" in generator.content

    def test_add_table_with_valid_data(self):
        """Test adding a table with valid headers and rows"""
        generator = MarkdownReportGenerator()
        initial_content_length = len(generator.content)
        
        headers = ["Name", "Age", "City"]
        rows = [
            ["Alice", "30", "New York"],
            ["Bob", "25", "Los Angeles"],
            ["Charlie", "35", "Chicago"]
        ]
        
        generator.add_table(headers, rows)
        
        # Should add header row, separator row, data rows, and blank line
        expected_additions = 1 + 1 + len(rows) + 1  # 6 lines total
        assert len(generator.content) == initial_content_length + expected_additions
        
        # Check header row
        assert "| Name | Age | City |" in generator.content
        # Check separator row
        assert "|  :---:  |  :---:  |  :---:  |" in generator.content
        # Check data rows
        assert "| Alice | 30 | New York |" in generator.content
        assert "| Bob | 25 | Los Angeles |" in generator.content

    def test_add_table_with_mismatched_columns(self):
        """Test adding table with rows that have different column counts"""
        generator = MarkdownReportGenerator()
        
        headers = ["Col1", "Col2", "Col3"]
        rows = [
            ["A", "B"],  # Missing one column
            ["X", "Y", "Z", "Extra"],  # Extra column
            ["P", "Q", "R"]  # Correct number
        ]
        
        generator.add_table(headers, rows)
        
        # Should pad missing columns with empty strings
        assert "| A | B |  |" in generator.content
        # Should include all provided columns (extra ones ignored by padding logic)
        assert "| X | Y | Z |" in generator.content
        assert "| P | Q | R |" in generator.content

    def test_add_table_with_empty_headers(self):
        """Test adding table with empty headers"""
        generator = MarkdownReportGenerator()
        initial_content_length = len(generator.content)
        
        headers = []
        rows = [["data1", "data2"]]
        
        generator.add_table(headers, rows)
        
        # Should not add anything for empty headers
        assert len(generator.content) == initial_content_length

    def test_add_separator(self):
        """Test adding separator line"""
        generator = MarkdownReportGenerator()
        initial_content_length = len(generator.content)
        
        generator.add_separator()
        
        assert len(generator.content) == initial_content_length + 1
        assert "---\n" in generator.content

    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.abspath')
    def test_save_success(self, mock_abspath, mock_file):
        """Test successful saving of report"""
        mock_abspath.return_value = "/absolute/path/to/report.md"
        
        generator = MarkdownReportGenerator(output_file="test_report.md")
        generator.add_paragraph("Test content")
        
        with patch('builtins.print') as mock_print:
            result = generator.save()
        
        assert result is True
        mock_file.assert_called_once_with("test_report.md", "w", encoding="utf-8")
        mock_print.assert_called_with("🎉 Report saved successfully to: `/absolute/path/to/report.md`")
        
        # Verify file was written with correct content
        handle = mock_file()
        written_content = ''.join(call.args[0] for call in handle.write.call_args_list)
        assert "Test content\n" in written_content

    @patch('builtins.open', side_effect=IOError("Permission denied"))
    def test_save_failure(self, mock_file):
        """Test save failure handling"""
        generator = MarkdownReportGenerator(output_file="test_report.md")
        
        with patch('builtins.print') as mock_print:
            result = generator.save()
        
        assert result is False
        mock_print.assert_called_with("🛑 Error saving report to test_report.md: Permission denied")

    @patch('builtins.open', new_callable=mock_open)
    def test_save_content_formatting(self, mock_file):
        """Test that content is properly formatted when saved"""
        generator = MarkdownReportGenerator(title="Test Report")
        generator.add_heading("Section 1", level=2)
        generator.add_paragraph("This is a paragraph.")
        generator.add_list_item("List item 1")
        generator.add_separator()
        
        generator.save()
        
        # Get the written content
        handle = mock_file()
        written_content = ''.join(call.args[0] for call in handle.write.call_args_list)
        
        # Verify content structure
        assert "# Test Report\n" in written_content
        assert "## Section 1\n" in written_content
        assert "This is a paragraph.\n" in written_content
        assert "* List item 1\n" in written_content
        assert "---\n" in written_content

    @pytest.mark.edge
    def test_add_heading_with_special_characters(self):
        """Test adding headings with special characters"""
        generator = MarkdownReportGenerator()
        
        generator.add_heading("Header with @#$%^&*() characters", level=2)
        generator.add_heading("Header with émojis 🎉✅❌", level=3)
        
        assert "## Header with @#$%^&*() characters\n" in generator.content
        assert "### Header with émojis 🎉✅❌\n" in generator.content

    @pytest.mark.edge
    def test_add_table_with_special_characters(self):
        """Test adding table with special characters in content"""
        generator = MarkdownReportGenerator()
        
        headers = ["Test Case", "Status", "Notes"]
        rows = [
            ["Test@123", "✅ PASSED", "All good!"],
            ["Test#456", "❌ FAILED", "Error: connection timeout"]
        ]
        
        generator.add_table(headers, rows)
        
        assert "| Test@123 | ✅ PASSED | All good! |" in generator.content
        assert "| Test#456 | ❌ FAILED | Error: connection timeout |" in generator.content

    @pytest.mark.integration
    def test_complete_report_generation_workflow(self):
        """Test complete workflow of report generation"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
            temp_filename = temp_file.name
        
        try:
            generator = MarkdownReportGenerator(
                title="Integration Test Report",
                output_file=temp_filename
            )
            
            # Build a complete report
            generator.add_heading("Test Summary", level=2)
            generator.add_paragraph("This is a comprehensive test report.")
            
            generator.add_heading("Test Results", level=3)
            headers = ["Test ID", "Test Name", "Status", "Duration"]
            rows = [
                ["TC001", "Login Test", "PASSED", "2.3s"],
                ["TC002", "Data Validation", "FAILED", "1.8s"],
                ["TC003", "API Test", "PASSED", "0.9s"]
            ]
            generator.add_table(headers, rows)
            
            generator.add_separator()
            generator.add_heading("Summary", level=3)
            generator.add_list_item("Total Tests: 3")
            generator.add_list_item("Passed: 2")
            generator.add_list_item("Failed: 1")
            
            # Save and verify
            result = generator.save()
            assert result is True
            
            # Verify file was actually created and contains expected content
            assert os.path.exists(temp_filename)
            with open(temp_filename, 'r', encoding='utf-8') as f:
                content = f.read()
                
            assert "# Integration Test Report" in content
            assert "## Test Summary" in content
            assert "| Test ID | Test Name | Status | Duration |" in content
            assert "TC001" in content
            assert "* Total Tests: 3" in content
            
        finally:
            # Cleanup
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    @pytest.mark.performance
    def test_large_report_generation(self):
        """Test generating a large report with many elements"""
        generator = MarkdownReportGenerator(title="Large Report")
        
        # Add many elements
        for i in range(100):
            generator.add_heading(f"Section {i}", level=2)
            generator.add_paragraph(f"This is paragraph {i} with some content.")
            generator.add_list_item(f"Item {i}")
        
        # Add large table
        headers = ["ID", "Name", "Value", "Status"]
        rows = [[f"ID{i}", f"Name{i}", f"Value{i}", "Active"] for i in range(1000)]
        generator.add_table(headers, rows)
        
        # Should handle large content without issues
        assert len(generator.content) > 3000  # Initial + 300 (100*3) + 1002 (table)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])