"""Data processing, cleaning, and normalization utilities."""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import re
from difflib import SequenceMatcher


class DataCleaner:
    """Handles data cleaning and normalization."""
    
    @staticmethod
    def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean a DataFrame with comprehensive cleaning operations.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        df_clean = df.copy()
        
        # Standardize column names
        df_clean.columns = DataCleaner._standardize_column_names(df_clean.columns)
        
        # Remove duplicate rows (handle unhashable types)
        try:
            df_clean = df_clean.drop_duplicates()
        except TypeError:
            # If we have unhashable types, only drop duplicates on hashable columns
            hashable_cols = []
            for col in df_clean.columns:
                try:
                    df_clean[col].iloc[0].__hash__()
                    hashable_cols.append(col)
                except (TypeError, AttributeError, IndexError):
                    pass
            if hashable_cols:
                # Keep first occurrence of duplicates based on hashable columns
                df_clean = df_clean.drop_duplicates(subset=hashable_cols)
        
        # Remove duplicate columns
        df_clean = df_clean.loc[:, ~df_clean.columns.duplicated()]
        
        # Clean string columns
        for col in df_clean.select_dtypes(include=['object']).columns:
            df_clean[col] = DataCleaner._clean_string_column(df_clean[col])
        
        # Handle numeric columns
        for col in df_clean.select_dtypes(include=['number']).columns:
            df_clean[col] = DataCleaner._clean_numeric_column(df_clean[col])
        
        return df_clean
    
    @staticmethod
    def _standardize_column_names(columns: pd.Index) -> List[str]:
        """Standardize column names to lowercase with underscores."""
        standardized = []
        for col in columns:
            # Convert to string and lowercase
            col_str = str(col).lower().strip()
            # Replace spaces and special characters with underscores
            col_str = re.sub(r'[^\w\s]', '', col_str)
            col_str = re.sub(r'\s+', '_', col_str)
            # Remove multiple consecutive underscores
            col_str = re.sub(r'_+', '_', col_str)
            # Remove leading/trailing underscores
            col_str = col_str.strip('_')
            standardized.append(col_str)
        return standardized
    
    @staticmethod
    def _clean_string_column(series: pd.Series) -> pd.Series:
        """Clean a string column."""
        return (series
                .astype(str)
                .str.strip()
                .str.replace(r'\s+', ' ', regex=True)
                .replace(['nan', 'None', 'NULL', ''], np.nan))
    
    @staticmethod
    def _clean_numeric_column(series: pd.Series) -> pd.Series:
        """Clean a numeric column."""
        # Replace infinite values with NaN
        series = series.replace([np.inf, -np.inf], np.nan)
        return series
    
    @staticmethod
    def handle_missing_data(
        df: pd.DataFrame,
        strategy: str = 'drop',
        threshold: float = 0.5
    ) -> pd.DataFrame:
        """
        Handle missing data in DataFrame.
        
        Args:
            df: Input DataFrame
            strategy: 'drop', 'fill_mean', 'fill_median', 'fill_mode', 'fill_forward'
            threshold: For 'drop' strategy, drop columns with > threshold missing
            
        Returns:
            DataFrame with missing data handled
        """
        df_processed = df.copy()
        
        if strategy == 'drop':
            # Drop columns with too many missing values
            missing_pct = df_processed.isnull().sum() / len(df_processed)
            cols_to_keep = missing_pct[missing_pct <= threshold].index
            df_processed = df_processed[cols_to_keep]
            
            # Drop rows with any remaining missing values
            df_processed = df_processed.dropna()
            
        elif strategy == 'fill_mean':
            numeric_cols = df_processed.select_dtypes(include=['number']).columns
            df_processed[numeric_cols] = df_processed[numeric_cols].fillna(
                df_processed[numeric_cols].mean()
            )
            
        elif strategy == 'fill_median':
            numeric_cols = df_processed.select_dtypes(include=['number']).columns
            df_processed[numeric_cols] = df_processed[numeric_cols].fillna(
                df_processed[numeric_cols].median()
            )
            
        elif strategy == 'fill_mode':
            for col in df_processed.columns:
                if df_processed[col].isnull().any():
                    mode_val = df_processed[col].mode()
                    if len(mode_val) > 0:
                        df_processed[col] = df_processed[col].fillna(mode_val[0])
                        
        elif strategy == 'fill_forward':
            df_processed = df_processed.fillna(method='ffill')
        
        return df_processed
    
    @staticmethod
    def normalize_values(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """
        Normalize values in specified columns (0-1 scaling).
        
        Args:
            df: Input DataFrame
            columns: Columns to normalize
            
        Returns:
            DataFrame with normalized columns
        """
        df_normalized = df.copy()
        
        for col in columns:
            if col in df_normalized.columns and df_normalized[col].dtype in ['int64', 'float64']:
                min_val = df_normalized[col].min()
                max_val = df_normalized[col].max()
                
                if max_val > min_val:
                    df_normalized[col] = (df_normalized[col] - min_val) / (max_val - min_val)
        
        return df_normalized


class SchemaMapper:
    """Maps columns between different data sources."""
    
    @staticmethod
    def suggest_column_mapping(
        source_df: pd.DataFrame,
        target_df: pd.DataFrame,
        threshold: float = 0.6
    ) -> Dict[str, str]:
        """
        Suggest column mappings between two DataFrames based on name similarity.
        
        Args:
            source_df: Source DataFrame
            target_df: Target DataFrame
            threshold: Minimum similarity score (0-1) to suggest a match
            
        Returns:
            Dictionary mapping source columns to target columns
        """
        mappings = {}
        source_cols = list(source_df.columns)
        target_cols = list(target_df.columns)
        
        for source_col in source_cols:
            best_match = None
            best_score = 0
            
            for target_col in target_cols:
                # Calculate similarity score
                score = SchemaMapper._similarity_score(source_col, target_col)
                
                if score > best_score and score >= threshold:
                    best_score = score
                    best_match = target_col
            
            if best_match:
                mappings[source_col] = best_match
        
        return mappings
    
    @staticmethod
    def _similarity_score(str1: str, str2: str) -> float:
        """Calculate similarity score between two strings."""
        # Convert to lowercase for comparison
        str1_lower = str1.lower()
        str2_lower = str2.lower()
        
        # Exact match
        if str1_lower == str2_lower:
            return 1.0
        
        # Sequence matcher for fuzzy matching
        ratio = SequenceMatcher(None, str1_lower, str2_lower).ratio()
        
        # Check for common patterns
        patterns = [
            ('email', 'mail', 0.9),
            ('company', 'organization', 0.8),
            ('company', 'business', 0.7),
            ('name', 'title', 0.6),
            ('phone', 'tel', 0.9),
            ('address', 'location', 0.7),
        ]
        
        for pattern1, pattern2, boost in patterns:
            if (pattern1 in str1_lower and pattern2 in str2_lower) or \
               (pattern2 in str1_lower and pattern1 in str2_lower):
                ratio = max(ratio, boost)
        
        return ratio
    
    @staticmethod
    def apply_mapping(
        df: pd.DataFrame,
        mapping: Dict[str, str],
        keep_unmapped: bool = True
    ) -> pd.DataFrame:
        """
        Apply column mapping to DataFrame.
        
        Args:
            df: Input DataFrame
            mapping: Dictionary of {old_name: new_name}
            keep_unmapped: Keep columns not in mapping
            
        Returns:
            DataFrame with renamed columns
        """
        df_mapped = df.copy()
        
        # Rename mapped columns
        df_mapped = df_mapped.rename(columns=mapping)
        
        # Optionally drop unmapped columns
        if not keep_unmapped:
            mapped_cols = list(mapping.values())
            df_mapped = df_mapped[mapped_cols]
        
        return df_mapped
    
    @staticmethod
    def find_common_columns(df1: pd.DataFrame, df2: pd.DataFrame) -> List[str]:
        """Find columns that exist in both DataFrames."""
        return list(set(df1.columns) & set(df2.columns))
    
    @staticmethod
    def align_schemas(
        df1: pd.DataFrame,
        df2: pd.DataFrame,
        mapping: Optional[Dict[str, str]] = None
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Align two DataFrames to have matching columns.
        
        Args:
            df1: First DataFrame
            df2: Second DataFrame
            mapping: Optional explicit mapping
            
        Returns:
            Tuple of aligned DataFrames
        """
        if mapping is None:
            # Auto-suggest mapping
            mapping = SchemaMapper.suggest_column_mapping(df2, df1)
        
        # Apply mapping to df2
        df2_aligned = SchemaMapper.apply_mapping(df2, mapping, keep_unmapped=True)
        
        # Find common columns
        common_cols = SchemaMapper.find_common_columns(df1, df2_aligned)
        
        # Keep only common columns in both DataFrames
        df1_aligned = df1[common_cols]
        df2_aligned = df2_aligned[common_cols]
        
        return df1_aligned, df2_aligned


class DataValidator:
    """Validates data quality and structure."""
    
    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform comprehensive validation on DataFrame.
        
        Returns:
            Dictionary with validation results
        """
        validation = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'stats': {}
        }
        
        # Check if DataFrame is empty
        if df.empty:
            validation['is_valid'] = False
            validation['errors'].append('DataFrame is empty')
            return validation
        
        # Check for duplicate rows (only on hashable columns)
        duplicate_count = 0
        try:
            # Try to check duplicates on all columns
            duplicate_count = df.duplicated().sum()
        except TypeError:
            # If we have unhashable types, check only hashable columns
            hashable_cols = []
            for col in df.columns:
                try:
                    # Test if column is hashable
                    df[col].iloc[0].__hash__()
                    hashable_cols.append(col)
                except (TypeError, AttributeError):
                    pass
            
            if hashable_cols:
                duplicate_count = df[hashable_cols].duplicated().sum()
                validation['warnings'].append(
                    f'Duplicate check performed on {len(hashable_cols)}/{len(df.columns)} columns (skipped unhashable types)'
                )
        
        if duplicate_count > 0:
            validation['warnings'].append(
                f'Found {duplicate_count} duplicate rows'
            )
        
        # Check for missing data
        missing_data = df.isnull().sum()
        total_missing = missing_data.sum()
        if total_missing > 0:
            missing_pct = (total_missing / (len(df) * len(df.columns))) * 100
            validation['warnings'].append(
                f'Missing data: {total_missing} values ({missing_pct:.1f}%)'
            )
        
        # Check for columns with all missing values
        all_missing_cols = missing_data[missing_data == len(df)].index.tolist()
        if all_missing_cols:
            validation['errors'].append(
                f'Columns with all missing values: {all_missing_cols}'
            )
        
        # Check data types
        validation['stats']['total_rows'] = len(df)
        validation['stats']['total_columns'] = len(df.columns)
        validation['stats']['numeric_columns'] = len(
            df.select_dtypes(include=['number']).columns
        )
        validation['stats']['text_columns'] = len(
            df.select_dtypes(include=['object']).columns
        )
        validation['stats']['missing_values'] = int(total_missing)
        validation['stats']['duplicate_rows'] = int(duplicate_count)
        
        return validation
    
    @staticmethod
    def check_required_columns(
        df: pd.DataFrame,
        required_columns: List[str]
    ) -> Tuple[bool, List[str]]:
        """
        Check if DataFrame has required columns.
        
        Returns:
            Tuple of (all_present, missing_columns)
        """
        missing = [col for col in required_columns if col not in df.columns]
        return len(missing) == 0, missing
    
    @staticmethod
    def get_data_quality_score(df: pd.DataFrame) -> float:
        """
        Calculate overall data quality score (0-100).
        
        Returns:
            Quality score
        """
        if df.empty:
            return 0.0
        
        # Completeness score (no missing values)
        completeness = 1 - (df.isnull().sum().sum() / (len(df) * len(df.columns)))
        
        # Uniqueness score (no duplicates) - handle unhashable types
        duplicate_count = 0
        try:
            duplicate_count = df.duplicated().sum()
        except TypeError:
            # If we have unhashable types, check only hashable columns
            hashable_cols = []
            for col in df.columns:
                try:
                    df[col].iloc[0].__hash__()
                    hashable_cols.append(col)
                except (TypeError, AttributeError):
                    pass
            if hashable_cols:
                duplicate_count = df[hashable_cols].duplicated().sum()
        
        uniqueness = 1 - (duplicate_count / len(df)) if len(df) > 0 else 1.0
        
        # Column validity (no all-null columns)
        all_null_cols = (df.isnull().sum() == len(df)).sum()
        validity = 1 - (all_null_cols / len(df.columns))
        
        # Weighted average
        score = (completeness * 0.4 + uniqueness * 0.3 + validity * 0.3) * 100
        
        return round(score, 2)

