#!/usr/bin/env python3
"""
Script to update Excel test cases with intelligent column mappings
"""

import pandas as pd
import sys
from datetime import datetime

def read_current_excel():
    """Read current Excel structure"""
    try:
        df = pd.read_excel('inputs/test_suite.xlsx', sheet_name='DATAVALIDATIONS')
        print('Current DATAVALIDATIONS test cases:')
        print('=' * 60)
        
        # Filter COL_COL_VALIDATION tests
        col_tests = df[df['Test_Category'] == 'COL_COL_VALIDATION']
        
        for idx, row in col_tests.iterrows():
            print(f'Test ID: {row["Test_Case_ID"]}')
            print(f'Name: {row["Test_Case_Name"]}')
            print(f'Current Parameters: {row["Parameters"]}')
            print()
            
        return df, col_tests
        
    except Exception as e:
        print(f'Error reading Excel: {e}')
        return None, None

def create_column_mappings():
    """Create intelligent column mappings based on schema analysis"""
    
    mappings = {
        'DVAL_007': {
            'table_pair': 'products/new_products',
            'mappings': 'cost_price=price,description=product_description,category=category_id,created_date=created_at,updated_date=last_updated',
            'exclusions': 'created_date,updated_date,created_at,last_updated'
        },
        'DVAL_008': {
            'table_pair': 'employees/new_employees', 
            'mappings': 'status=is_active,created_date=created_at',
            'exclusions': 'created_date,created_at'
        },
        'DVAL_009': {
            'table_pair': 'orders/new_orders',
            'mappings': 'total_amount=order_total,shipping_cost=freight,created_date=created_at',
            'exclusions': 'created_date,created_at'
        }
    }
    
    return mappings

def update_excel_with_mappings():
    """Update Excel file with intelligent column mappings"""
    
    df, col_tests = read_current_excel()
    if df is None:
        return
    
    mappings = create_column_mappings()
    
    print('Updating Excel with intelligent column mappings...')
    print('=' * 60)
    
    # Update each COL_COL_VALIDATION test case
    for idx, row in df.iterrows():
        test_id = row['Test_Case_ID']
        
        if test_id in mappings:
            mapping_info = mappings[test_id]
            
            # Create enhanced parameters
            current_params = str(row['Parameters']) if pd.notna(row['Parameters']) else ''
            
            # Build new parameters - use semicolon format
            new_params_parts = []
            
            # Keep existing parameters first (they use semicolons)
            if current_params and current_params != 'nan':
                new_params_parts.append(current_params)
            
            # Add column mappings (use semicolon)
            new_params_parts.append(f"column_mappings={mapping_info['mappings']}")
            
            # Add exclusions if specified (use semicolon)
            if mapping_info['exclusions']:
                new_params_parts.append(f"exclude_columns={mapping_info['exclusions']}")
            
            new_parameters = ';'.join(new_params_parts)
            
            # Update the DataFrame
            df.at[idx, 'Parameters'] = new_parameters
            
            print(f'✅ Updated {test_id} ({mapping_info["table_pair"]}):')
            print(f'   New Parameters: {new_parameters}')
            print()
    
    # Save updated Excel file
    backup_filename = f'inputs/test_suite_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    
    try:
        # Create backup
        original_df = pd.read_excel('inputs/test_suite.xlsx', sheet_name=None)
        with pd.ExcelWriter(backup_filename, engine='openpyxl') as writer:
            for sheet_name, sheet_df in original_df.items():
                sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)
        print(f'📄 Backup created: {backup_filename}')
        
        # Save updated file
        with pd.ExcelWriter('inputs/test_suite.xlsx', engine='openpyxl') as writer:
            # Write DATAVALIDATIONS sheet with updates
            df.to_excel(writer, sheet_name='DATAVALIDATIONS', index=False)
            
            # Copy other sheets unchanged
            for sheet_name, sheet_df in original_df.items():
                if sheet_name != 'DATAVALIDATIONS':
                    sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        print('✅ Excel file updated successfully!')
        print(f'📁 Updated file: inputs/test_suite.xlsx')
        
    except Exception as e:
        print(f'❌ Error saving Excel file: {e}')

if __name__ == '__main__':
    print('🔄 Excel Column Mapping Update Tool')
    print('=' * 60)
    update_excel_with_mappings()