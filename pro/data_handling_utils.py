"""
Data Handling Utilities for Procurement Analytics
Provides consistent data handling functions across the entire program.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
from typing import Union, List, Dict, Optional, Tuple
from sklearn.preprocessing import LabelEncoder

warnings.filterwarnings('ignore')

class DataHandler:
    """
    Centralized data handling class for consistent data processing across the application.
    """
    
    def __init__(self):
        self.label_encoders = {}
        self.column_mappings = {}
        self.data_validation_rules = {}
        
    def validate_dataframe(self, df: pd.DataFrame, required_columns: List[str], 
                          operation_name: str = "operation") -> Tuple[bool, str]:
        """
        Validate DataFrame for required columns and basic data quality.
        
        Args:
            df: DataFrame to validate
            required_columns: List of required column names
            operation_name: Name of the operation for error messages
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if df is None or df.empty:
            return False, f"No data available for {operation_name}"
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return False, f"Missing required columns for {operation_name}: {missing_columns}"
        
        return True, "Data validation passed"
    
    def safe_merge(self, left_df: pd.DataFrame, right_df: pd.DataFrame, 
                   on: Union[str, List[str]], how: str = 'left', 
                   suffixes: Tuple[str, str] = ('_x', '_y')) -> pd.DataFrame:
        """
        Safely merge DataFrames with proper error handling and column name management.
        
        Args:
            left_df: Left DataFrame
            right_df: Right DataFrame
            on: Column(s) to merge on
            how: Merge type ('left', 'right', 'inner', 'outer')
            suffixes: Suffixes for duplicate columns
            
        Returns:
            Merged DataFrame
        """
        if left_df.empty or right_df.empty:
            return pd.DataFrame()
        
        try:
            merged_df = left_df.merge(right_df, on=on, how=how, suffixes=suffixes)
            return merged_df
        except Exception as e:
            print(f"Merge error: {str(e)}")
            return pd.DataFrame()
    
    def handle_missing_values(self, df: pd.DataFrame, 
                            categorical_fill: str = 'Unknown',
                            numeric_fill: Union[int, float] = 0) -> pd.DataFrame:
        """
        Handle missing values consistently across the DataFrame.
        
        Args:
            df: DataFrame to process
            categorical_fill: Value to fill missing categorical data
            numeric_fill: Value to fill missing numeric data
            
        Returns:
            DataFrame with missing values handled
        """
        if df.empty:
            return df
        
        df_clean = df.copy()
        
        for col in df_clean.columns:
            if df_clean[col].dtype.name == 'category':
                # Convert categorical to string first to avoid category issues
                df_clean[col] = df_clean[col].astype(str)
                df_clean[col] = df_clean[col].replace(['nan', 'None', '<NA>', 'NaT'], categorical_fill)
            elif df_clean[col].dtype in ['object', 'string']:
                df_clean[col] = df_clean[col].fillna(categorical_fill)
            elif df_clean[col].dtype in ['int64', 'float64', 'int32', 'float32']:
                df_clean[col] = df_clean[col].fillna(numeric_fill)
        
        return df_clean
    
    def encode_categorical(self, series: pd.Series, column_name: str = None) -> np.ndarray:
        """
        Encode categorical variables consistently.
        
        Args:
            series: Series to encode
            column_name: Name of the column for encoder storage
            
        Returns:
            Encoded array
        """
        if series.empty:
            return np.array([])
        
        # Convert to string and handle missing values
        if series.dtype.name == 'category':
            series_clean = series.astype(str)
        else:
            series_clean = series.astype(str)
        
        # Handle missing values
        series_clean = series_clean.replace(['nan', 'None', '<NA>', 'NaT'], 'Missing')
        
        # Use column name if provided, otherwise use series name
        col_key = column_name if column_name else series.name
        
        if col_key not in self.label_encoders:
            self.label_encoders[col_key] = LabelEncoder()
            return self.label_encoders[col_key].fit_transform(series_clean)
        else:
            # Handle unseen categories
            encoder_values = self.label_encoders[col_key].classes_
            unseen_mask = ~series_clean.isin(encoder_values)
            series_encoded = series_clean.copy()
            series_encoded[unseen_mask] = encoder_values[0]  # Use first known category
            return self.label_encoders[col_key].transform(series_encoded)
    
    def detect_delivery_date_column(self, df: pd.DataFrame) -> Optional[str]:
        """
        Detect the appropriate delivery date column from common naming patterns.
        
        Args:
            df: DataFrame to search for delivery date columns
            
        Returns:
            Column name or None if not found
        """
        delivery_columns = [
            'delivery_date_actual',
            'actual_delivery_date', 
            'date_delivered',
            'delivery_date'
        ]
        
        for col in delivery_columns:
            if col in df.columns:
                return col
        
        return None
    
    def calculate_delivery_days(self, df: pd.DataFrame, 
                              order_date_col: str = 'order_date',
                              delivery_date_col: str = None) -> pd.Series:
        """
        Calculate delivery days consistently.
        
        Args:
            df: DataFrame containing order and delivery dates
            order_date_col: Name of order date column
            delivery_date_col: Name of delivery date column (auto-detected if None)
            
        Returns:
            Series with delivery days
        """
        if df.empty:
            return pd.Series()
        
        if delivery_date_col is None:
            delivery_date_col = self.detect_delivery_date_column(df)
            if delivery_date_col is None:
                return pd.Series()
        
        if order_date_col not in df.columns or delivery_date_col not in df.columns:
            return pd.Series()
        
        try:
            order_dates = pd.to_datetime(df[order_date_col], errors='coerce')
            delivery_dates = pd.to_datetime(df[delivery_date_col], errors='coerce')
            
            delivery_days = (delivery_dates - order_dates).dt.days
            return delivery_days.fillna(0)
        except Exception as e:
            print(f"Error calculating delivery days: {str(e)}")
            return pd.Series()
    
    def calculate_spend(self, df: pd.DataFrame, 
                       quantity_col: str = 'quantity',
                       unit_price_col: str = 'unit_price') -> pd.Series:
        """
        Calculate spend consistently.
        
        Args:
            df: DataFrame with quantity and unit price
            quantity_col: Name of quantity column
            unit_price_col: Name of unit price column
            
        Returns:
            Series with calculated spend
        """
        if df.empty:
            return pd.Series()
        
        # Handle potential column renaming after merge
        actual_quantity_col = quantity_col if quantity_col in df.columns else f"{quantity_col}_x"
        actual_unit_price_col = unit_price_col if unit_price_col in df.columns else f"{unit_price_col}_x"
        
        if actual_quantity_col not in df.columns or actual_unit_price_col not in df.columns:
            return pd.Series()
        
        try:
            spend = df[actual_quantity_col] * df[actual_unit_price_col]
            return spend.fillna(0)
        except Exception as e:
            print(f"Error calculating spend: {str(e)}")
            return pd.Series()
    
    def prepare_features_for_ml(self, df: pd.DataFrame, 
                               categorical_columns: List[str] = None,
                               numeric_columns: List[str] = None) -> pd.DataFrame:
        """
        Prepare features for machine learning consistently.
        
        Args:
            df: DataFrame to prepare
            categorical_columns: List of categorical column names
            numeric_columns: List of numeric column names
            
        Returns:
            Prepared DataFrame
        """
        if df.empty:
            return pd.DataFrame()
        
        df_prepared = df.copy()
        
        # Handle missing values
        df_prepared = self.handle_missing_values(df_prepared)
        
        # Encode categorical variables
        if categorical_columns:
            for col in categorical_columns:
                if col in df_prepared.columns:
                    df_prepared[f"{col}_encoded"] = self.encode_categorical(df_prepared[col], col)
        
        # Ensure numeric columns are numeric
        if numeric_columns:
            for col in numeric_columns:
                if col in df_prepared.columns:
                    df_prepared[col] = pd.to_numeric(df_prepared[col], errors='coerce').fillna(0)
        
        return df_prepared
    
    def validate_date_column(self, df: pd.DataFrame, date_col: str) -> bool:
        """
        Validate if a column contains valid dates.
        
        Args:
            df: DataFrame to check
            date_col: Name of date column
            
        Returns:
            True if valid dates, False otherwise
        """
        if df.empty or date_col not in df.columns:
            return False
        
        try:
            dates = pd.to_datetime(df[date_col], errors='coerce')
            return not dates.isna().all()
        except:
            return False
    
    def get_column_info(self, df: pd.DataFrame) -> Dict:
        """
        Get comprehensive information about DataFrame columns.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dictionary with column information
        """
        if df.empty:
            return {}
        
        info = {}
        for col in df.columns:
            col_info = {
                'dtype': str(df[col].dtype),
                'null_count': df[col].isnull().sum(),
                'null_percentage': (df[col].isnull().sum() / len(df)) * 100,
                'unique_count': df[col].nunique(),
                'is_numeric': pd.api.types.is_numeric_dtype(df[col]),
                'is_datetime': pd.api.types.is_datetime64_any_dtype(df[col])
            }
            
            if col_info['is_numeric']:
                col_info['min'] = df[col].min()
                col_info['max'] = df[col].max()
                col_info['mean'] = df[col].mean()
            elif col_info['unique_count'] <= 20:  # Show sample values for categorical
                col_info['sample_values'] = df[col].dropna().unique()[:5].tolist()
            
            info[col] = col_info
        
        return info
    
    def log_data_quality_issues(self, df: pd.DataFrame, operation_name: str = "operation") -> List[str]:
        """
        Log data quality issues for debugging.
        
        Args:
            df: DataFrame to check
            operation_name: Name of the operation
            
        Returns:
            List of quality issues found
        """
        issues = []
        
        if df.empty:
            issues.append(f"{operation_name}: DataFrame is empty")
            return issues
        
        # Check for null values
        null_counts = df.isnull().sum()
        high_null_cols = null_counts[null_counts > len(df) * 0.5]
        if not high_null_cols.empty:
            issues.append(f"{operation_name}: High null values in columns: {list(high_null_cols.index)}")
        
        # Check for duplicate rows
        duplicate_count = df.duplicated().sum()
        if duplicate_count > 0:
            issues.append(f"{operation_name}: {duplicate_count} duplicate rows found")
        
        # Check for infinite values in numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            inf_count = np.isinf(df[col]).sum()
            if inf_count > 0:
                issues.append(f"{operation_name}: {inf_count} infinite values in {col}")
        
        return issues

# Global instance for consistent usage across the application
data_handler = DataHandler()

# Convenience functions for backward compatibility
def validate_dataframe(df: pd.DataFrame, required_columns: List[str], 
                      operation_name: str = "operation") -> Tuple[bool, str]:
    """Convenience function for DataFrame validation."""
    return data_handler.validate_dataframe(df, required_columns, operation_name)

def safe_merge(left_df: pd.DataFrame, right_df: pd.DataFrame, 
               on: Union[str, List[str]], how: str = 'left', 
               suffixes: Tuple[str, str] = ('_x', '_y')) -> pd.DataFrame:
    """Convenience function for safe DataFrame merging."""
    return data_handler.safe_merge(left_df, right_df, on, how, suffixes)

def handle_missing_values(df: pd.DataFrame, 
                        categorical_fill: str = 'Unknown',
                        numeric_fill: Union[int, float] = 0) -> pd.DataFrame:
    """Convenience function for missing value handling."""
    return data_handler.handle_missing_values(df, categorical_fill, numeric_fill)

def encode_categorical(series: pd.Series, column_name: str = None) -> np.ndarray:
    """Convenience function for categorical encoding."""
    return data_handler.encode_categorical(series, column_name)

def detect_delivery_date_column(df: pd.DataFrame) -> Optional[str]:
    """Convenience function for delivery date column detection."""
    return data_handler.detect_delivery_date_column(df)

def calculate_delivery_days(df: pd.DataFrame, 
                          order_date_col: str = 'order_date',
                          delivery_date_col: str = None) -> pd.Series:
    """Convenience function for delivery days calculation."""
    return data_handler.calculate_delivery_days(df, order_date_col, delivery_date_col)

def calculate_spend(df: pd.DataFrame, 
                   quantity_col: str = 'quantity',
                   unit_price_col: str = 'unit_price') -> pd.Series:
    """Convenience function for spend calculation."""
    return data_handler.calculate_spend(df, quantity_col, unit_price_col) 