"""Utility functions for the ICP Analysis Dashboard."""

import pandas as pd
from typing import Any, Dict, List


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean a DataFrame by standardizing column names and handling common issues.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Cleaned DataFrame
    """
    df_clean = df.copy()
    
    # Standardize column names: lowercase, replace spaces with underscores
    df_clean.columns = [
        col.lower().strip().replace(' ', '_').replace('-', '_')
        for col in df_clean.columns
    ]
    
    # Remove duplicate columns
    df_clean = df_clean.loc[:, ~df_clean.columns.duplicated()]
    
    # Strip whitespace from string columns
    for col in df_clean.select_dtypes(include=['object']).columns:
        df_clean[col] = df_clean[col].str.strip()
    
    return df_clean


def format_number(num: float, decimals: int = 0) -> str:
    """
    Format a number with thousands separators.
    
    Args:
        num: Number to format
        decimals: Number of decimal places
        
    Returns:
        Formatted string
    """
    if decimals == 0:
        return f"{int(num):,}"
    return f"{num:,.{decimals}f}"


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning a default if denominator is zero.
    
    Args:
        numerator: The numerator
        denominator: The denominator
        default: Value to return if division by zero
        
    Returns:
        Result of division or default value
    """
    if denominator == 0:
        return default
    return numerator / denominator


def calculate_similarity_score(
    value1: Any,
    value2: Any,
    field_type: str = "string"
) -> float:
    """
    Calculate a similarity score between two values.
    
    Args:
        value1: First value
        value2: Second value
        field_type: Type of field ("string", "numeric", "categorical")
        
    Returns:
        Similarity score between 0 and 1
    """
    # Handle None/NaN cases
    if pd.isna(value1) or pd.isna(value2):
        return 0.0
    
    if field_type == "string":
        # Simple string similarity (could be enhanced with fuzzy matching)
        str1 = str(value1).lower().strip()
        str2 = str(value2).lower().strip()
        
        if str1 == str2:
            return 1.0
        
        # Check for partial matches
        if str1 in str2 or str2 in str1:
            return 0.7
        
        # Check for word overlap
        words1 = set(str1.split())
        words2 = set(str2.split())
        if words1 and words2:
            overlap = len(words1 & words2) / max(len(words1), len(words2))
            return overlap * 0.5
        
        return 0.0
    
    elif field_type == "numeric":
        # Numeric similarity based on relative difference
        try:
            num1 = float(value1)
            num2 = float(value2)
            
            if num1 == num2:
                return 1.0
            
            # Calculate relative difference
            max_val = max(abs(num1), abs(num2))
            if max_val == 0:
                return 1.0
            
            diff = abs(num1 - num2) / max_val
            return max(0.0, 1.0 - diff)
        except (ValueError, TypeError):
            return 0.0
    
    elif field_type == "categorical":
        # Exact match for categorical values
        return 1.0 if str(value1).lower() == str(value2).lower() else 0.0
    
    return 0.0


def get_sample_icp_criteria() -> Dict[str, Any]:
    """
    Get sample ICP criteria for testing/demonstration.
    
    Returns:
        Dictionary with sample ICP criteria
    """
    return {
        "industries": ["SaaS", "Technology", "Software", "E-commerce"],
        "company_size": ["50-200", "200-1000", "1000+"],
        "revenue_range": ["$1M-$10M", "$10M-$50M", "$50M+"],
        "locations": ["United States", "Canada", "Europe"],
        "key_attributes": [
            "fast-growing",
            "technical team",
            "remote-first",
            "data-driven"
        ],
        "use_cases": [
            "automation",
            "analytics",
            "data integration",
            "workflow optimization"
        ]
    }

