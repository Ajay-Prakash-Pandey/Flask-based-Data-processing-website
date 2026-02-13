import pandas as pd
from typing import Dict, Any, List

def analyze_data(df: pd.DataFrame) -> Dict[str, Any]:
    """Comprehensive data analysis"""
    numeric_cols: List[str] = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_cols: List[str] = df.select_dtypes(include=['object']).columns.tolist()
    
    analysis: Dict[str, Any] = {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "columns_names": list(df.columns),
        "data_types": df.dtypes.astype(str).to_dict(),  # type: ignore
        "numeric_columns": numeric_cols,
        "categorical_columns": categorical_cols,
        "missing_count": int(df.isnull().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "memory_usage_mb": round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2)
    }
    
    return analysis
