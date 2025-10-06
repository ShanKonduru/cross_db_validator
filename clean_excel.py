#!/usr/bin/env python3
"""
Clean Excel file and add proper column mappings
"""

import pandas as pd
from datetime import datetime

def clean_and_update_excel():
    """Clean parameters and add proper column mappings"""
    
    try:
        df = pd.read_excel('inputs/test_suite.xlsx', sheet_name='DATAVALIDATIONS')
        
        # Clean parameter mappings for COL_COL_VALIDATION tests
        clean_mappings = {
            'DVAL_007': {
                'base_params': 'source_table=public.products;target_table=public.new_products;tolerance_numeric=0.001;sample_size=100',
                'column_mappings': 'cost_price=price,description=product_description,category=category_id,created_date=created_at,updated_date=last_updated',
                'exclude_columns': 'created_date,updated_date,created_at,last_updated'
            },
            'DVAL_008': {
                'base_params': 'source_table=public.employees;target_table=public.new_employees;tolerance_numeric=0.001;sample_size=100',
                'column_mappings': 'status=is_active,created_date=created_at',
                'exclude_columns': 'created_date,created_at'
            },
            'DVAL_009': {
                'base_params': 'source_table=public.orders;target_table=public.new_orders;tolerance_numeric=0.001;sample_size=100',
                'column_mappings': 'total_amount=order_total,shipping_cost=freight,created_date=created_at',
                'exclude_columns': 'created_date,created_at'
            }
        }
        
        print('🔄 Cleaning and updating Excel with proper column mappings...')
        print('=' * 70)
        
        # Update each test case with clean parameters
        for idx, row in df.iterrows():
            test_id = row['Test_Case_ID']
            
            if test_id in clean_mappings:
                mapping_info = clean_mappings[test_id]
                
                # Build clean parameters with semicolon separation
                params_list = [
                    mapping_info['base_params'],
                    f"column_mappings={mapping_info['column_mappings']}",
                    f"exclude_columns={mapping_info['exclude_columns']}"
                ]
                
                clean_parameters = ';'.join(params_list)
                
                # Update the DataFrame
                df.at[idx, 'Parameters'] = clean_parameters
                
                print(f'✅ Cleaned {test_id}:')
                print(f'   Parameters: {clean_parameters}')
                print()
        
        # Save the cleaned file
        backup_filename = f'inputs/test_suite_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        
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
        
        print('✅ Excel file cleaned and updated successfully!')
        
    except Exception as e:
        print(f'❌ Error updating Excel: {e}')

if __name__ == '__main__':
    clean_and_update_excel()