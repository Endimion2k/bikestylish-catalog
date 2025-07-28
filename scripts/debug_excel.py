#!/usr/bin/env python3
"""
Debug Excel File Structure
"""

import pandas as pd

def debug_excel_structure():
    """Debug what's in the Excel file"""
    
    try:
        # Load the Excel file
        df = pd.read_excel('../sxt26.xls')
        
        print(f"📊 Excel file structure:")
        print(f"   Shape: {df.shape}")
        print(f"   Columns: {list(df.columns)}")
        
        print(f"\n📋 First 5 rows:")
        for i, row in df.head().iterrows():
            print(f"   Row {i}: {dict(row)}")
        
        print(f"\n🔍 Sample data from each column:")
        for col in df.columns:
            sample_values = df[col].dropna().head(3).tolist()
            print(f"   {col}: {sample_values}")
            
    except Exception as e:
        print(f"❌ Error loading Excel: {e}")

if __name__ == "__main__":
    debug_excel_structure()
