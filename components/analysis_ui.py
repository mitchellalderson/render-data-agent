"""UI components for ICP analysis and results display."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from typing import Dict, List, Optional

from src.icp_analyzer import ICPAnalysisResult, ICPMatch
from src.utils import escape_markdown


def render_analysis_configuration() -> Dict[str, any]:
    """
    Render analysis configuration options.
    
    Returns:
        Dictionary with configuration settings
    """
    st.markdown("### ⚙️ Analysis Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        provider = st.selectbox(
            "LLM Provider",
            options=["openai", "anthropic"],
            help="Choose which LLM provider to use for analysis"
        )
        
        max_customers = st.slider(
            "Max Customers to Analyze",
            min_value=10,
            max_value=100,
            value=50,
            step=10,
            help="Limit analysis to this many customers (reduces cost and time)"
        )
    
    with col2:
        model_options = {
            "openai": ["gpt-4-turbo-preview", "gpt-4", "gpt-3.5-turbo"],
            "anthropic": ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-sonnet-20240229"]
        }
        
        model = st.selectbox(
            "Model",
            options=model_options[provider],
            help="Choose which model to use"
        )
        
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.1,
            help="Lower = more focused, Higher = more creative"
        )
    
    # Optional ICP criteria
    with st.expander("🎯 Define Custom ICP Criteria (Optional)", expanded=False):
        st.markdown("Define specific criteria for your Ideal Customer Profile. Leave blank to let the LLM infer from signup data.")
        
        use_custom = st.checkbox("Use custom ICP criteria")
        
        custom_criteria = None
        if use_custom:
            industries = st.text_input("Target Industries (comma-separated)", placeholder="SaaS, Technology, E-commerce")
            company_sizes = st.text_input("Company Sizes (comma-separated)", placeholder="50-200, 200-1000")
            attributes = st.text_area("Key Attributes", placeholder="Fast-growing\nTechnical team\nData-driven")
            
            if industries or company_sizes or attributes:
                custom_criteria = {
                    "industries": [i.strip() for i in industries.split(",") if i.strip()] if industries else [],
                    "company_sizes": [s.strip() for s in company_sizes.split(",") if s.strip()] if company_sizes else [],
                    "key_attributes": [a.strip() for a in attributes.split("\n") if a.strip()] if attributes else []
                }
    
    return {
        "provider": provider,
        "model": model,
        "temperature": temperature,
        "max_customers": max_customers,
        "custom_criteria": custom_criteria if use_custom else None
    }


def render_analysis_progress(status: str, progress: float = 0.0) -> None:
    """
    Render analysis progress indicator.
    
    Args:
        status: Status message
        progress: Progress value (0-1)
    """
    st.markdown("### 🔄 Analysis in Progress")
    st.progress(progress)
    st.info(f"**Status:** {status}")


def render_analysis_summary(result: ICPAnalysisResult, stats: Dict[str, any]) -> None:
    """
    Render high-level analysis summary.
    
    Args:
        result: Analysis result
        stats: Statistics dictionary
    """
    st.markdown("### 📊 Analysis Summary")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Analyzed", stats["total_analyzed"])
    
    with col2:
        st.metric("Avg ICP Score", f"{stats['avg_score']:.1f}")
    
    with col3:
        st.metric("Strong Matches (>80)", stats["matches_above_80"])
    
    with col4:
        st.metric("Good Matches (>60)", stats["matches_above_60"])
    
    # Executive summary
    if result.summary:
        st.markdown("#### 📝 Executive Summary")
        st.info(result.summary)


def render_score_distribution(result: ICPAnalysisResult) -> None:
    """
    Render ICP score distribution chart.
    
    Args:
        result: Analysis result
    """
    if not result.matches:
        st.warning("No matches to display")
        return
    
    st.markdown("### 📈 Score Distribution")
    
    # Prepare data
    scores = [m.score for m in result.matches]
    
    # Create histogram
    fig = go.Figure(data=[
        go.Histogram(
            x=scores,
            nbinsx=20,
            marker_color='#5469d4',
            hovertemplate='Score: %{x}<br>Count: %{y}<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title="ICP Score Distribution",
        xaxis_title="ICP Score",
        yaxis_title="Count",
        showlegend=False,
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_confidence_breakdown(result: ICPAnalysisResult, stats: Dict[str, any]) -> None:
    """
    Render confidence level breakdown.
    
    Args:
        result: Analysis result
        stats: Statistics dictionary
    """
    st.markdown("### 🎯 Confidence Breakdown")
    
    # Prepare data
    confidence_data = {
        "High": stats["high_confidence_count"],
        "Medium": stats["medium_confidence_count"],
        "Low": stats["low_confidence_count"]
    }
    
    # Create pie chart
    fig = go.Figure(data=[
        go.Pie(
            labels=list(confidence_data.keys()),
            values=list(confidence_data.values()),
            marker_colors=['#10b981', '#f59e0b', '#ef4444'],
            hole=0.4,
            hovertemplate='%{label}<br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title="Confidence Level Distribution",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_top_matches(matches: List[ICPMatch], top_n: int = 10) -> None:
    """
    Render top ICP matches.
    
    Args:
        matches: List of matches
        top_n: Number of top matches to show
    """
    st.markdown(f"### 🏆 Top {top_n} ICP Matches")
    
    if not matches:
        st.warning("No matches to display")
        return
    
    for i, match in enumerate(matches[:top_n], 1):
        # Color based on score
        if match.score >= 80:
            color = "🟢"
        elif match.score >= 60:
            color = "🟡"
        else:
            color = "🔴"
        
        with st.expander(
            f"{color} #{i} - {match.company_name} (Score: {match.score:.0f})",
            expanded=(i <= 3)
        ):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Customer ID:** {match.customer_id}")
                st.markdown(f"**ICP Score:** {match.score:.1f}/100")
                st.markdown(f"**Confidence:** {match.confidence.title()}")
                
                st.markdown("**Reasoning:**")
                st.write(match.reasoning)
            
            with col2:
                if match.matching_attributes:
                    st.markdown("**✅ Matching Attributes:**")
                    st.markdown(f"*{len(match.matching_attributes)} attributes align with ICP*")
                    for idx, attr in enumerate(match.matching_attributes, 1):
                        # Parse attribute to show more detail
                        if ":" in attr:
                            # Attribute already has detail (e.g., "Industry: Technology")
                            st.success(f"{idx}. {escape_markdown(attr)}")
                        else:
                            # Simple attribute name
                            st.success(f"{idx}. {escape_markdown(attr)}")
                else:
                    st.markdown("**✅ Matching Attributes:**")
                    st.caption("*No specific matches identified*")
                
                if match.gaps:
                    st.markdown("**⚠️ Gaps / Missing:**")
                    st.markdown(f"*{len(match.gaps)} areas need improvement*")
                    for idx, gap in enumerate(match.gaps, 1):
                        # Parse gap to show more detail
                        if ":" in gap:
                            # Gap already has detail (e.g., "Missing: Team size info")
                            st.warning(f"{idx}. {escape_markdown(gap)}")
                        else:
                            # Simple gap name
                            st.warning(f"{idx}. Missing or weak: {escape_markdown(gap)}")
                else:
                    st.markdown("**⚠️ Gaps / Missing:**")
                    st.caption("*No significant gaps identified*")


def render_patterns(patterns: Dict[str, any]) -> None:
    """
    Render identified patterns.
    
    Args:
        patterns: Patterns dictionary
    """
    st.markdown("### 🔍 Identified Patterns")
    
    if not patterns:
        st.info("No patterns identified")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        if patterns.get("common_industries"):
            st.markdown("**Common Industries:**")
            for industry in patterns["common_industries"]:
                st.markdown(f"- {industry}")
        
        if patterns.get("common_sizes"):
            st.markdown("**Common Company Sizes:**")
            for size in patterns["common_sizes"]:
                st.markdown(f"- {size}")
    
    with col2:
        if patterns.get("common_attributes"):
            st.markdown("**Common Attributes:**")
            for attr in patterns["common_attributes"]:
                st.markdown(f"- {escape_markdown(attr)}")
        
        if patterns.get("key_indicators"):
            st.markdown("**Key Success Indicators:**")
            for indicator in patterns["key_indicators"]:
                st.markdown(f"- {escape_markdown(indicator)}")


def render_recommendations(recommendations: List[str]) -> None:
    """
    Render actionable recommendations.
    
    Args:
        recommendations: List of recommendations
    """
    st.markdown("### 💡 Recommendations")
    
    if not recommendations:
        st.info("No recommendations generated")
        return
    
    for i, rec in enumerate(recommendations, 1):
        st.markdown(f"**{i}.** {rec}")


def render_data_quality_notes(notes: List[str]) -> None:
    """
    Render data quality notes.
    
    Args:
        notes: List of data quality notes
    """
    if not notes:
        return
    
    with st.expander("⚠️ Data Quality Notes", expanded=False):
        for note in notes:
            st.warning(note)


def render_export_options(result: ICPAnalysisResult, df: pd.DataFrame) -> None:
    """
    Render export options for analysis results.
    
    Args:
        result: Analysis result
        df: Results DataFrame
    """
    st.markdown("### 💾 Export Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # CSV export
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name="icp_analysis_results.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        # JSON export
        json_str = json.dumps(result.to_dict(), indent=2)
        st.download_button(
            label="📥 Download JSON",
            data=json_str,
            file_name="icp_analysis_results.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col3:
        # Excel export (if openpyxl available)
        try:
            from io import BytesIO
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='ICP Analysis', index=False)
            
            st.download_button(
                label="📥 Download Excel",
                data=buffer.getvalue(),
                file_name="icp_analysis_results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        except ImportError:
            st.button("📥 Download Excel", disabled=True, help="openpyxl not installed", use_container_width=True)


def render_full_results_table(df: pd.DataFrame) -> None:
    """
    Render full results table.
    
    Args:
        df: Results DataFrame
    """
    st.markdown("### 📋 Full Results Table")
    
    # Add filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        min_score = st.slider("Minimum Score", 0, 100, 0, 10)
    
    with col2:
        confidence_filter = st.multiselect(
            "Confidence Level",
            options=["high", "medium", "low"],
            default=["high", "medium", "low"]
        )
    
    with col3:
        search = st.text_input("Search Company", "")
    
    # Apply filters
    filtered_df = df.copy()
    
    if min_score > 0:
        filtered_df = filtered_df[filtered_df["ICP Score"] >= min_score]
    
    if confidence_filter:
        filtered_df = filtered_df[filtered_df["Confidence"].isin(confidence_filter)]
    
    if search:
        filtered_df = filtered_df[
            filtered_df["Company Name"].str.contains(search, case=False, na=False)
        ]
    
    # Display options
    show_details = st.checkbox("Show detailed attribute and gap information", value=False)
    
    # Display
    if show_details and not filtered_df.empty:
        # Show with expandable details
        st.caption(f"Showing {len(filtered_df)} of {len(df)} results - Click rows below for details")
        
        for idx, row in filtered_df.iterrows():
            # Color coding based on score
            if row["ICP Score"] >= 80:
                emoji = "🟢"
            elif row["ICP Score"] >= 60:
                emoji = "🟡"
            else:
                emoji = "🔴"
            
            with st.expander(
                f"{emoji} {row['Company Name']} - Score: {row['ICP Score']:.0f} ({row['Confidence']})",
                expanded=False
            ):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**✅ Matching Attributes:**")
                    if row["Matching Attributes"]:
                        attrs = row["Matching Attributes"].split(", ")
                        for i, attr in enumerate(attrs, 1):
                            st.markdown(f"{i}. {escape_markdown(attr)}")
                    else:
                        st.caption("*None specified*")
                
                with col2:
                    st.markdown("**⚠️ Gaps:**")
                    if row["Gaps"]:
                        gaps = row["Gaps"].split(", ")
                        for i, gap in enumerate(gaps, 1):
                            st.markdown(f"{i}. {escape_markdown(gap)}")
                    else:
                        st.caption("*None specified*")
                
                if row["Reasoning"]:
                    st.markdown("**💭 Reasoning:**")
                    st.info(row["Reasoning"])
    else:
        # Standard table view
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True,
            height=400
        )
        st.caption(f"Showing {len(filtered_df)} of {len(df)} results")

