"""CSV file upload and preview component."""

import pandas as pd
import streamlit as st
from typing import Optional


def render_csv_uploader(key: str = "csv_upload") -> Optional[pd.DataFrame]:
    """
    Render a CSV file uploader with preview.
    
    Args:
        key: Unique key for the uploader widget
        
    Returns:
        DataFrame if file is uploaded and valid, None otherwise
    """
    st.markdown("### 📄 Upload Customer Data")
    st.markdown("Upload a CSV file containing your customer data for analysis.")
    
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=["csv"],
        key=key,
        help="Upload a CSV file with customer information"
    )
    
    if uploaded_file is not None:
        try:
            # Read the CSV file
            df = pd.read_csv(uploaded_file)
            
            # Display file info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Rows", len(df))
            with col2:
                st.metric("Total Columns", len(df.columns))
            with col3:
                file_size = uploaded_file.size / 1024  # Convert to KB
                st.metric("File Size", f"{file_size:.1f} KB")
            
            # Show column info
            with st.expander("📊 Column Information", expanded=False):
                col_info = pd.DataFrame({
                    'Column': df.columns,
                    'Type': df.dtypes.astype(str),
                    'Non-Null': df.count().values,
                    'Null': df.isnull().sum().values
                })
                st.dataframe(col_info, use_container_width=True, hide_index=True)
            
            # Show data preview
            with st.expander("👁️ Data Preview", expanded=True):
                st.dataframe(df.head(10), use_container_width=True)
            
            # Data quality checks
            missing_data_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
            if missing_data_pct > 0:
                st.info(f"ℹ️ Dataset contains {missing_data_pct:.1f}% missing values")
            
            return df
            
        except Exception as e:
            st.error(f"❌ Error reading CSV file: {str(e)}")
            st.info("Please ensure your file is a valid CSV format.")
            return None
    
    return None


def render_csv_column_mapper(
    df: pd.DataFrame,
    required_columns: dict[str, str]
) -> Optional[dict[str, str]]:
    """
    Render a column mapping interface for CSV files.
    
    Args:
        df: DataFrame with uploaded data
        required_columns: Dict of {internal_name: description} for required columns
        
    Returns:
        Dictionary mapping internal column names to CSV column names
    """
    st.markdown("### 🔄 Map Your Columns")
    st.markdown("Match your CSV columns to the expected fields.")
    
    mapping = {}
    cols = st.columns(2)
    
    for i, (internal_name, description) in enumerate(required_columns.items()):
        col_idx = i % 2
        with cols[col_idx]:
            selected = st.selectbox(
                f"{internal_name.replace('_', ' ').title()}",
                options=["-- Select Column --"] + list(df.columns),
                help=description,
                key=f"map_{internal_name}"
            )
            
            if selected != "-- Select Column --":
                mapping[internal_name] = selected
    
    # Check if all required fields are mapped
    if len(mapping) == len(required_columns):
        st.success("✅ All required columns mapped!")
        return mapping
    else:
        missing = set(required_columns.keys()) - set(mapping.keys())
        st.warning(f"⚠️ Please map all required columns. Missing: {', '.join(missing)}")
        return None


def render_data_stats(df: pd.DataFrame) -> None:
    """
    Render statistics about the uploaded data.
    
    Args:
        df: DataFrame to analyze
    """
    st.markdown("### 📈 Data Statistics")
    
    # Numeric columns statistics
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        st.markdown("**Numeric Columns**")
        st.dataframe(df[numeric_cols].describe(), use_container_width=True)
    
    # Categorical columns statistics
    categorical_cols = df.select_dtypes(include=['object']).columns
    if len(categorical_cols) > 0:
        st.markdown("**Categorical Columns**")
        for col in categorical_cols[:5]:  # Show first 5 categorical columns
            unique_count = df[col].nunique()
            st.markdown(f"- **{col}**: {unique_count} unique values")
            if unique_count <= 10:
                value_counts = df[col].value_counts().head(5)
                st.write(value_counts)

