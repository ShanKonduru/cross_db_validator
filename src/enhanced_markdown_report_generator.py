import os
import datetime
from typing import Dict, List, Any


class EnhancedMarkdownReportGenerator:
    """
    An enhanced Markdown report generator with better formatting, tables, and visual elements.
    """

    def __init__(self, title="Test Execution Report", output_file="report.md"):
        self.title = title
        self.output_file = output_file
        self.test_results = []
        self.summary_stats = {"total": 0, "passed": 0, "failed": 0, "skipped": 0}
        self.sheets_data = {}

    def add_test_result(
        self,
        sheet_name: str,
        test_case_id: str,
        test_case_name: str,
        status: str,
        category: str = "",
        execution_time: str = "",
        error_message: str = "",
    ):
        """Add a test result to the report."""
        test_result = {
            "sheet_name": sheet_name,
            "test_case_id": test_case_id,
            "test_case_name": test_case_name,
            "status": status.upper(),
            "category": category,
            "execution_time": execution_time,
            "error_message": error_message,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        self.test_results.append(test_result)

        # Update summary stats
        self.summary_stats["total"] += 1
        if status.upper() == "PASSED":
            self.summary_stats["passed"] += 1
        elif status.upper() == "FAILED":
            self.summary_stats["failed"] += 1
        elif status.upper().startswith("SKIPPED"):
            self.summary_stats["skipped"] += 1

        # Group by sheet
        if sheet_name not in self.sheets_data:
            self.sheets_data[sheet_name] = []
        self.sheets_data[sheet_name].append(test_result)

    def _get_status_emoji(self, status: str) -> str:
        """Return emoji for status."""
        emoji_map = {"PASSED": "✅", "FAILED": "❌", "SKIPPED": "⏭️"}
        return emoji_map.get(status.upper(), "❓")

    def _get_status_badge(self, status: str) -> str:
        """Return status badge with emoji."""
        emoji = self._get_status_emoji(status)
        return f"{emoji} **{status.upper()}**"

    def _generate_progress_bar(
        self, passed: int, failed: int, skipped: int, total: int, width: int = 50
    ) -> str:
        """Generate ASCII progress bar."""
        if total == 0:
            return "No tests executed"

        passed_blocks = int((passed / total) * width)
        failed_blocks = int((failed / total) * width)
        skipped_blocks = int((skipped / total) * width)
        remaining = width - (passed_blocks + failed_blocks + skipped_blocks)

        progress = (
            "🟢" * passed_blocks
            + "🔴" * failed_blocks
            + "🟡" * skipped_blocks
            + "⚪" * remaining
        )

        return f"`{progress}`"

    def _generate_summary_table(self) -> str:
        """Generate summary statistics table."""
        total = self.summary_stats["total"]
        if total == 0:
            return "No test results to display."

        passed_pct = (self.summary_stats["passed"] / total) * 100
        failed_pct = (self.summary_stats["failed"] / total) * 100
        skipped_pct = (self.summary_stats["skipped"] / total) * 100

        return f"""
| Status | Count | Percentage | Visual |
|--------|-------|------------|---------|
| ✅ **Passed** | {self.summary_stats['passed']} | {passed_pct:.1f}% | {self._generate_progress_bar(self.summary_stats['passed'], 0, 0, total, 20)} |
| ❌ **Failed** | {self.summary_stats['failed']} | {failed_pct:.1f}% | {self._generate_progress_bar(0, self.summary_stats['failed'], 0, total, 20)} |
| ⏭️ **Skipped** | {self.summary_stats['skipped']} | {skipped_pct:.1f}% | {self._generate_progress_bar(0, 0, self.summary_stats['skipped'], total, 20)} |
| 📊 **Total** | {total} | 100.0% | {self._generate_progress_bar(self.summary_stats['passed'], self.summary_stats['failed'], self.summary_stats['skipped'], total, 20)} |
"""

    def _generate_category_breakdown(self) -> str:
        """Generate category breakdown table."""
        category_stats = {}
        for result in self.test_results:
            category = result["category"] or "Unknown"
            if category not in category_stats:
                category_stats[category] = {
                    "passed": 0,
                    "failed": 0,
                    "skipped": 0,
                    "total": 0,
                }

            status = (
                result["status"].split(":")[0].lower()
            )  # Extract status before any colon
            category_stats[category][status] += 1
            category_stats[category]["total"] += 1

        if not category_stats:
            return "No category data available."

        table = """
| Category | ✅ Passed | ❌ Failed | ⏭️ Skipped | 📊 Total | Success Rate |
|----------|-----------|-----------|------------|----------|--------------|
"""

        for category, stats in sorted(category_stats.items()):
            # Calculate success rate excluding skipped tests
            executed_tests = stats["passed"] + stats["failed"]
            if executed_tests > 0:
                success_rate = stats["passed"] / executed_tests * 100
                success_rate_text = f"{success_rate:.1f}%"
            else:
                success_rate_text = "N/A"
            table += f"| **{category}** | {stats['passed']} | {stats['failed']} | {stats['skipped']} | {stats['total']} | {success_rate_text} |\n"

        return table

    def _generate_sheet_summary(self) -> str:
        """Generate per-sheet summary."""
        if not self.sheets_data:
            return "No sheet data available."

        summary = ""
        for sheet_name, tests in self.sheets_data.items():
            sheet_passed = sum(1 for test in tests if test["status"] == "PASSED")
            sheet_failed = sum(1 for test in tests if test["status"] == "FAILED")
            sheet_skipped = sum(
                1 for test in tests if test["status"].upper().startswith("SKIPPED")
            )
            sheet_total = len(tests)

            # Calculate success rate excluding skipped tests
            sheet_executed = sheet_passed + sheet_failed
            if sheet_executed > 0:
                success_rate = sheet_passed / sheet_executed * 100
                success_rate_text = f"{success_rate:.1f}%"
            else:
                success_rate_text = "N/A"

            summary += f"""
### 📋 {sheet_name}

**Summary:** {sheet_total} tests | ✅ {sheet_passed} passed | ❌ {sheet_failed} failed | ⏭️ {sheet_skipped} skipped | Success Rate: **{success_rate_text}**

{self._generate_progress_bar(sheet_passed, sheet_failed, sheet_skipped, sheet_total, 40)}

| Test ID | Test Case | Category | Status | Timestamp |
|---------|-----------|----------|---------|-----------|
"""

            for test in tests:
                status_badge = self._get_status_badge(test["status"])
                category_badge = f"`{test['category']}`" if test["category"] else "N/A"
                summary += f"| `{test['test_case_id']}` | {test['test_case_name']} | {category_badge} | {status_badge} | `{test['timestamp']}` |\n"

            summary += "\n---\n"

        return summary

    def generate_markdown(self) -> str:
        """Generate the complete enhanced Markdown report."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        total = self.summary_stats["total"]
        # Calculate success rate excluding skipped tests (passed / (passed + failed))
        executed_tests = self.summary_stats["passed"] + self.summary_stats["failed"]
        if executed_tests > 0:
            passed_pct = self.summary_stats["passed"] / executed_tests * 100
            success_rate_text = f"{passed_pct:.1f}%"
            execution_status = (
                "🟢 HEALTHY"
                if passed_pct >= 80
                else "🟡 ATTENTION NEEDED" if passed_pct >= 60 else "🔴 CRITICAL"
            )
        else:
            # All tests were skipped - no actual execution to evaluate
            passed_pct = 0  # For visual progress bar
            success_rate_text = "N/A (All tests skipped)"
            execution_status = "⚪ NO EXECUTION"

        # Header with better styling
        markdown_content = f"""# 🚀 {self.title}

> **Generated on:** {timestamp} | **Framework:** Cross Database Validator

---

## 📊 Executive Summary

{self._generate_summary_table()}

### 🎯 Overall Performance
- **Success Rate:** {success_rate_text}
- **Total Test Cases:** {total}
- **Execution Status:** {execution_status}

{self._generate_progress_bar(self.summary_stats['passed'], self.summary_stats['failed'], self.summary_stats['skipped'], total, 50)}

---

## 📈 Category Breakdown

{self._generate_category_breakdown()}

---

## 📝 Detailed Test Results

{self._generate_sheet_summary()}

---

## 🔍 Quick Stats

- 🎯 **Best Performing Category:** {self._get_best_category()}
- ⚠️ **Categories Needing Attention:** {self._get_failing_categories()}
- ⏱️ **Report Generated:** {timestamp}
- 🏷️ **Report Version:** Enhanced Markdown v2.0

---

## 📋 Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Test Passed Successfully |
| ❌ | Test Failed |
| ⏭️ | Test Skipped |
| 🟢 | Passed Test Block |
| 🔴 | Failed Test Block |
| 🟡 | Skipped Test Block |
| ⚪ | Empty/Remaining Block |

---

*This report was automatically generated by the Cross Database Validator framework.*
"""

        return markdown_content

    def _get_best_category(self) -> str:
        """Get the best performing category."""
        category_stats = {}
        for result in self.test_results:
            category = result["category"] or "Unknown"
            if category not in category_stats:
                category_stats[category] = {"passed": 0, "total": 0}

            if result["status"] == "PASSED":
                category_stats[category]["passed"] += 1
            category_stats[category]["total"] += 1

        best_category = "None"
        best_rate = 0

        for category, stats in category_stats.items():
            if stats["total"] > 0:
                rate = (stats["passed"] / stats["total"]) * 100
                if rate > best_rate:
                    best_rate = rate
                    best_category = category

        return (
            f"{best_category} ({best_rate:.1f}%)" if best_category != "None" else "None"
        )

    def _get_failing_categories(self) -> str:
        """Get categories with failures."""
        category_stats = {}
        for result in self.test_results:
            category = result["category"] or "Unknown"
            if category not in category_stats:
                category_stats[category] = {"failed": 0, "total": 0}

            if result["status"] == "FAILED":
                category_stats[category]["failed"] += 1
            category_stats[category]["total"] += 1

        failing_categories = []
        for category, stats in category_stats.items():
            if stats["failed"] > 0:
                fail_rate = (stats["failed"] / stats["total"]) * 100
                failing_categories.append(
                    f"{category} ({stats['failed']} failures, {fail_rate:.1f}%)"
                )

        return ", ".join(failing_categories) if failing_categories else "None 🎉"

    def save(self) -> bool:
        """Save the enhanced Markdown report to file."""
        try:
            markdown_content = self.generate_markdown()
            output_path = os.path.abspath(self.output_file)

            with open(self.output_file, "w", encoding="utf-8") as f:
                f.write(markdown_content)

            print(f"🎉 Enhanced Markdown Report saved successfully to: `{output_path}`")
            return True
        except Exception as e:
            print(f"🛑 Error saving enhanced Markdown report: {e}")
            return False
