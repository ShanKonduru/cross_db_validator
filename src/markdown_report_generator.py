import os
import datetime


class MarkdownReportGenerator:
    """
    A class for incrementally building and generating a Markdown (.md) report.
    """

    def __init__(self, title="Report", output_file="report.md"):
        self.title = title
        self.output_file = output_file
        self.content = []
        self._add_header()

    def _add_header(self):
        """Adds the main title and timestamp to the start of the report."""
        self.content.append(f"# {self.title}\n")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.content.append(f"**Generated On:** {timestamp}\n")
        self.content.append("---\n")

    def add_heading(self, text, level=2):
        """Adds a markdown heading (e.g., ## or ###)."""
        if 1 <= level <= 6:
            self.content.append(f"{'#' * level} {text}\n")

    def add_paragraph(self, text):
        """Adds a paragraph of text."""
        self.content.append(f"{text}\n")

    def add_list_item(self, text, ordered=False):
        """Adds a bullet point or numbered list item."""
        prefix = "1. " if ordered else "* "
        self.content.append(f"{prefix}{text}\n")

    def add_table(self, headers, rows):
        """
        Adds a Markdown table.

        Args:
            headers (list): List of column names (strings).
            rows (list of lists): List of rows, where each row is a list of strings.
        """
        if not headers:
            return

        # Header Row
        self.content.append(f"| {' | '.join(headers)} |")

        # Separator Row (ensures alignment)
        # Using :---: for center alignment, :--- for left alignment
        alignment = [" :---: "] * len(headers)
        self.content.append(f"| {' | '.join(alignment)} |")

        # Data Rows
        for row in rows:
            # Ensure row has correct number of columns (pad with empty string if necessary)
            padded_row = row + [""] * (len(headers) - len(row))
            self.content.append(f"| {' | '.join(padded_row)} |")

        self.content.append("\n")  # Add a newline after the table for spacing

    def add_separator(self):
        """Adds a horizontal rule."""
        self.content.append("---\n")

    def save(self):
        """Writes all accumulated content to the output file."""
        output_path = os.path.abspath(self.output_file)
        try:
            with open(self.output_file, "w", encoding="utf-8") as f:
                # Join content lines, ensuring there are two newlines between block elements
                # for better readability in the source file
                f.write("\n".join(self.content))
            print(f"🎉 Report saved successfully to: `{output_path}`")
            return True
        except Exception as e:
            print(f"🛑 Error saving report to {output_path}: {e}")
            return False
