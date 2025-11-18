"""Customer segmentation and clustering analysis."""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Segment:
    """Represents a customer segment."""
    id: str
    name: str
    size: int
    avg_score: float
    characteristics: List[str]
    customer_ids: List[str]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "size": self.size,
            "avg_score": self.avg_score,
            "characteristics": self.characteristics,
            "customer_ids": self.customer_ids
        }


class CustomerSegmenter:
    """Segments customers based on ICP analysis results."""
    
    @staticmethod
    def segment_by_score(
        matches: List,
        thresholds: Optional[Dict[str, float]] = None
    ) -> List[Segment]:
        """
        Segment customers by ICP score ranges.
        
        Args:
            matches: List of ICPMatch objects
            thresholds: Custom score thresholds
            
        Returns:
            List of segments
        """
        if thresholds is None:
            thresholds = {
                "Excellent Fit": 85,
                "Strong Fit": 70,
                "Good Fit": 55,
                "Moderate Fit": 40,
                "Poor Fit": 0
            }
        
        segments = []
        threshold_items = sorted(thresholds.items(), key=lambda x: x[1], reverse=True)
        
        for i, (name, min_score) in enumerate(threshold_items):
            # Determine max score for this segment
            max_score = 100 if i == 0 else threshold_items[i-1][1]
            
            # Filter matches in this range
            segment_matches = [
                m for m in matches 
                if min_score <= m.score < max_score
            ]
            
            if segment_matches:
                # Extract common characteristics
                all_attrs = []
                for m in segment_matches:
                    all_attrs.extend(m.matching_attributes)
                
                # Count frequency
                attr_counts = {}
                for attr in all_attrs:
                    attr_counts[attr] = attr_counts.get(attr, 0) + 1
                
                # Get top 5 most common
                top_attrs = sorted(
                    attr_counts.items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )[:5]
                characteristics = [attr for attr, _ in top_attrs]
                
                segments.append(Segment(
                    id=f"segment_{i+1}",
                    name=name,
                    size=len(segment_matches),
                    avg_score=sum(m.score for m in segment_matches) / len(segment_matches),
                    characteristics=characteristics,
                    customer_ids=[m.customer_id for m in segment_matches]
                ))
        
        return segments
    
    @staticmethod
    def segment_by_confidence(matches: List) -> List[Segment]:
        """
        Segment customers by confidence level.
        
        Args:
            matches: List of ICPMatch objects
            
        Returns:
            List of segments
        """
        segments = []
        
        for conf_level in ["high", "medium", "low"]:
            segment_matches = [m for m in matches if m.confidence == conf_level]
            
            if segment_matches:
                # Extract characteristics
                all_attrs = []
                for m in segment_matches:
                    all_attrs.extend(m.matching_attributes)
                
                attr_counts = {}
                for attr in all_attrs:
                    attr_counts[attr] = attr_counts.get(attr, 0) + 1
                
                top_attrs = sorted(
                    attr_counts.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5]
                characteristics = [attr for attr, _ in top_attrs]
                
                segments.append(Segment(
                    id=f"conf_{conf_level}",
                    name=f"{conf_level.title()} Confidence",
                    size=len(segment_matches),
                    avg_score=sum(m.score for m in segment_matches) / len(segment_matches),
                    characteristics=characteristics,
                    customer_ids=[m.customer_id for m in segment_matches]
                ))
        
        return segments
    
    @staticmethod
    def get_segment_trends(
        segments: List[Segment],
        customer_data: pd.DataFrame
    ) -> Dict[str, any]:
        """
        Analyze trends across segments.
        
        Args:
            segments: List of segments
            customer_data: Original customer DataFrame
            
        Returns:
            Dictionary of trends
        """
        trends = {
            "segment_distribution": [],
            "score_progression": [],
            "size_comparison": []
        }
        
        for segment in segments:
            trends["segment_distribution"].append({
                "name": segment.name,
                "size": segment.size,
                "avg_score": segment.avg_score
            })
            
            trends["score_progression"].append({
                "segment": segment.name,
                "score": segment.avg_score
            })
            
            trends["size_comparison"].append({
                "segment": segment.name,
                "count": segment.size
            })
        
        return trends


class CustomerComparator:
    """Compare customers side-by-side."""
    
    @staticmethod
    def compare_customers(
        customer_ids: List[str],
        matches: List,
        customer_data: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Create comparison table for selected customers.
        
        Args:
            customer_ids: List of customer IDs to compare
            matches: List of ICPMatch objects
            customer_data: Original customer DataFrame
            
        Returns:
            Comparison DataFrame
        """
        # Find matches for selected customers
        selected_matches = [m for m in matches if m.customer_id in customer_ids]
        
        if not selected_matches:
            return pd.DataFrame()
        
        # Build comparison data
        comparison_data = []
        for match in selected_matches:
            # Get original customer data
            customer_row = customer_data[
                customer_data.iloc[:, 0].astype(str) == str(match.customer_id)
            ]
            
            row = {
                "Customer ID": match.customer_id,
                "Company": match.company_name,
                "ICP Score": match.score,
                "Confidence": match.confidence,
                "Matching Attributes": ", ".join(match.matching_attributes[:3]),
                "Gaps": ", ".join(match.gaps[:3]),
                "Score Rank": None  # Will fill after sorting
            }
            comparison_data.append(row)
        
        # Create DataFrame and add rank
        df = pd.DataFrame(comparison_data)
        df = df.sort_values("ICP Score", ascending=False)
        df["Score Rank"] = range(1, len(df) + 1)
        
        return df
    
    @staticmethod
    def get_attribute_comparison(matches: List) -> pd.DataFrame:
        """
        Compare attributes across all customers.
        
        Args:
            matches: List of ICPMatch objects
            
        Returns:
            DataFrame with attribute comparison
        """
        # Collect all unique attributes
        all_attributes = set()
        for match in matches:
            all_attributes.update(match.matching_attributes)
        
        # Build matrix
        data = []
        for match in matches:
            row = {
                "Customer": match.company_name,
                "Score": match.score
            }
            for attr in sorted(all_attributes):
                row[attr] = "✓" if attr in match.matching_attributes else ""
            data.append(row)
        
        return pd.DataFrame(data)


class ProfileGenerator:
    """Generate detailed customer profiles."""
    
    @staticmethod
    def generate_profile(
        customer_id: str,
        match,
        customer_data: pd.DataFrame,
        all_matches: List
    ) -> Dict[str, any]:
        """
        Generate detailed profile for a customer.
        
        Args:
            customer_id: Customer ID
            match: ICPMatch object for this customer
            customer_data: Original customer DataFrame
            all_matches: All matches for context
            
        Returns:
            Profile dictionary
        """
        # Get original data
        customer_row = customer_data[
            customer_data.iloc[:, 0].astype(str) == str(customer_id)
        ]
        
        # Calculate percentile
        all_scores = [m.score for m in all_matches]
        percentile = sum(1 for s in all_scores if s < match.score) / len(all_scores) * 100
        
        # Find similar customers
        similar = [
            m for m in all_matches
            if abs(m.score - match.score) <= 10 and m.customer_id != customer_id
        ][:5]
        
        profile = {
            "basic_info": {
                "customer_id": customer_id,
                "company_name": match.company_name,
                "icp_score": match.score,
                "confidence": match.confidence,
                "percentile": percentile
            },
            "strengths": {
                "matching_attributes": match.matching_attributes,
                "count": len(match.matching_attributes)
            },
            "weaknesses": {
                "gaps": match.gaps,
                "count": len(match.gaps)
            },
            "analysis": {
                "reasoning": match.reasoning,
                "recommendation": ProfileGenerator._generate_recommendation(match)
            },
            "context": {
                "rank": None,  # Set by caller
                "total_analyzed": len(all_matches),
                "similar_customers": [
                    {
                        "name": m.company_name,
                        "score": m.score
                    }
                    for m in similar
                ]
            },
            "raw_data": customer_row.to_dict(orient="records")[0] if not customer_row.empty else {}
        }
        
        return profile
    
    @staticmethod
    def _generate_recommendation(match) -> str:
        """Generate recommendation based on match data."""
        if match.score >= 80:
            return "High-priority prospect. Engage immediately with tailored outreach."
        elif match.score >= 60:
            return "Strong candidate. Qualify further and address gaps before full engagement."
        elif match.score >= 40:
            return "Moderate fit. Consider nurture campaign to build alignment."
        else:
            return "Low fit. Deprioritize or use for market research only."

