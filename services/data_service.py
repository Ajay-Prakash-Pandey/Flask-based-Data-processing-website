import pandas as pd  # type: ignore
from processing.cleaner import clean_data  # type: ignore
from processing.analyzer import analyze_data  # type: ignore
from database.models import UploadedDataset  # type: ignore
from database.db import db  # type: ignore
from typing import Dict, Any, Tuple, Optional, BinaryIO, Union
import io  # type: ignore
import os  # type: ignore
import numpy as np  # type: ignore
import matplotlib  # type: ignore
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt  # type: ignore
import base64  # type: ignore
import seaborn as sns  # type: ignore

def convert_to_json_serializable(obj: Any) -> Any:  # type: ignore
    """Convert numpy/pandas types to JSON-serializable Python types"""
    if isinstance(obj, dict):
        return {str(k): convert_to_json_serializable(v) for k, v in obj.items()}  # type: ignore
    elif isinstance(obj, (list, tuple)):
        return [convert_to_json_serializable(item) for item in obj]  # type: ignore
    elif isinstance(obj, np.integer):  # type: ignore
        return int(obj)  # type: ignore
    elif isinstance(obj, np.floating):  # type: ignore
        return float(obj)  # type: ignore
    elif isinstance(obj, (bool, np.bool_)):  # type: ignore
        return bool(obj)  # type: ignore
    elif isinstance(obj, np.ndarray):
        return obj.tolist()  # type: ignore
    elif isinstance(obj, pd.Series):  # type: ignore
        return {str(k): convert_to_json_serializable(v) for k, v in obj.to_dict().items()}  # type: ignore
    elif isinstance(obj, pd.DataFrame):  # type: ignore
        return {str(k): convert_to_json_serializable(v) for k, v in obj.to_dict().items()}  # type: ignore
    elif obj is None:
        return None
    return obj

def detect_file_format(filename: str) -> str:
    """Detect file format from filename"""
    _, file_ext = os.path.splitext(filename)
    ext = file_ext.lower().strip()
    
    formats: Dict[str, str] = {
        '.csv': 'csv',
        '.json': 'json',
        '.xlsx': 'xlsx',
        '.xls': 'xls',
        '.tsv': 'tsv',
        '.txt': 'txt',
        '.parquet': 'parquet',
        '.pq': 'parquet',
        '.hdf5': 'hdf5',
        '.h5': 'hdf5',
        '.feather': 'feather',
    }
    return formats.get(ext, 'unknown')

def read_data_file(file: Union[BinaryIO, Any]) -> pd.DataFrame:  # type: ignore
    """Read various data file formats using pandas with encoding support"""
    file_format = detect_file_format(getattr(file, 'filename', ''))
    encodings = ['utf-8', 'latin-1', 'windows-1252', 'iso-8859-1', 'cp1252']
    
    def try_read_csv_with_encodings(file_obj: Any, **kwargs: Any) -> pd.DataFrame:  # type: ignore
        """Try reading CSV with multiple encodings"""
        file_obj.seek(0)
        for encoding in encodings:
            try:
                file_obj.seek(0)
                return pd.read_csv(file_obj, encoding=encoding, **kwargs)  # type: ignore
            except (UnicodeDecodeError, UnicodeError, LookupError):
                continue
        file_obj.seek(0)
        return pd.read_csv(file_obj, encoding='utf-8', errors='replace', **kwargs)  # type: ignore
    
    try:
        if file_format == 'csv':
            return try_read_csv_with_encodings(file)
        elif file_format == 'json':
            return pd.read_json(file)  # type: ignore
        elif file_format in ['xlsx', 'xls']:
            return pd.read_excel(file)  # type: ignore
        elif file_format == 'tsv':
            return try_read_csv_with_encodings(file, sep='\t')
        elif file_format == 'txt':
            file.seek(0)
            first_line: str = file.readline().decode('utf-8', errors='ignore')
            if '\t' in first_line:
                return try_read_csv_with_encodings(file, sep='\t')
            else:
                return try_read_csv_with_encodings(file, delimiter=r'\s+')
        elif file_format == 'parquet':
            file.seek(0)
            return pd.read_parquet(file)  # type: ignore
        elif file_format in ['hdf5', 'h5']:
            file.seek(0)
            result = pd.read_hdf(file)  # type: ignore
            if isinstance(result, pd.DataFrame):  # type: ignore
                return result
            raise ValueError("HDF5 file did not contain a DataFrame")
        elif file_format == 'feather':
            file.seek(0)
            return pd.read_feather(file)  # type: ignore
        else:
            return try_read_csv_with_encodings(file)
    except Exception as e:
        raise ValueError(f"Error reading {file_format} file: {str(e)}")

def process_file(file: Any) -> Tuple[Dict[str, Any], pd.DataFrame]:  # type: ignore
    """Process data file with comprehensive cleaning - supports multiple formats"""
    try:
        # Read file in appropriate format
        df = read_data_file(file)
        
        if df.empty:
            raise ValueError("Uploaded file is empty")
        
        # Clean data and get report
        df_cleaned, cleaning_report = clean_data(df)  # type: ignore
        
        # Analyze cleaned data
        result = analyze_data(df_cleaned)
        result["cleaning_report"] = cleaning_report
        result["file_format"] = detect_file_format(getattr(file, 'filename', 'unknown'))
        
        # Generate all graph types for EDA
        graphs = generate_all_graphs(df_cleaned)
        result["graphs"] = graphs
        
        # Generate all comparison tables
        tables = generate_all_tables(df_cleaned)
        result["tables"] = tables
        
        # Convert all numpy/pandas types to JSON-serializable Python types
        result = convert_to_json_serializable(result)
        
        # Save to DB - handle missing attributes gracefully
        filename: str = getattr(file, 'filename', 'unknown')
        try:
            record = UploadedDataset(  # type: ignore
                filename=filename,  # type: ignore
                rows=int(result.get("rows", 0)),  # type: ignore
                columns=int(result.get("columns", 0))  # type: ignore
            )
            db.session.add(record)  # type: ignore
            db.session.commit()  # type: ignore
        except Exception as db_error:  # type: ignore
            db.session.rollback()  # type: ignore
            pass  # Continue even if DB write fails
        
        # Store cleaned data in session for export
        return result, df_cleaned
    except Exception as e:
        raise ValueError(f"File processing failed: {str(e)}")

def generate_all_tables(df: pd.DataFrame) -> Dict[str, Any]:  # type: ignore
    """Generate comparison tables and statistics"""
    tables: Dict[str, Any] = {}
    
    try:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()  # type: ignore
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()  # type: ignore
        
        # Descriptive statistics table
        if numeric_cols:
            desc_stats = df[numeric_cols].describe().to_dict()  # type: ignore
            tables['descriptive_statistics'] = convert_to_json_serializable(desc_stats)
        
        # Data types table
        data_types_table = {  # type: ignore
            'column_name': list(df.columns),
            'data_type': [str(dt) for dt in df.dtypes],
            'non_null_count': [int(df[col].notna().sum()) for col in df.columns],  # type: ignore
            'null_count': [int(df[col].isna().sum()) for col in df.columns]  # type: ignore
        }
        tables['data_types'] = data_types_table
        
        # Numeric columns comparison table
        if numeric_cols:
            numeric_comparison = {}  # type: ignore
            for col in numeric_cols:
                numeric_comparison[col] = {  # type: ignore
                    'count': int(df[col].count()),
                    'mean': float(df[col].mean()),  # type: ignore
                    'std': float(df[col].std()),  # type: ignore
                    'min': float(df[col].min()),  # type: ignore
                    'max': float(df[col].max()),  # type: ignore
                    'q1': float(df[col].quantile(0.25)),  # type: ignore
                    'median': float(df[col].median()),  # type: ignore
                    'q3': float(df[col].quantile(0.75)),  # type: ignore
                }
            tables['numeric_comparison'] = numeric_comparison
        
        # Categorical columns comparison table
        if categorical_cols:
            categorical_comparison = {}  # type: ignore
            for col in categorical_cols:
                value_counts = df[col].value_counts().to_dict()  # type: ignore
                unique_count = int(df[col].nunique())  # type: ignore
                most_common = df[col].mode()[0] if len(df[col].mode()) > 0 else None  # type: ignore
                categorical_comparison[col] = {  # type: ignore
                    'unique_count': unique_count,
                    'most_common_value': str(most_common),
                    'value_distribution': {str(k): int(v) for k, v in value_counts.items()},  # type: ignore
                }
            tables['categorical_comparison'] = categorical_comparison
        
        # Missing values summary table
        missing_summary = {}  # type: ignore
        for col in df.columns:
            missing_count = int(df[col].isna().sum())  # type: ignore
            if missing_count > 0:
                missing_pct = round((missing_count / len(df)) * 100, 2)  # type: ignore
                missing_summary[col] = {  # type: ignore
                    'missing_count': missing_count,
                    'missing_percentage': missing_pct
                }
        tables['missing_values'] = missing_summary
        
        # Correlation comparison table
        if len(numeric_cols) > 1:
            corr_matrix = df[numeric_cols].corr()  # type: ignore
            corr_dict = {}  # type: ignore
            for col in numeric_cols:
                corr_dict[col] = {str(k): float(v) for k, v in corr_matrix[col].items()}  # type: ignore
            tables['correlation_matrix'] = corr_dict
        
        # Duplicate rows analysis
        duplicate_rows = int(df.duplicated().sum())  # type: ignore
        tables['duplicate_analysis'] = {  # type: ignore
            'total_duplicates': duplicate_rows,
            'duplicate_percentage': round((duplicate_rows / len(df)) * 100, 2) if len(df) > 0 else 0  # type: ignore
        }
        
        # Summary statistics table
        tables['summary'] = {  # type: ignore
            'total_rows': int(df.shape[0]),
            'total_columns': int(df.shape[1]),
            'numeric_columns': len(numeric_cols),
            'categorical_columns': len(categorical_cols),
            'total_missing_values': int(df.isna().sum().sum()),  # type: ignore
            'memory_usage_mb': round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2)  # type: ignore
        }
        
    except Exception as e:  # type: ignore
        pass
    
    return tables

def generate_graph(df: pd.DataFrame, column: Optional[str] = None, graph_type: str = 'histogram') -> str:  # type: ignore
    """Generate graph and return base64 encoded image"""
    try:
        plt.figure(figsize=(10, 6))  # type: ignore
        plt.tight_layout()  # type: ignore
        
        if graph_type == 'histogram' and column:
            if df[column].dtype in ['int64', 'float64']:
                plt.hist(df[column].dropna(), bins=30, edgecolor='black', color='skyblue')  # type: ignore
                plt.xlabel(column)  # type: ignore
                plt.ylabel('Frequency')  # type: ignore
                plt.title(f'Histogram of {column}')  # type: ignore
        elif graph_type == 'distribution':
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()  # type: ignore
            if numeric_cols:
                df[numeric_cols].boxplot()  # type: ignore
                plt.title('Distribution of Numeric Columns')  # type: ignore
        elif graph_type == 'correlation':
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()  # type: ignore
            if len(numeric_cols) > 1:
                corr_matrix = df[numeric_cols].corr()  # type: ignore
                sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0)  # type: ignore
                plt.title('Correlation Matrix')  # type: ignore
        elif graph_type == 'missing':
            missing = df.isnull().sum()  # type: ignore
            if missing.sum() > 0:
                missing[missing > 0].plot(kind='barh', color='coral')  # type: ignore
                plt.xlabel('Missing Count')  # type: ignore
                plt.title('Missing Values by Column')  # type: ignore
        elif graph_type == 'scatter' and column:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()  # type: ignore
            if len(numeric_cols) >= 2 and column in numeric_cols:
                other_col = [c for c in numeric_cols if c != column][0]
                plt.scatter(df[column], df[other_col], alpha=0.6, color='green')  # type: ignore
                plt.xlabel(column)  # type: ignore
                plt.ylabel(other_col)  # type: ignore
                plt.title(f'Scatter: {column} vs {other_col}')  # type: ignore
        elif graph_type == 'pie' and column:
            value_counts = df[column].value_counts()
            if len(value_counts) <= 10:
                plt.pie(value_counts, labels=value_counts.index, autopct='%1.1f%%')  # type: ignore
                plt.title(f'Pie Chart of {column}')  # type: ignore
        elif graph_type == 'line' and column:
            if df[column].dtype in ['int64', 'float64']:
                plt.plot(df[column].reset_index(drop=True), marker='o', color='purple', alpha=0.7)  # type: ignore
                plt.xlabel('Index')  # type: ignore
                plt.ylabel(column)  # type: ignore
                plt.title(f'Line Plot of {column}')  # type: ignore
        elif graph_type == 'bar':
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()  # type: ignore
            if numeric_cols:
                df[numeric_cols[:5]].mean().plot(kind='bar', color='steelblue')  # type: ignore
                plt.title('Mean Values of Numeric Columns')  # type: ignore
                plt.ylabel('Mean')  # type: ignore
        elif graph_type == 'kde' and column:
            if df[column].dtype in ['int64', 'float64']:
                df[column].plot(kind='kde', color='orange')  # type: ignore
                plt.title(f'KDE Plot of {column}')  # type: ignore
        elif graph_type == 'area' and column:
            if df[column].dtype in ['int64', 'float64']:
                plt.fill_between(range(len(df[column])), df[column], alpha=0.4, color='red')  # type: ignore
                plt.plot(df[column], color='red', alpha=0.8)  # type: ignore
                plt.title(f'Area Chart of {column}')  # type: ignore
        elif graph_type == 'violin':
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()  # type: ignore
            if numeric_cols:
                data_to_plot = [df[col].dropna().values for col in numeric_cols[:4]]  # type: ignore
                plt.violinplot(data_to_plot)  # type: ignore
                plt.title('Violin Plot of Numeric Columns')  # type: ignore
        
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight')  # type: ignore
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')
        plt.close()  # type: ignore
        return img_base64
    except Exception as e:  # type: ignore
        plt.close()  # type: ignore
        return ""

def generate_all_graphs(df: pd.DataFrame) -> Dict[str, str]:  # type: ignore
    """Generate all types of graphs for comprehensive exploratory data analysis"""
    graphs: Dict[str, str] = {}
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()  # type: ignore
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()  # type: ignore
    
    try:
        # Numeric column graphs
        if numeric_cols:
            graphs['histogram'] = generate_graph(df, numeric_cols[0], 'histogram')
            graphs['distribution'] = generate_graph(df, None, 'distribution')
            graphs['correlation'] = generate_graph(df, None, 'correlation')
            graphs['scatter'] = generate_graph(df, numeric_cols[0], 'scatter')
            graphs['line'] = generate_graph(df, numeric_cols[0], 'line')
            graphs['kde'] = generate_graph(df, numeric_cols[0], 'kde')
            graphs['area'] = generate_graph(df, numeric_cols[0], 'area')
            graphs['bar'] = generate_graph(df, None, 'bar')
            graphs['violin'] = generate_graph(df, None, 'violin')
        
        # Categorical column graphs
        if categorical_cols:
            graphs['pie'] = generate_graph(df, categorical_cols[0], 'pie')
        
        # Missing values chart
        graphs['missing'] = generate_graph(df, None, 'missing')
        
    except Exception as e:  # type: ignore
        pass
    
    return graphs
