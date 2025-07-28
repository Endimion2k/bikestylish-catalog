#!/usr/bin/env python3
"""
Convert Excel file to CSV with proper structure for BikeStylish data.
"""

import pandas as pd
import sys

def convert_excel_to_csv():
    """Convert the Excel file to CSV format with proper structure."""
    try:
        # Read Excel file
        df = pd.read_excel('../sxt26.xls')
        print(f"📊 Loaded {len(df)} rows from Excel")
        print(f"📋 Columns: {list(df.columns)}")
        
        # Create a complete structure based on the original CSV format
        # Add missing columns with default or derived values
        
        # Add missing columns with defaults
        if 'cod_produs' not in df.columns:
            df['cod_produs'] = range(100000, 100000 + len(df))  # Generate product codes
        
        if 'cod_ean' not in df.columns:
            df['cod_ean'] = ''  # Empty EAN codes
            
        if 'imag_baza' not in df.columns:
            df['imag_baza'] = ''  # Empty base images
            
        if 'in_stock' not in df.columns:
            df['in_stock'] = (df['cant_stock'] > 0).astype(int)  # 1 if stock > 0
            
        if 'pret_produs' not in df.columns:
            # Calculate purchase price as 50% of suggested price
            df['pret_produs'] = df['pret_sugerat'] * 0.5
            
        if 'categorie_id' not in df.columns:
            df['categorie_id'] = 100  # Default category ID
            
        if 'categorie_path_subcat' not in df.columns:
            df['categorie_path_subcat'] = df['nume_categorie']  # Use category name as path
            
        if 'greutate' not in df.columns:
            df['greutate'] = ''  # Empty weight
            
        if 'creat_la_data' not in df.columns:
            df['creat_la_data'] = '2024/01/01'  # Default creation date
            
        if 'imag_galerie' not in df.columns:
            df['imag_galerie'] = ''  # Empty gallery images
        
        # Reorder columns to match original CSV structure
        column_order = [
            'cod_produs', 'cod_ean', 'nume_produs', 'descriere', 'nume_categorie',
            'imag_baza', 'cant_stock', 'in_stock', 'pret_produs', 'pret_sugerat',
            'categorie_id', 'categorie_path_subcat', 'greutate', 'producator',
            'creat_la_data', 'imag_galerie'
        ]
        
        # Keep only columns that exist
        available_columns = [col for col in column_order if col in df.columns]
        df_ordered = df[available_columns]
        
        # Save to CSV with semicolon separator
        df_ordered.to_csv('../sxt26.csv', index=False, sep=';', encoding='utf-8')
        print(f"✅ Successfully converted to CSV with {len(df_ordered)} rows")
        print(f"📋 Final columns: {list(df_ordered.columns)}")
        
        # Show sample data
        print("\n📋 Sample product:")
        sample = df_ordered.iloc[0]
        for col, value in sample.items():
            print(f"   {col}: {value}")
            
    except Exception as e:
        print(f"❌ Error converting Excel to CSV: {e}")
        return False
        
    return True

if __name__ == "__main__":
    convert_excel_to_csv()
