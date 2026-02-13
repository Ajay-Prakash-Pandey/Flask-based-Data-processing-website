import pandas as pd
from typing import Tuple

def clean_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    """
    Comprehensive data cleaning with detailed statistics
    Returns: cleaned dataframe and cleaning report
    """
    # Store original stats
    original_stats = {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "missing_values": {k: int(v) for k, v in df.isnull().sum().to_dict().items()},
        "duplicate_rows": int(df.duplicated().sum())
    }
    
    # Remove duplicate rows
    df_cleaned = df.drop_duplicates().copy()
    
    # Handle missing values - different strategies per column
    for col in df_cleaned.columns:
        missing_count = df_cleaned[col].isnull().sum()
        
        if missing_count > 0:
            # For numeric columns: fill with median
            if df_cleaned[col].dtype in ['int64', 'float64']:
                median_val = df_cleaned[col].median()
                df_cleaned[col].fillna(median_val, inplace=True)
            
            # For categorical columns: fill with mode
            elif df_cleaned[col].dtype == 'object':
                mode_val = df_cleaned[col].mode()
                if len(mode_val) > 0:
                    df_cleaned[col].fillna(mode_val[0], inplace=True)
                else:
                    df_cleaned[col].fillna('Unknown', inplace=True)
    
    # Remove any rows with still missing values
    df_cleaned = df_cleaned.dropna()
    
    # Remove duplicate rows again after imputation
    df_cleaned = df_cleaned.drop_duplicates()
    
    # Store cleaning stats
    cleaning_report = {
        "original": original_stats,
        "cleaned": {
            "rows": int(len(df_cleaned)),
            "columns": int(len(df_cleaned.columns)),
            "rows_removed": int(original_stats["rows"] - len(df_cleaned)),
            "missing_values_filled": int(sum(original_stats["missing_values"].values())),
            "duplicate_rows_removed": int(original_stats["duplicate_rows"])
        }
    }
    
    return df_cleaned, cleaning_report
