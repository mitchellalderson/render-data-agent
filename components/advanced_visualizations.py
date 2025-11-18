"""Advanced visualization components for Phase 4."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Optional

from src.segmentation import Segment
from src.utils import escape_markdown


def render_segment_overview(segments: List[Segment]) -> None:
    """
    Render segment overview with multiple visualizations.
    
    Args:
        segments: List of customer segments
    """
    st.markdown("### 📊 Customer Segmentation")
    
    if not segments:
        st.info("No segments to display")
        return
    
    # Segment distribution
    col1, col2 = st.columns(2)
    
    with col1:
        # Size distribution pie chart
        fig = go.Figure(data=[
            go.Pie(
                labels=[s.name for s in segments],
                values=[s.size for s in segments],
                hole=0.4,
                marker=dict(
                    colors=px.colors.sequential.RdBu[:len(segments)]
                ),
                hovertemplate='%{label}<br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title="Customer Distribution by Segment",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Average score by segment bar chart
        fig = go.Figure(data=[
            go.Bar(
                x=[s.name for s in segments],
                y=[s.avg_score for s in segments],
                marker_color=[s.avg_score for s in segments],
                marker_colorscale='RdYlGn',
                text=[f"{s.avg_score:.1f}" for s in segments],
                textposition='outside',
                hovertemplate='%{x}<br>Avg Score: %{y:.1f}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title="Average ICP Score by Segment",
            xaxis_title="Segment",
            yaxis_title="Average Score",
            yaxis_range=[0, 100],
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)


def render_segment_details(segments: List[Segment]) -> None:
    """
    Render detailed segment cards.
    
    Args:
        segments: List of customer segments
    """
    st.markdown("### 🎯 Segment Details")
    
    for segment in segments:
        with st.expander(f"**{segment.name}** ({segment.size} customers)", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Customers", segment.size)
            
            with col2:
                st.metric("Avg Score", f"{segment.avg_score:.1f}")
            
            with col3:
                # Calculate percentage of total
                total = sum(s.size for s in segments)
                pct = (segment.size / total * 100) if total > 0 else 0
                st.metric("% of Total", f"{pct:.1f}%")
            
            st.markdown("**Common Characteristics:**")
            for char in segment.characteristics:
                st.markdown(f"- {escape_markdown(char)}")


def render_customer_comparison(comparison_df: pd.DataFrame) -> None:
    """
    Render customer comparison table and charts.
    
    Args:
        comparison_df: DataFrame with customer comparison data
    """
    st.markdown("### 🔀 Customer Comparison")
    
    if comparison_df.empty:
        st.info("No customers selected for comparison")
        return
    
    # Score comparison chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=comparison_df["Company"],
        y=comparison_df["ICP Score"],
        text=comparison_df["ICP Score"].round(1),
        textposition='outside',
        marker=dict(
            color=comparison_df["ICP Score"],
            colorscale='RdYlGn',
            showscale=True,
            colorbar=dict(title="ICP Score")
        ),
        hovertemplate='%{x}<br>Score: %{y:.1f}<extra></extra>'
    ))
    
    fig.update_layout(
        title="ICP Score Comparison",
        xaxis_title="Customer",
        yaxis_title="ICP Score",
        yaxis_range=[0, 100],
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Comparison table
    st.markdown("#### Detailed Comparison")
    st.dataframe(
        comparison_df,
        use_container_width=True,
        hide_index=True
    )


def render_customer_profile(profile: Dict, rank: int = None) -> None:
    """
    Render detailed customer profile view.
    
    Args:
        profile: Customer profile dictionary
        rank: Customer's rank
    """
    st.markdown("### 👤 Customer Profile")
    
    basic = profile["basic_info"]
    strengths = profile["strengths"]
    weaknesses = profile["weaknesses"]
    analysis = profile["analysis"]
    context = profile["context"]
    
    # Header with key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("ICP Score", f"{basic['icp_score']:.1f}")
    
    with col2:
        st.metric("Percentile", f"{basic['percentile']:.0f}th")
    
    with col3:
        st.metric("Confidence", basic['confidence'].title())
    
    with col4:
        if rank:
            st.metric("Rank", f"#{rank}")
    
    st.markdown("---")
    
    # Strengths and Weaknesses
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"#### ✅ Strengths ({strengths['count']})")
        if strengths['matching_attributes']:
            st.caption(f"*This customer has {strengths['count']} attributes that align with your ICP*")
            for idx, attr in enumerate(strengths['matching_attributes'], 1):
                # Enhanced display with numbering and detail
                if ":" in attr:
                    # Attribute has detail (e.g., "Industry: Technology")
                    st.success(f"**{idx}.** {attr}")
                else:
                    # Simple attribute name
                    st.success(f"**{idx}.** ✓ {attr}")
        else:
            st.info("No specific strengths identified - review reasoning below")
    
    with col2:
        st.markdown(f"#### ⚠️ Gaps ({weaknesses['count']})")
        if weaknesses['gaps']:
            st.caption(f"*{weaknesses['count']} areas where this customer differs from your ICP*")
            for idx, gap in enumerate(weaknesses['gaps'], 1):
                # Enhanced display with numbering and detail
                if ":" in gap:
                    # Gap has detail (e.g., "Missing: Team size data")
                    st.warning(f"**{idx}.** {gap}")
                else:
                    # Simple gap name
                    st.warning(f"**{idx}.** ⚠ Missing or weak: {gap}")
        else:
            st.info("No significant gaps identified - strong ICP match")
    
    st.markdown("---")
    
    # Analysis
    st.markdown("#### 📊 Analysis")
    st.info(analysis['reasoning'])
    
    st.markdown("#### 💡 Recommendation")
    st.success(analysis['recommendation'])
    
    # Similar customers
    if context['similar_customers']:
        st.markdown("---")
        st.markdown("#### 🔗 Similar Customers")
        
        for similar in context['similar_customers']:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"- {similar['name']}")
            with col2:
                st.markdown(f"Score: {similar['score']:.1f}")


def render_trend_analysis(segments: List[Segment]) -> None:
    """
    Render trend analysis across segments.
    
    Args:
        segments: List of customer segments
    """
    st.markdown("### 📈 Trend Analysis")
    
    if not segments:
        st.info("No trend data available")
        return
    
    # Create funnel chart
    fig = go.Figure(go.Funnel(
        y=[s.name for s in segments],
        x=[s.size for s in segments],
        textposition="inside",
        textinfo="value+percent initial",
        marker=dict(
            color=[s.avg_score for s in segments],
            colorscale='RdYlGn'
        ),
        hovertemplate='%{y}<br>Count: %{x}<br>Avg Score: %{marker.color:.1f}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Customer Funnel by Segment Quality",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_attribute_heatmap(attribute_df: pd.DataFrame) -> None:
    """
    Render heatmap of attributes across customers.
    
    Args:
        attribute_df: DataFrame with attribute comparison
    """
    st.markdown("### 🔥 Attribute Heatmap")
    
    if attribute_df.empty:
        st.info("No attribute data available")
        return
    
    # Convert to numeric (1 for ✓, 0 for empty)
    df_numeric = attribute_df.copy()
    for col in df_numeric.columns:
        if col not in ["Customer", "Score"]:
            df_numeric[col] = df_numeric[col].apply(lambda x: 1 if x == "✓" else 0)
    
    # Get attribute columns
    attr_cols = [c for c in df_numeric.columns if c not in ["Customer", "Score"]]
    
    if not attr_cols:
        st.info("No attributes to display")
        return
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=df_numeric[attr_cols].values,
        x=attr_cols,
        y=df_numeric["Customer"],
        colorscale='RdYlGn',
        hovertemplate='Customer: %{y}<br>Attribute: %{x}<br>Present: %{z}<extra></extra>',
        showscale=False
    ))
    
    fig.update_layout(
        title="Attribute Presence by Customer",
        xaxis_title="Attributes",
        yaxis_title="Customers",
        height=max(400, len(df_numeric) * 30)
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_score_radar(customers: List[Dict]) -> None:
    """
    Render radar chart comparing multiple customers.
    
    Args:
        customers: List of customer dictionaries with scores
    """
    st.markdown("### 📡 Multi-Dimensional Comparison")
    
    if not customers or len(customers) < 2:
        st.info("Select at least 2 customers for radar comparison")
        return
    
    # Create radar chart
    fig = go.Figure()
    
    categories = ['ICP Score', 'Data Quality', 'Attribute Match', 'Confidence']
    
    for customer in customers[:5]:  # Limit to 5 for readability
        fig.add_trace(go.Scatterpolar(
            r=[
                customer.get('score', 0),
                customer.get('quality', 50),
                customer.get('match_rate', 50),
                {'high': 90, 'medium': 60, 'low': 30}.get(customer.get('confidence', 'medium'), 50)
            ],
            theta=categories,
            fill='toself',
            name=customer.get('name', 'Unknown')
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=True,
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_insights_summary(segments: List[Segment], total_customers: int) -> None:
    """
    Render key insights and takeaways.
    
    Args:
        segments: List of customer segments
        total_customers: Total number of customers analyzed
    """
    st.markdown("### 💎 Key Insights")
    
    if not segments:
        return
    
    # Calculate insights
    top_segment = max(segments, key=lambda s: s.size)
    best_segment = max(segments, key=lambda s: s.avg_score)
    
    high_quality = sum(s.size for s in segments if s.avg_score >= 70)
    high_quality_pct = (high_quality / total_customers * 100) if total_customers > 0 else 0
    
    # Display insights
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"""
        **Largest Segment:** {top_segment.name}
        - Contains {top_segment.size} customers ({top_segment.size/total_customers*100:.1f}%)
        - Average score: {top_segment.avg_score:.1f}
        """)
        
        st.success(f"""
        **High-Quality Prospects:** {high_quality} customers
        - {high_quality_pct:.1f}% of total have score ≥70
        - Focus outreach on these customers first
        """)
    
    with col2:
        st.info(f"""
        **Highest Quality Segment:** {best_segment.name}
        - Average score: {best_segment.avg_score:.1f}
        - Contains {best_segment.size} customers
        """)
        
        # Recommendations
        if high_quality_pct >= 30:
            message = "✅ Strong pipeline! Focus on converting top segments."
        elif high_quality_pct >= 15:
            message = "⚠️ Moderate pipeline. Nurture middle segments."
        else:
            message = "❌ Weak pipeline. Review ICP definition or expand targeting."
        
        st.warning(f"**Pipeline Health:** {message}")

