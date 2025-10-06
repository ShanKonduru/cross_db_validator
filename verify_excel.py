#!/usr/bin/env python3
"""
Verify Excel file updates
"""

import pandas as pd

def verify_updates():
    """Verify the Excel file was updated correctly"""
    
    try:
        df = pd.read_excel('inputs/test_suite.xlsx', sheet_name='DATAVALIDATIONS')
        
        # Filter COL_COL_VALIDATION tests
        col_tests = df[df['Test_Category'] == 'COL_COL_VALIDATION']
        
        print('✅ Updated COL_COL_VALIDATION Tests:')
        print('=' * 80)
        
        for idx, row in col_tests.iterrows():
            print(f'🔍 {row["Test_Case_ID"]} - {row["Test_Case_Name"]}')
            print(f'Parameters: {row["Parameters"]}')
            print()
            
    except Exception as e:
        print(f'❌ Error verifying Excel: {e}')

if __name__ == '__main__':
    verify_updates()