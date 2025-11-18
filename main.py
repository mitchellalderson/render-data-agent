"""
ICP Analysis Dashboard - Main Application

A Streamlit web app that analyzes customer data from PostgreSQL and CSV sources
using LLM insights to identify Ideal Customer Profile matches.
"""

import streamlit as st
import pandas as pd
from typing import Optional

# Import our custom modules
from src.config import config
from src.database import get_database_connection
from src.styles import get_render_css, render_header, render_section_header
from src.data_processing import DataCleaner, SchemaMapper, DataValidator
from src.llm_client import LLMClient, test_connection
from src.icp_analyzer import ICPAnalyzer
from src.segmentation import CustomerSegmenter, CustomerComparator, ProfileGenerator
from components.data_upload import render_csv_uploader, render_data_stats
from components.data_processing_ui import (
    render_data_quality_report,
    render_data_cleaning_options,
    render_schema_mapper,
    render_column_comparison,
    render_data_transformation_options
)
from components.analysis_ui import (
    render_analysis_configuration,
    render_analysis_summary,
    render_score_distribution,
    render_confidence_breakdown,
    render_top_matches,
    render_patterns,
    render_recommendations,
    render_data_quality_notes,
    render_export_options,
    render_full_results_table
)
from components.advanced_visualizations import (
    render_segment_overview,
    render_segment_details,
    render_customer_comparison,
    render_customer_profile,
    render_trend_analysis,
    render_attribute_heatmap,
    render_insights_summary
)

# Page configuration
st.set_page_config(
    page_title="ICP Analysis Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom CSS
st.markdown(get_render_css(), unsafe_allow_html=True)


def check_configuration() -> bool:
    """
    Check if the app is properly configured.
    
    Returns:
        True if configured, False otherwise
    """
    errors = config.validate()
    if errors:
        st.error("⚠️ Configuration Error")
        st.markdown("The following configuration issues were found:")
        for error in errors:
            st.markdown(f"- {error}")
        st.info("""
        Please create a `.env` file in the project root with the required configuration.
        You can copy `.env.template` as a starting point.
        """)
        return False
    return True


def render_sidebar() -> dict:
    """
    Render the sidebar with configuration and options.
    
    Returns:
        Dictionary with user selections
    """
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")
        
        # Database connection section
        st.markdown("### Database Connection")
        
        db = get_database_connection()
        success, message = db.test_connection()
        
        if success:
            st.success("✅ Connected to database")
            
            # Table selection
            tables = db.get_tables()
            if tables:
                selected_table = st.selectbox(
                    "Select Signups Table",
                    options=tables,
                    help="Choose the table containing user signup data"
                )
                
                # Show row count
                if selected_table:
                    row_count = db.get_row_count(selected_table)
                    st.metric("Total Signups", f"{row_count:,}")
            else:
                st.warning("No tables found in database")
                selected_table = None
        else:
            st.error("❌ Database connection failed")
            st.code(message, language=None)
            selected_table = None
        
        st.markdown("---")
        
        # Data options
        st.markdown("### Data Options")
        
        limit_data = st.checkbox(
            "Limit number of records",
            value=False,
            help="Limit the number of records to process"
        )
        
        record_limit = None
        if limit_data:
            record_limit = st.number_input(
                "Max Records",
                min_value=10,
                max_value=10000,
                value=1000,
                step=100
            )
        
        st.markdown("---")
        
        # Analysis options
        st.markdown("### Analysis Options")
        
        analysis_mode = st.radio(
            "Analysis Mode",
            options=["Quick Preview", "Full Analysis"],
            help="Quick preview shows basic comparison, Full analysis uses LLM"
        )
        
        return {
            "db_connected": success,
            "selected_table": selected_table,
            "record_limit": record_limit,
            "analysis_mode": analysis_mode
        }


def render_database_preview(table_name: str, limit: Optional[int] = None):
    """
    Render a preview of the database table.
    
    Args:
        table_name: Name of the table to preview
        limit: Optional limit on number of rows
    """
    st.markdown(render_section_header(
        "📊 Database Preview",
        "User signup data from PostgreSQL"
    ), unsafe_allow_html=True)
    
    db = get_database_connection()
    
    # Get table info
    with st.expander("🔍 Table Schema", expanded=False):
        table_info = db.get_table_info(table_name)
        if not table_info.empty:
            st.dataframe(table_info, use_container_width=True, hide_index=True)
    
    # Query data
    df = db.query_signups(table_name, limit=limit or 100)
    
    if not df.empty:
        # Show metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Records", len(df))
        with col2:
            st.metric("Columns", len(df.columns))
        with col3:
            # Calculate unique values only for hashable columns
            try:
                # Exclude columns with unhashable types (like dicts from JSONB)
                hashable_cols = []
                for col in df.columns:
                    try:
                        df[col].nunique()
                        hashable_cols.append(col)
                    except TypeError:
                        pass
                unique_vals = df[hashable_cols].nunique().sum() if hashable_cols else 0
                st.metric("Unique Values", unique_vals)
            except Exception:
                st.metric("Unique Values", "N/A")
        with col4:
            completeness = ((1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100)
            st.metric("Completeness", f"{completeness:.1f}%")
        
        # Show data preview
        with st.expander("👁️ Data Preview", expanded=True):
            st.dataframe(df.head(20), use_container_width=True)
        
        return df
    else:
        st.warning("No data found in the selected table.")
        return None


def render_comparison_view(signup_data: pd.DataFrame, customer_data: pd.DataFrame):
    """
    Render a comparison view of the two datasets.
    
    Args:
        signup_data: DataFrame with signup data
        customer_data: DataFrame with customer data
    """
    st.markdown(render_section_header(
        "🔄 Data Comparison",
        "Side-by-side view of your datasets"
    ), unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Signup Data")
        st.metric("Records", len(signup_data))
        st.metric("Columns", len(signup_data.columns))
        with st.expander("View Columns"):
            st.write(list(signup_data.columns))
    
    with col2:
        st.markdown("#### Customer Data")
        st.metric("Records", len(customer_data))
        st.metric("Columns", len(customer_data.columns))
        with st.expander("View Columns"):
            st.write(list(customer_data.columns))
    
    # Show column overlap
    signup_cols = set(signup_data.columns)
    customer_cols = set(customer_data.columns)
    common_cols = signup_cols & customer_cols
    
    if common_cols:
        st.success(f"✅ Found {len(common_cols)} common columns: {', '.join(common_cols)}")
    else:
        st.info("ℹ️ No common column names found. You may need to map columns for analysis.")


def navigate_to_tab(tab_name: str):
    """
    Navigate to a specific tab by setting session state.
    
    Args:
        tab_name: Name of the tab to navigate to
    """
    st.session_state["active_tab"] = tab_name
    st.rerun()


def get_active_tab() -> str:
    """
    Get the currently active tab from session state.
    
    Returns:
        Active tab name, defaults to "data_sources"
    """
    if "active_tab" not in st.session_state:
        st.session_state["active_tab"] = "data_sources"
    return st.session_state["active_tab"]


def main():
    """Main application entry point."""
    
    # Render header
    st.markdown(render_header(), unsafe_allow_html=True)
    
    # Check configuration
    if not check_configuration():
        st.stop()
    
    # Render sidebar and get options
    options = render_sidebar()
    
    # Get active tab from session state
    active_tab = get_active_tab()
    
    # Tab configuration
    tab_config = {
        "data_sources": "📥 Data Sources",
        "data_processing": "🧹 Data Processing",
        "analysis": "🔍 Analysis",
        "results": "📊 Results",
        "advanced": "🎯 Advanced"
    }
    
    # Create custom tab bar using pills
    st.markdown("### ")  # Spacing
    selected_tab = st.pills(
        "Navigation",
        options=list(tab_config.keys()),
        format_func=lambda x: tab_config[x],
        default=active_tab,
        label_visibility="collapsed"
    )
    
    # Update active tab if selection changed
    if selected_tab != active_tab:
        st.session_state["active_tab"] = selected_tab
        st.rerun()
    
    st.markdown("---")
    
    # Render content based on active tab
    if active_tab == "data_sources":
        st.markdown("## 📥 Data Sources")
        
        # Clear instructions at the top
        st.info("""
        **👋 Welcome!** To analyze your customer data, you need to provide **two datasets**:
        
        **Step 1:** Upload your **Customer Data CSV** (the customers you want to analyze)  
        **Step 2:** Connect your **Signup Database** (represents your ideal customer profile)
        
        Once both are loaded, you can proceed to analysis! 🚀
        """)
        
        st.markdown("---")
        
        # STEP 1: CSV upload section (moved to top)
        st.markdown("### Step 1: Upload Customer Data CSV 📤")
        st.markdown("Upload a CSV file containing the customers you want to analyze against your ICP.")
        
        customer_df = render_csv_uploader(key="customer_csv")
        
        if customer_df is not None:
            st.session_state["customer_data"] = customer_df
            st.success("✅ **Customer data loaded successfully!**")
            render_data_stats(customer_df)
        else:
            st.warning("⬆️ Please upload your customer data CSV file to continue")
        
        st.markdown("---")
        
        # STEP 2: Database section (moved to second)
        st.markdown("### Step 2: Connect Signup Database 🔌")
        st.markdown("Configure your PostgreSQL connection in the sidebar to load signup data (your ICP).")
        
        if options["db_connected"] and options["selected_table"]:
            signup_df = render_database_preview(
                options["selected_table"],
                options["record_limit"]
            )
            
            # Store in session state
            if signup_df is not None:
                st.session_state["signup_data"] = signup_df
                st.success("✅ **Signup data connected successfully!**")
        else:
            st.warning("⬅️ Please configure database connection in the **sidebar** (left side)")
            st.info("💡 **Tip:** Make sure your PostgreSQL database is running and credentials are set in your `.env` file")
            signup_df = None
        
        st.markdown("---")
        
        # Show status and next steps
        signup_loaded = "signup_data" in st.session_state and st.session_state["signup_data"] is not None
        customer_loaded = "customer_data" in st.session_state and st.session_state["customer_data"] is not None
        
        st.markdown("### 🎯 Ready to Analyze?")
        
        col1, col2 = st.columns(2)
        with col1:
            if customer_loaded:
                st.success("✅ Customer data loaded")
            else:
                st.error("❌ Customer data not loaded")
        
        with col2:
            if signup_loaded:
                st.success("✅ Signup data connected")
            else:
                st.error("❌ Signup data not connected")
        
        # Show comparison if both datasets are loaded
        if signup_loaded and customer_loaded:
            signup_df = st.session_state["signup_data"]
            customer_df = st.session_state["customer_data"]
            
            st.markdown("---")
            
            with st.expander("📊 View Data Comparison", expanded=False):
                render_comparison_view(signup_df, customer_df)
            
            st.markdown("---")
            # Navigation buttons
            st.success("🎉 **Both datasets loaded successfully!** You're ready to proceed.")
            st.markdown("**Choose your next step:**")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🧹 Clean & Process Data First", type="secondary", use_container_width=True, help="Recommended: Clean and align your data for better results"):
                    navigate_to_tab("data_processing")
            with col2:
                if st.button("🚀 Skip to Analysis", type="primary", use_container_width=True, help="Start ICP analysis immediately"):
                    navigate_to_tab("analysis")
        else:
            st.markdown("---")
            st.info("⬆️ **Complete both steps above to continue**")
    
    elif active_tab == "data_processing":
        st.markdown("## Data Processing & Schema Mapping")
        st.markdown("Clean, transform, and align your datasets for analysis.")
        
        # Check if data is loaded
        if "signup_data" not in st.session_state or "customer_data" not in st.session_state:
            st.info("📋 Please load both datasets in the Data Sources tab first.")
            st.stop()
        
        signup_data = st.session_state["signup_data"]
        customer_data = st.session_state["customer_data"]
        
        # Data quality reports
        col1, col2 = st.columns(2)
        
        with col1:
            render_data_quality_report(signup_data, "📊 Signup Data Quality")
        
        with col2:
            render_data_quality_report(customer_data, "📊 Customer Data Quality")
        
        st.markdown("---")
        
        # Column comparison
        render_column_comparison(signup_data, customer_data, "Signup Data", "Customer Data")
        
        st.markdown("---")
        
        # Processing options
        processing_tab1, processing_tab2, processing_tab3 = st.tabs([
            "Clean Data", "Map Schemas", "Transform Data"
        ])
        
        with processing_tab1:
            st.markdown("## Clean Your Data")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Signup Data")
                cleaned_signup = render_data_cleaning_options(signup_data, "signup")
                if cleaned_signup is not None:
                    st.session_state["signup_data_cleaned"] = cleaned_signup
                    st.session_state["signup_data"] = cleaned_signup
                    st.rerun()
            
            with col2:
                st.markdown("#### Customer Data")
                cleaned_customer = render_data_cleaning_options(customer_data, "customer")
                if cleaned_customer is not None:
                    st.session_state["customer_data_cleaned"] = cleaned_customer
                    st.session_state["customer_data"] = cleaned_customer
                    st.rerun()
        
        with processing_tab2:
            st.markdown("## Map Column Schemas")
            st.markdown("Align column names between datasets for easier comparison.")
            
            mapping = render_schema_mapper(
                signup_data, 
                customer_data,
                "Signup Data",
                "Customer Data"
            )
            
            if mapping:
                if st.button("✅ Apply Mapping to Customer Data", type="primary"):
                    with st.spinner("Applying schema mapping..."):
                        customer_mapped = SchemaMapper.apply_mapping(
                            customer_data,
                            mapping,
                            keep_unmapped=True
                        )
                        st.session_state["customer_data"] = customer_mapped
                        st.session_state["schema_mapping_applied"] = True
                        st.success("✅ Schema mapping applied successfully!")
                        st.rerun()
        
        with processing_tab3:
            st.markdown("## Transform Data")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Signup Data")
                transformed_signup = render_data_transformation_options(signup_data)
                if transformed_signup is not None:
                    st.session_state["signup_data"] = transformed_signup
            
            with col2:
                st.markdown("#### Customer Data")
                transformed_customer = render_data_transformation_options(customer_data)
                if transformed_customer is not None:
                    st.session_state["customer_data"] = transformed_customer
        
        # Navigation at bottom of Data Processing tab
        st.markdown("---")
        st.markdown("### 🎯 Ready for Analysis?")
        st.info("💡 Your data is ready! Proceed to the Analysis tab to run ICP matching.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Back to Data Sources", type="secondary", use_container_width=True):
                navigate_to_tab("data_sources")
        with col2:
            if st.button("➡️ Continue to Analysis", type="primary", use_container_width=True):
                navigate_to_tab("analysis")
                st.balloons()
    
    elif active_tab == "analysis":
        st.markdown("## 🤖 ICP Analysis")
        
        # Check if data is loaded
        if "signup_data" not in st.session_state or "customer_data" not in st.session_state:
            st.info("📋 Please load both datasets in the Data Sources tab first.")
            st.stop()
        
        signup_data = st.session_state["signup_data"]
        customer_data = st.session_state["customer_data"]
        
        # Check LLM connection
        st.markdown("### 🔌 LLM Connection")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Show available providers
            openai_key = config.get("OPENAI_API_KEY")
            anthropic_key = config.get("ANTHROPIC_API_KEY")
            
            if openai_key:
                st.success("✅ OpenAI API key configured")
            if anthropic_key:
                st.success("✅ Anthropic API key configured")
            
            if not openai_key and not anthropic_key:
                st.error("❌ No LLM API key found. Please configure OPENAI_API_KEY or ANTHROPIC_API_KEY in your .env file.")
                st.stop()
        
        with col2:
            if st.button("🧪 Test Connection"):
                with st.spinner("Testing LLM connection..."):
                    if test_connection():
                        st.success("✅ Connected!")
                    else:
                        st.error("❌ Connection failed")
        
        st.markdown("---")
        
        # Analysis configuration
        config_params = render_analysis_configuration()
        
        st.markdown("---")
        
        # Data summary
        st.markdown("### 📊 Data to Analyze")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Signup Records", len(signup_data))
        with col2:
            st.metric("Customer Records", len(customer_data))
        
        # Run analysis button
        if st.button("🚀 Run ICP Analysis", type="primary", use_container_width=True):
            with st.spinner("Running ICP analysis... This may take a minute."):
                try:
                    # Create LLM client
                    llm_client = LLMClient(
                        provider=config_params["provider"],
                        model=config_params["model"],
                        temperature=config_params["temperature"]
                    )
                    
                    # Create analyzer
                    analyzer = ICPAnalyzer(llm_client=llm_client)
                    
                    # Run analysis
                    result = analyzer.analyze(
                        signup_data=signup_data,
                        customer_data=customer_data,
                        icp_criteria=config_params["custom_criteria"],
                        max_customers=config_params["max_customers"]
                    )
                    
                    # Get statistics
                    stats = analyzer.get_match_statistics(result)
                    
                    # Get top matches
                    top_matches = analyzer.get_top_matches(result, top_n=10, min_score=60.0)
                    
                    # Export to DataFrame
                    results_df = analyzer.export_results_to_dataframe(result)
                    
                    # Phase 4: Generate segments
                    segments_by_score = CustomerSegmenter.segment_by_score(result.matches)
                    segments_by_confidence = CustomerSegmenter.segment_by_confidence(result.matches)
                    
                    # Store in session state
                    st.session_state["analysis_result"] = result
                    st.session_state["analysis_stats"] = stats
                    st.session_state["top_matches"] = top_matches
                    st.session_state["results_df"] = results_df
                    st.session_state["segments_by_score"] = segments_by_score
                    st.session_state["segments_by_confidence"] = segments_by_confidence
                    
                    st.success("✅ Analysis complete! View results in the Results tab.")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Analysis failed: {str(e)}")
                    st.exception(e)
        
        # Show if analysis already run
        if "analysis_result" in st.session_state:
            st.markdown("---")
            st.markdown("### 📊 View Your Results")
            st.success("✅ Analysis complete! Your ICP matches are ready.")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("⬅️ Back to Data Processing", type="secondary", use_container_width=True):
                    navigate_to_tab("data_processing")
            with col2:
                if st.button("➡️ View Results", type="primary", use_container_width=True):
                    navigate_to_tab("results")
        else:
            st.markdown("---")
            st.info("💡 Run the analysis above to see your ICP matches.")
    
    elif active_tab == "results":
        st.markdown("## 📊 Analysis Results")
        
        # Check if analysis has been run
        if "analysis_result" not in st.session_state:
            st.info("🔍 No analysis results yet. Run the analysis in the **Analysis** tab first.")
            st.stop()
        
        result = st.session_state["analysis_result"]
        stats = st.session_state["analysis_stats"]
        top_matches = st.session_state["top_matches"]
        results_df = st.session_state["results_df"]
        
        # Summary
        render_analysis_summary(result, stats)
        
        st.markdown("---")
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            render_score_distribution(result)
        
        with col2:
            render_confidence_breakdown(result, stats)
        
        st.markdown("---")
        
        # Top matches
        render_top_matches(top_matches, top_n=10)
        
        st.markdown("---")
        
        # Patterns and recommendations
        col1, col2 = st.columns(2)
        
        with col1:
            render_patterns(result.patterns)
        
        with col2:
            render_recommendations(result.recommendations)
        
        # Data quality notes
        render_data_quality_notes(result.data_quality_notes)
        
        st.markdown("---")
        
        # Export options
        render_export_options(result, results_df)
        
        st.markdown("---")
        
        # Full results table
        render_full_results_table(results_df)
        
        # Navigation at bottom of Results tab
        st.markdown("---")
        st.markdown("### 🎯 Explore Advanced Features")
        st.info("💡 Dive deeper with customer segmentation, comparisons, and detailed profiles!")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Back to Analysis", type="secondary", use_container_width=True):
                navigate_to_tab("analysis")
        with col2:
            if st.button("➡️ Go to Advanced Analysis", type="primary", use_container_width=True):
                navigate_to_tab("advanced")
    
    elif active_tab == "advanced":
        st.markdown("## 🎯 Advanced Analysis")
        
        # Check if analysis has been run
        if "analysis_result" not in st.session_state:
            st.info("🔍 No analysis results yet. Run the analysis in the **Analysis** tab first.")
            st.stop()
        
        result = st.session_state["analysis_result"]
        stats = st.session_state["analysis_stats"]
        segments_by_score = st.session_state.get("segments_by_score", [])
        segments_by_confidence = st.session_state.get("segments_by_confidence", [])
        customer_data = st.session_state.get("customer_data")
        
        # Advanced features menu
        advanced_view = st.selectbox(
            "Select View",
            [
                "🎯 Customer Segmentation",
                "🔀 Customer Comparison",
                "👤 Detailed Profiles",
                "📈 Trend Analysis",
                "🔥 Attribute Analysis",
                "💎 Key Insights"
            ]
        )
        
        st.markdown("---")
        
        if advanced_view == "🎯 Customer Segmentation":
            st.markdown("## Customer Segmentation")
            
            segment_type = st.radio(
                "Segment By",
                ["ICP Score Ranges", "Confidence Level"],
                horizontal=True
            )
            
            if segment_type == "ICP Score Ranges":
                segments = segments_by_score
            else:
                segments = segments_by_confidence
            
            if segments:
                render_segment_overview(segments)
                st.markdown("---")
                render_segment_details(segments)
                st.markdown("---")
                render_insights_summary(segments, stats["total_analyzed"])
            else:
                st.info("No segments available")
        
        elif advanced_view == "🔀 Customer Comparison":
            st.markdown("## Customer Comparison")
            
            # Select customers to compare
            available_matches = result.matches[:20]  # Limit to top 20
            
            selected_companies = st.multiselect(
                "Select customers to compare (2-5)",
                options=[m.company_name for m in available_matches],
                max_selections=5
            )
            
            if len(selected_companies) >= 2:
                # Get customer IDs
                selected_ids = [
                    m.customer_id for m in available_matches 
                    if m.company_name in selected_companies
                ]
                
                # Create comparison
                comparison_df = CustomerComparator.compare_customers(
                    selected_ids,
                    result.matches,
                    customer_data
                )
                
                render_customer_comparison(comparison_df)
                
                # Attribute comparison
                if st.checkbox("Show Attribute Comparison"):
                    selected_matches = [m for m in result.matches if m.company_name in selected_companies]
                    attr_df = CustomerComparator.get_attribute_comparison(selected_matches)
                    render_attribute_heatmap(attr_df)
            else:
                st.info("👆 Select at least 2 customers to compare")
        
        elif advanced_view == "👤 Detailed Profiles":
            st.markdown("## Detailed Customer Profiles")
            
            # Select customer
            available_matches = result.matches[:50]
            
            selected_customer = st.selectbox(
                "Select a customer",
                options=[f"{m.company_name} (Score: {m.score:.0f})" for m in available_matches]
            )
            
            if selected_customer:
                # Extract company name
                company_name = selected_customer.split(" (Score:")[0]
                
                # Find match
                match = next((m for m in available_matches if m.company_name == company_name), None)
                
                if match:
                    # Generate profile
                    profile = ProfileGenerator.generate_profile(
                        match.customer_id,
                        match,
                        customer_data,
                        result.matches
                    )
                    
                    # Get rank
                    sorted_matches = sorted(result.matches, key=lambda x: x.score, reverse=True)
                    rank = next((i+1 for i, m in enumerate(sorted_matches) if m.customer_id == match.customer_id), None)
                    
                    render_customer_profile(profile, rank)
        
        elif advanced_view == "📈 Trend Analysis":
            st.markdown("## Trend Analysis")
            
            segment_type = st.radio(
                "View Trends By",
                ["ICP Score Ranges", "Confidence Level"],
                horizontal=True
            )
            
            segments = segments_by_score if segment_type == "ICP Score Ranges" else segments_by_confidence
            
            if segments:
                render_trend_analysis(segments)
                
                # Additional metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    high_value = sum(s.size for s in segments if s.avg_score >= 80)
                    st.metric("High-Value Customers", high_value)
                
                with col2:
                    avg_overall = sum(s.avg_score * s.size for s in segments) / sum(s.size for s in segments)
                    st.metric("Overall Avg Score", f"{avg_overall:.1f}")
                
                with col3:
                    largest_segment = max(segments, key=lambda s: s.size)
                    st.metric("Largest Segment", largest_segment.name)
            else:
                st.info("No trend data available")
        
        elif advanced_view == "🔥 Attribute Analysis":
            st.markdown("## Attribute Analysis")
            
            # Top customers for attribute analysis
            top_n = st.slider("Number of customers to analyze", 5, 30, 15)
            top_customers = result.matches[:top_n]
            
            attr_df = CustomerComparator.get_attribute_comparison(top_customers)
            
            if not attr_df.empty:
                render_attribute_heatmap(attr_df)
                
                st.markdown("---")
                st.markdown("### 📊 Attribute Statistics")
                
                # Calculate attribute frequency
                attr_cols = [c for c in attr_df.columns if c not in ["Customer", "Score"]]
                attr_counts = {}
                
                for col in attr_cols:
                    count = (attr_df[col] == "✓").sum()
                    attr_counts[col] = count
                
                # Display top attributes
                sorted_attrs = sorted(attr_counts.items(), key=lambda x: x[1], reverse=True)[:10]
                
                attr_freq_df = pd.DataFrame(sorted_attrs, columns=["Attribute", "Count"])
                attr_freq_df["Frequency %"] = (attr_freq_df["Count"] / len(attr_df) * 100).round(1)
                
                st.dataframe(attr_freq_df, use_container_width=True, hide_index=True)
            else:
                st.info("No attribute data available")
        
        elif advanced_view == "💎 Key Insights":
            st.markdown("## Key Insights & Recommendations")
            
            segment_type = st.radio(
                "Analyze By",
                ["ICP Score Ranges", "Confidence Level"],
                horizontal=True
            )
            
            segments = segments_by_score if segment_type == "ICP Score Ranges" else segments_by_confidence
            
            if segments:
                render_insights_summary(segments, stats["total_analyzed"])
                
                st.markdown("---")
                st.markdown("### 📋 Action Items")
                
                # Generate action items based on analysis
                high_quality = sum(s.size for s in segments if s.avg_score >= 70)
                medium_quality = sum(s.size for s in segments if 50 <= s.avg_score < 70)
                low_quality = sum(s.size for s in segments if s.avg_score < 50)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Immediate Actions:**")
                    st.success(f"1. Engage {high_quality} high-quality prospects immediately")
                    st.info(f"2. Qualify {medium_quality} medium-quality leads further")
                    st.warning(f"3. Nurture or deprioritize {low_quality} low-fit prospects")
                
                with col2:
                    st.markdown("**Strategic Recommendations:**")
                    if result.patterns.get("common_industries"):
                        industries = ", ".join(result.patterns["common_industries"][:3])
                        st.markdown(f"- Focus outreach on: {industries}")
                    if result.patterns.get("common_sizes"):
                        sizes = ", ".join(result.patterns["common_sizes"][:2])
                        st.markdown(f"- Target company sizes: {sizes}")
                    if result.patterns.get("key_indicators"):
                        indicator = result.patterns["key_indicators"][0]
                        st.markdown(f"- Look for: {indicator}")
            else:
                st.info("No insights available")
        
        # Navigation at bottom of Advanced tab
        st.markdown("---")
        st.markdown("### 🎉 Analysis Complete!")
        st.success("✅ You've explored all the features! Export your results from the Results tab.")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("⬅️ Back to Results", type="secondary", use_container_width=True):
                navigate_to_tab("results")
        with col2:
            if st.button("📥 Go to Data Sources", type="secondary", use_container_width=True):
                navigate_to_tab("data_sources")
        with col3:
            if st.button("🔄 Start New Analysis", type="primary", use_container_width=True):
                # Clear session state for new analysis
                for key in ["analysis_result", "analysis_stats", "top_matches", "results_df", 
                           "segments_by_score", "segments_by_confidence"]:
                    if key in st.session_state:
                        del st.session_state[key]
                navigate_to_tab("data_sources")


if __name__ == "__main__":
    main()
