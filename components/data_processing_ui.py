"""UI components for data processing and schema mapping."""

import streamlit as st
import pandas as pd
from typing import Dict, Optional

from src.data_processing import DataCleaner, SchemaMapper, DataValidator


def render_data_quality_report(df: pd.DataFrame, title: str = "Data Quality Report") -> None:
    """
    Render a comprehensive data quality report.
    
    Args:
        df: DataFrame to analyze
        title: Report title
    """
    st.markdown(f"### {title}")
    
    # Get validation results
    validation = DataValidator.validate_dataframe(df)
    quality_score = DataValidator.get_data_quality_score(df)
    
    # Display quality score
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Color code the quality score
        if quality_score >= 80:
            st.success(f"**Quality Score: {quality_score}/100** ✅")
        elif quality_score >= 60:
            st.warning(f"**Quality Score: {quality_score}/100** ⚠️")
        else:
            st.error(f"**Quality Score: {quality_score}/100** ❌")
    
    with col2:
        missing_pct = (validation['stats']['missing_values'] / 
                      (validation['stats']['total_rows'] * validation['stats']['total_columns'])) * 100
        st.metric("Completeness", f"{100 - missing_pct:.1f}%")
    
    with col3:
        dup_pct = (validation['stats']['duplicate_rows'] / validation['stats']['total_rows']) * 100
        st.metric("Uniqueness", f"{100 - dup_pct:.1f}%")
    
    # Show errors and warnings
    if validation['errors']:
        st.error("**Errors:**")
        for error in validation['errors']:
            st.markdown(f"- {error}")
    
    if validation['warnings']:
        with st.expander("⚠️ Warnings", expanded=False):
            for warning in validation['warnings']:
                st.markdown(f"- {warning}")
    
    # Show stats
    with st.expander("📊 Detailed Statistics", expanded=False):
        stats = validation['stats']
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            - **Total Rows:** {stats['total_rows']:,}
            - **Total Columns:** {stats['total_columns']}
            - **Numeric Columns:** {stats['numeric_columns']}
            """)
        
        with col2:
            st.markdown(f"""
            - **Text Columns:** {stats['text_columns']}
            - **Missing Values:** {stats['missing_values']:,}
            - **Duplicate Rows:** {stats['duplicate_rows']:,}
            """)


def render_data_cleaning_options(df: pd.DataFrame, key_prefix: str = "") -> Optional[pd.DataFrame]:
    """
    Render data cleaning options and return cleaned DataFrame.
    
    Args:
        df: Input DataFrame
        key_prefix: Prefix for widget keys
        
    Returns:
        Cleaned DataFrame if cleaning was applied, None otherwise
    """
    st.markdown("### 🧹 Data Cleaning Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        clean_basic = st.checkbox(
            "Clean column names & remove duplicates",
            value=True,
            key=f"{key_prefix}_clean_basic",
            help="Standardize column names and remove duplicate rows/columns"
        )
    
    with col2:
        handle_missing = st.checkbox(
            "Handle missing data",
            value=False,
            key=f"{key_prefix}_handle_missing",
            help="Apply strategy to handle missing values"
        )
    
    missing_strategy = None
    if handle_missing:
        missing_strategy = st.selectbox(
            "Missing data strategy",
            options=['drop', 'fill_mean', 'fill_median', 'fill_mode', 'fill_forward'],
            key=f"{key_prefix}_missing_strategy",
            help="Choose how to handle missing values"
        )
        
        if missing_strategy == 'drop':
            threshold = st.slider(
                "Drop threshold (% missing allowed)",
                0.0, 1.0, 0.5, 0.1,
                key=f"{key_prefix}_threshold",
                help="Drop columns with more than this % of missing values"
            )
        else:
            threshold = 0.5
    
    # Apply cleaning button
    if st.button(f"🚀 Apply Cleaning", key=f"{key_prefix}_apply", type="primary"):
        with st.spinner("Cleaning data..."):
            df_cleaned = df.copy()
            
            # Apply basic cleaning
            if clean_basic:
                df_cleaned = DataCleaner.clean_dataframe(df_cleaned)
                st.success("✅ Applied basic cleaning")
            
            # Handle missing data
            if handle_missing and missing_strategy:
                df_cleaned = DataCleaner.handle_missing_data(
                    df_cleaned,
                    strategy=missing_strategy,
                    threshold=threshold
                )
                st.success(f"✅ Applied {missing_strategy} strategy for missing data")
            
            # Show before/after comparison
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Original Rows", len(df))
            with col2:
                st.metric("Cleaned Rows", len(df_cleaned), 
                         delta=len(df_cleaned) - len(df))
            
            return df_cleaned
    
    return None


def render_schema_mapper(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    df1_name: str = "Dataset 1",
    df2_name: str = "Dataset 2"
) -> Optional[Dict[str, str]]:
    """
    Render interactive schema mapping interface.
    
    Args:
        df1: First DataFrame
        df2: Second DataFrame
        df1_name: Name for first dataset
        df2_name: Name for second dataset
        
    Returns:
        Column mapping dictionary if mapping was created
    """
    st.markdown("### 🔄 Schema Mapping")
    st.markdown(f"Map columns from **{df2_name}** to **{df1_name}**")
    
    # Auto-suggest mapping
    suggested_mapping = SchemaMapper.suggest_column_mapping(df2, df1, threshold=0.6)
    
    if suggested_mapping:
        st.info(f"💡 Found {len(suggested_mapping)} suggested column matches")
    
    # Let user review and modify mappings
    st.markdown("#### Review Suggested Mappings")
    
    mapping = {}
    for source_col in df2.columns:
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col1:
            st.markdown(f"**{source_col}**")
            st.caption(f"Type: {df2[source_col].dtype}")
        
        with col2:
            st.markdown("→")
        
        with col3:
            # Get suggested target or None
            suggested_target = suggested_mapping.get(source_col, "-- Skip --")
            
            # Create list of options
            options = ["-- Skip --"] + list(df1.columns)
            default_idx = options.index(suggested_target) if suggested_target in options else 0
            
            target_col = st.selectbox(
                f"Map to",
                options=options,
                index=default_idx,
                key=f"map_{source_col}",
                label_visibility="collapsed"
            )
            
            if target_col != "-- Skip --":
                mapping[source_col] = target_col
    
    # Show mapping summary
    if mapping:
        st.success(f"✅ {len(mapping)} columns mapped")
        
        with st.expander("📋 View Mapping Summary"):
            for source, target in mapping.items():
                st.markdown(f"- `{source}` → `{target}`")
        
        return mapping
    else:
        st.warning("⚠️ No columns mapped")
        return None


def render_column_comparison(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    df1_name: str = "Dataset 1",
    df2_name: str = "Dataset 2"
) -> None:
    """
    Render side-by-side column comparison.
    
    Args:
        df1: First DataFrame
        df2: Second DataFrame
        df1_name: Name for first dataset
        df2_name: Name for second dataset
    """
    st.markdown("### 📊 Column Comparison")
    
    col1, col2 = st.columns(2)
    
    # Dataset 1 columns
    with col1:
        st.markdown(f"#### {df1_name}")
        st.markdown(f"**{len(df1.columns)} columns**")
        
        df1_cols = pd.DataFrame({
            'Column': df1.columns,
            'Type': df1.dtypes.astype(str),
            'Non-Null': df1.count().values,
            'Null %': (df1.isnull().sum() / len(df1) * 100).round(1).values
        })
        st.dataframe(df1_cols, use_container_width=True, hide_index=True)
    
    # Dataset 2 columns
    with col2:
        st.markdown(f"#### {df2_name}")
        st.markdown(f"**{len(df2.columns)} columns**")
        
        df2_cols = pd.DataFrame({
            'Column': df2.columns,
            'Type': df2.dtypes.astype(str),
            'Non-Null': df2.count().values,
            'Null %': (df2.isnull().sum() / len(df2) * 100).round(1).values
        })
        st.dataframe(df2_cols, use_container_width=True, hide_index=True)
    
    # Show common columns
    common_cols = SchemaMapper.find_common_columns(df1, df2)
    if common_cols:
        st.success(f"✅ {len(common_cols)} common columns: {', '.join(common_cols)}")
    else:
        st.info("ℹ️ No common column names found. Use schema mapping to align datasets.")


def render_data_transformation_options(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """
    Render data transformation options.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Transformed DataFrame if transformations were applied
    """
    st.markdown("### ⚙️ Data Transformations")
    
    # Get numeric columns
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    if not numeric_cols:
        st.info("ℹ️ No numeric columns available for transformation")
        return None
    
    normalize_cols = st.multiselect(
        "Normalize columns (0-1 scaling)",
        options=numeric_cols,
        help="Select numeric columns to normalize to 0-1 range"
    )
    
    if normalize_cols and st.button("Apply Normalization", type="primary"):
        with st.spinner("Normalizing data..."):
            df_transformed = DataCleaner.normalize_values(df, normalize_cols)
            st.success(f"✅ Normalized {len(normalize_cols)} columns")
            
            # Show before/after samples
            st.markdown("**Before / After Comparison:**")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Original:**")
                st.dataframe(df[normalize_cols].head(), use_container_width=True)
            with col2:
                st.markdown("**Normalized:**")
                st.dataframe(df_transformed[normalize_cols].head(), use_container_width=True)
            
            return df_transformed
    
    return None

