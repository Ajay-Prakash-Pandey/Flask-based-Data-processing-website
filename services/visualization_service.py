import matplotlib
import io
import base64
import pandas as pd
from typing import Optional, Any, Dict

matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt

def generate_column_distribution_chart(df: pd.DataFrame, column_name: str) -> Optional[str]:
    """Generate distribution chart for a column"""
    try:
        fig, ax = plt.subplots(figsize=(8, 6))  # type: ignore
        
        if df[column_name].dtype in ['int64', 'float64']:
            ax.hist(df[column_name].dropna(), bins=20, color='#667eea', edgecolor='black')  # type: ignore
            ax.set_title(f'Distribution of {column_name}')  # type: ignore
            ax.set_xlabel(column_name)  # type: ignore
            ax.set_ylabel('Frequency')  # type: ignore
        else:
            df[column_name].value_counts().head(10).plot(kind='bar', ax=ax, color='#667eea')
            ax.set_title(f'Top 10 Values in {column_name}')  # type: ignore
            ax.set_xlabel(column_name)  # type: ignore
            ax.set_ylabel('Count')  # type: ignore
            plt.xticks(rotation=45)  # type: ignore
        
        plt.tight_layout()
        
        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')  # type: ignore
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close(fig)
        
        return f"data:image/png;base64,{img_base64}"
    except Exception:
        return None

def generate_correlation_heatmap(df: pd.DataFrame) -> Optional[str]:
    """Generate correlation heatmap for numeric columns"""
    try:
        numeric_df = df.select_dtypes(include=['int64', 'float64'])
        
        if numeric_df.shape[1] < 2:
            return None
        
        fig, ax = plt.subplots(figsize=(10, 8))  # type: ignore
        
        corr_matrix = numeric_df.corr()
        im = ax.imshow(corr_matrix, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)  # type: ignore
        
        ax.set_xticks(range(len(corr_matrix.columns)))  # type: ignore
        ax.set_yticks(range(len(corr_matrix.columns)))  # type: ignore
        ax.set_xticklabels(corr_matrix.columns, rotation=45, ha='right')  # type: ignore
        ax.set_yticklabels(corr_matrix.columns)  # type: ignore
        
        ax.set_title('Correlation Heatmap')  # type: ignore
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)  # type: ignore
        cbar.set_label('Correlation')  # type: ignore
        
        plt.tight_layout()
        
        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')  # type: ignore
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close(fig)
        
        return f"data:image/png;base64,{img_base64}"
    except Exception:
        return None

def generate_summary_statistics(df: pd.DataFrame) -> Dict[str, Any]:
    """Generate summary statistics for the dataset"""
    stats: Dict[str, Any] = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "memory_usage": f"{df.memory_usage(deep=True).sum() / 1024:.2f} KB",
        "numeric_columns": len(df.select_dtypes(include=['int64', 'float64']).columns),
        "categorical_columns": len(df.select_dtypes(include=['object']).columns),
        "missing_values": df.isnull().sum().to_dict(),  # type: ignore
        "duplicate_rows": df.duplicated().sum(),
        "numeric_stats": {}
    }
    
    numeric_df = df.select_dtypes(include=['int64', 'float64'])
    for col in numeric_df.columns:
        stats["numeric_stats"][col] = {
            "mean": float(numeric_df[col].mean()),
            "median": float(numeric_df[col].median()),
            "std": float(numeric_df[col].std()),
            "min": float(numeric_df[col].min()),
            "max": float(numeric_df[col].max()),
            "q25": float(numeric_df[col].quantile(0.25)),
            "q75": float(numeric_df[col].quantile(0.75))
        }
    
    return stats

