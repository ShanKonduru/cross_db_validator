"""
Execution Data Persistence Manager
Handles storing and retrieving test execution data in a persistent JSON file.
This ensures historical data is preserved even if output reports are deleted.

Supports multi-level trend analysis:
- Overall execution trends
- Sheet-level trends (SMOKE, DATAVALIDATIONS, etc.)
- Category-level trends (extracted from Excel Test_Category column)
- Individual test case trends with performance metrics
"""

import os
import json
import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path


class ExecutionDataPersistence:
    """
    Manages persistent storage of comprehensive test execution data.
    Stores data in a JSON file that persists across runs and survives report deletions.
    Supports multi-level trend analysis: Overall, Sheet-level, Category-level, Individual test case.
    """
    
    def __init__(self, data_file: str = "test_execution_history.json"):
        self.data_file = data_file
        self.data_dir = "data"
        self.full_path = os.path.join(self.data_dir, data_file)
        self._ensure_data_directory()
        
    def _ensure_data_directory(self):
        """Ensure the data directory exists."""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            print(f"📁 Created data directory: {self.data_dir}")
    
    def load_execution_history(self) -> Dict:
        """Load all historical execution data from the persistent file."""
        if not os.path.exists(self.full_path):
            print(f"📄 No existing history file found at {self.full_path}")
            return {"execution_history": [], "trends_metadata": {}}
        
        try:
            with open(self.full_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                execution_count = len(data.get('execution_history', []))
                print(f"📊 Loaded {execution_count} historical execution records")
                return data
        except Exception as e:
            print(f"⚠️ Error loading execution history: {e}")
            return {"execution_history": [], "trends_metadata": {}}
    
    def save_execution_record(self, execution_record: Dict) -> bool:
        """
        Save a new execution record to the persistent file.
        Appends to existing data without overwriting.
        
        Args:
            execution_record: Comprehensive execution record from TestExecutionDataCollector
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        # Load existing data
        existing_data = self.load_execution_history()
        execution_history = existing_data.get('execution_history', [])
        
        # Get execution ID from the record
        execution_id = execution_record.get('execution_metadata', {}).get('execution_id')
        if not execution_id:
            print("⚠️ No execution_id found in execution record")
            return False
        
        # Check for duplicates
        existing_ids = {record.get('execution_metadata', {}).get('execution_id') 
                       for record in execution_history}
        if execution_id in existing_ids:
            print(f"⚠️ Execution {execution_id} already exists, skipping duplicate")
            return False
        
        # Add new execution record
        execution_history.append(execution_record)
        
        # Sort by execution time (newest last)
        execution_history.sort(key=lambda x: x.get('execution_metadata', {}).get('execution_time', ''))
        
        # Update metadata
        metadata = self._generate_metadata(execution_history)
        
        # Prepare complete data structure
        complete_data = {
            "execution_history": execution_history,
            "trends_metadata": metadata
        }
        
        # Save updated data
        try:
            with open(self.full_path, 'w', encoding='utf-8') as f:
                json.dump(complete_data, f, indent=2, ensure_ascii=False)
            print(f"💾 Saved execution record {execution_id} to {self.full_path}")
            print(f"📊 Total records in history: {len(execution_history)}")
            return True
        except Exception as e:
            print(f"❌ Error saving execution record: {e}")
            return False
    
    def _generate_metadata(self, execution_history: List[Dict]) -> Dict:
        """Generate metadata about the execution history."""
        if not execution_history:
            return {}
        
        execution_times = []
        for record in execution_history:
            exec_time_str = record.get('execution_metadata', {}).get('execution_time')
            if exec_time_str:
                try:
                    execution_times.append(datetime.datetime.fromisoformat(exec_time_str))
                except:
                    continue
        
        if not execution_times:
            return {}
        
        return {
            "data_version": "2.0",
            "last_updated": datetime.datetime.now().isoformat(),
            "total_executions": len(execution_history),
            "date_range": {
                "earliest": min(execution_times).isoformat(),
                "latest": max(execution_times).isoformat(),
                "span_days": (max(execution_times) - min(execution_times)).days
            },
            "analysis_capabilities": [
                "overall_trends", "sheet_level_trends", "category_level_trends", 
                "individual_test_trends", "performance_trends", "time_based_aggregation"
            ]
        }
    
    def get_execution_statistics(self) -> Dict:
        """Get summary statistics from all historical executions."""
        data = self.load_execution_history()
        if not data:
            return {'total_executions': 0}
        
        total_executions = len(data)
        
        # Calculate averages
        avg_total_tests = sum(record.get('total_tests', 0) for record in data) / total_executions
        avg_passed_rate = sum(record.get('passed_rate', 0) for record in data) / total_executions
        avg_failed_rate = sum(record.get('failed_rate', 0) for record in data) / total_executions
        avg_skipped_rate = sum(record.get('skipped_rate', 0) for record in data) / total_executions
        
        # Get date range
        dates = [record['execution_time'] for record in data]
        earliest = min(dates)
        latest = max(dates)
        
        return {
            'total_executions': total_executions,
            'date_range': {
                'earliest': earliest,
                'latest': latest
            },
            'averages': {
                'total_tests': round(avg_total_tests, 2),
                'passed_rate': round(avg_passed_rate, 2),
                'failed_rate': round(avg_failed_rate, 2),
                'skipped_rate': round(avg_skipped_rate, 2)
            }
        }
    
    def backup_data(self, backup_suffix: str = None) -> str:
        """Create a backup of the execution history file."""
        if not os.path.exists(self.full_path):
            return None
        
        if backup_suffix is None:
            backup_suffix = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        
        backup_filename = f"test_execution_history_backup_{backup_suffix}.json"
        backup_path = os.path.join(self.data_dir, backup_filename)
        
        try:
            import shutil
            shutil.copy2(self.full_path, backup_path)
            print(f"💾 Backup created: {backup_path}")
            return backup_path
        except Exception as e:
            print(f"❌ Error creating backup: {e}")
            return None
    
    def cleanup_old_records(self, keep_days: int = 365) -> int:
        """
        Remove execution records older than specified days.
        Returns number of records removed.
        """
        data = self.load_execution_history()
        if not data:
            return 0
        
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=keep_days)
        cutoff_iso = cutoff_date.isoformat()
        
        original_count = len(data)
        filtered_data = [record for record in data if record['execution_time'] >= cutoff_iso]
        removed_count = original_count - len(filtered_data)
        
        if removed_count > 0:
            # Save filtered data
            with open(self.full_path, 'w', encoding='utf-8') as f:
                json.dump(filtered_data, f, indent=2, ensure_ascii=False)
            print(f"🧹 Removed {removed_count} old execution records (older than {keep_days} days)")
        
        return removed_count
    
    def export_to_csv(self, csv_file: str = None) -> str:
        """Export execution history to CSV format."""
        if csv_file is None:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            csv_file = f"execution_history_export_{timestamp}.csv"
        
        data = self.load_execution_history()
        if not data:
            print("📄 No data to export")
            return None
        
        try:
            import pandas as pd
            
            # Flatten the data for CSV
            flattened_data = []
            for record in data:
                flat_record = {
                    'execution_id': record.get('execution_id', ''),
                    'execution_time': record.get('execution_time', ''),
                    'total_tests': record.get('total_tests', 0),
                    'passed_tests': record.get('passed_tests', 0),
                    'failed_tests': record.get('failed_tests', 0),
                    'skipped_tests': record.get('skipped_tests', 0),
                    'passed_rate': record.get('passed_rate', 0),
                    'failed_rate': record.get('failed_rate', 0),
                    'skipped_rate': record.get('skipped_rate', 0),
                    'categories_count': len(record.get('categories', {})),
                    'sheets_count': len(record.get('sheets', {}))
                }
                flattened_data.append(flat_record)
            
            df = pd.DataFrame(flattened_data)
            csv_path = os.path.join(self.data_dir, csv_file)
            df.to_csv(csv_path, index=False)
            print(f"📊 Exported {len(data)} records to {csv_path}")
            return csv_path
        
        except ImportError:
            print("❌ pandas not available for CSV export")
            return None
        except Exception as e:
            print(f"❌ Error exporting to CSV: {e}")
            return None