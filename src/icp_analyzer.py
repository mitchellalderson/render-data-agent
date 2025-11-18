"""ICP (Ideal Customer Profile) analysis using LLM."""

import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
import json
from dataclasses import dataclass, asdict

from src.llm_client import LLMClient, get_default_client


@dataclass
class ICPMatch:
    """Represents a customer matched to the ICP."""
    customer_id: str
    company_name: str
    score: float  # 0-100
    confidence: str  # high, medium, low
    matching_attributes: List[str]
    gaps: List[str]
    reasoning: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class ICPAnalysisResult:
    """Complete ICP analysis results."""
    matches: List[ICPMatch]
    patterns: Dict[str, Any]
    recommendations: List[str]
    data_quality_notes: List[str]
    summary: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "matches": [m.to_dict() for m in self.matches],
            "patterns": self.patterns,
            "recommendations": self.recommendations,
            "data_quality_notes": self.data_quality_notes,
            "summary": self.summary
        }


class ICPAnalyzer:
    """Analyzes customer data against ICP using LLM."""
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        """
        Initialize ICP analyzer.
        
        Args:
            llm_client: LLM client to use (if None, uses default)
        """
        self.llm_client = llm_client or get_default_client()
    
    def analyze(
        self,
        signup_data: pd.DataFrame,
        customer_data: pd.DataFrame,
        icp_criteria: Optional[Dict[str, Any]] = None,
        max_customers: int = 50
    ) -> ICPAnalysisResult:
        """
        Analyze customers against ICP.
        
        Args:
            signup_data: DataFrame of user signups (represents ICP)
            customer_data: DataFrame of customers to analyze
            icp_criteria: Optional explicit ICP criteria
            max_customers: Maximum customers to analyze (for performance)
            
        Returns:
            ICPAnalysisResult with matches and insights
        """
        # Limit data size for LLM context
        signup_sample = signup_data.head(max_customers)
        customer_sample = customer_data.head(max_customers)
        
        # Build prompt
        prompt = self._build_analysis_prompt(
            signup_sample,
            customer_sample,
            icp_criteria
        )
        
        system_prompt = self._build_system_prompt()
        
        # Get LLM response
        response_json = self.llm_client.generate_json(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.5
        )
        
        # Parse response into structured result
        return self._parse_analysis_response(response_json, customer_sample)
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for ICP analysis."""
        return """You are an expert B2B sales and customer profiling analyst. Your job is to:

1. Analyze customer data and identify which customers match an Ideal Customer Profile (ICP)
2. Score each customer on ICP fit (0-100 scale)
3. Identify patterns in high-scoring customers
4. Provide actionable recommendations

Guidelines:
- Be objective and data-driven
- Consider multiple dimensions: company size, industry, use case, behavior
- Assign confidence levels (high/medium/low) based on data completeness
- Identify both matches and gaps for each customer
- Highlight patterns that define the best customers
- Provide specific, actionable recommendations

IMPORTANT - For matching_attributes and gaps:
- Be specific and descriptive, not just attribute names
- Include the actual value or context when possible
- Use format "Attribute Name: Specific Detail" (e.g., "Industry: SaaS/Technology" instead of just "Industry")
- For gaps, explain what's missing or weak (e.g., "Missing: Company size data" or "Team size: Too small (5 employees vs ICP of 50+)")
- This helps users understand exactly what matched and what needs improvement

Output Format:
Return a valid JSON object with this structure:
{
  "matches": [
    {
      "customer_id": "unique identifier",
      "company_name": "company name",
      "score": 85,
      "confidence": "high",
      "matching_attributes": [
        "Industry: SaaS/Technology (matches ICP)",
        "Company size: 100-200 employees (ideal range)",
        "Revenue: $5-10M ARR (strong fit)"
      ],
      "gaps": [
        "Missing: Product usage data",
        "Team structure: No engineering team identified",
        "Growth rate: Below 20% (ICP target is 50%+)"
      ],
      "reasoning": "Why this score was assigned"
    }
  ],
  "patterns": {
    "common_industries": ["industry1", "industry2"],
    "common_sizes": ["50-200", "200-1000"],
    "common_attributes": ["attribute1", "attribute2"],
    "key_indicators": ["indicator1", "indicator2"]
  },
  "recommendations": [
    "Specific actionable recommendation 1",
    "Specific actionable recommendation 2"
  ],
  "data_quality_notes": [
    "Note about data quality or limitations"
  ],
  "summary": "2-3 sentence executive summary of findings"
}"""
    
    def _build_analysis_prompt(
        self,
        signup_data: pd.DataFrame,
        customer_data: pd.DataFrame,
        icp_criteria: Optional[Dict[str, Any]]
    ) -> str:
        """Build the analysis prompt with data."""
        prompt_parts = []
        
        # Header
        prompt_parts.append("# ICP Analysis Request\n")
        
        # ICP criteria (from signup data or explicit)
        prompt_parts.append("## Ideal Customer Profile (ICP)")
        if icp_criteria:
            prompt_parts.append(f"Explicit criteria provided:\n```json\n{json.dumps(icp_criteria, indent=2)}\n```\n")
        else:
            prompt_parts.append("Derive ICP from the signup data below (these represent our target customers).\n")
        
        # Signup data (represents ICP)
        prompt_parts.append("## Signup Data (Represents ICP)")
        prompt_parts.append(f"Total signups: {len(signup_data)}")
        prompt_parts.append(f"Columns: {', '.join(signup_data.columns)}\n")
        
        # Convert to JSON-like format for LLM
        signup_json = signup_data.to_dict(orient='records')
        # Limit to first 20 for context size
        prompt_parts.append(f"Sample records (showing {min(20, len(signup_json))} of {len(signup_json)}):")
        prompt_parts.append(f"```json\n{json.dumps(signup_json[:20], indent=2, default=str)}\n```\n")
        
        # Customer data (to analyze)
        prompt_parts.append("## Customer Data (To Analyze)")
        prompt_parts.append(f"Total customers: {len(customer_data)}")
        prompt_parts.append(f"Columns: {', '.join(customer_data.columns)}\n")
        
        customer_json = customer_data.to_dict(orient='records')
        prompt_parts.append(f"Customer records (showing {min(20, len(customer_json))} of {len(customer_json)}):")
        prompt_parts.append(f"```json\n{json.dumps(customer_json[:20], indent=2, default=str)}\n```\n")
        
        # Instructions
        prompt_parts.append("## Task")
        prompt_parts.append("""Analyze each customer in the customer data and:
1. Score them on ICP fit (0-100)
2. Identify matching attributes and gaps
3. Assign confidence level
4. Provide reasoning for the score

Then identify patterns and provide recommendations.

Return the response as valid JSON matching the specified structure.""")
        
        return "\n".join(prompt_parts)
    
    def _parse_analysis_response(
        self,
        response: Dict[str, Any],
        customer_data: pd.DataFrame
    ) -> ICPAnalysisResult:
        """Parse LLM JSON response into ICPAnalysisResult."""
        # Parse matches
        matches = []
        for match_data in response.get("matches", []):
            try:
                matches.append(ICPMatch(
                    customer_id=str(match_data.get("customer_id", "")),
                    company_name=str(match_data.get("company_name", "")),
                    score=float(match_data.get("score", 0)),
                    confidence=str(match_data.get("confidence", "medium")),
                    matching_attributes=match_data.get("matching_attributes", []),
                    gaps=match_data.get("gaps", []),
                    reasoning=str(match_data.get("reasoning", ""))
                ))
            except (ValueError, TypeError) as e:
                # Skip invalid matches
                continue
        
        # Sort matches by score
        matches.sort(key=lambda x: x.score, reverse=True)
        
        return ICPAnalysisResult(
            matches=matches,
            patterns=response.get("patterns", {}),
            recommendations=response.get("recommendations", []),
            data_quality_notes=response.get("data_quality_notes", []),
            summary=response.get("summary", "")
        )
    
    def get_top_matches(
        self,
        result: ICPAnalysisResult,
        top_n: int = 10,
        min_score: float = 60.0
    ) -> List[ICPMatch]:
        """
        Get top N matches above minimum score.
        
        Args:
            result: Analysis result
            top_n: Number of top matches to return
            min_score: Minimum score threshold
            
        Returns:
            List of top matches
        """
        filtered = [m for m in result.matches if m.score >= min_score]
        return filtered[:top_n]
    
    def get_match_statistics(self, result: ICPAnalysisResult) -> Dict[str, Any]:
        """
        Calculate statistics from analysis results.
        
        Args:
            result: Analysis result
            
        Returns:
            Dictionary of statistics
        """
        if not result.matches:
            return {
                "total_analyzed": 0,
                "avg_score": 0,
                "high_confidence_count": 0,
                "matches_above_80": 0,
                "matches_above_60": 0
            }
        
        scores = [m.score for m in result.matches]
        
        return {
            "total_analyzed": len(result.matches),
            "avg_score": sum(scores) / len(scores),
            "median_score": sorted(scores)[len(scores) // 2],
            "high_confidence_count": sum(1 for m in result.matches if m.confidence == "high"),
            "medium_confidence_count": sum(1 for m in result.matches if m.confidence == "medium"),
            "low_confidence_count": sum(1 for m in result.matches if m.confidence == "low"),
            "matches_above_80": sum(1 for s in scores if s >= 80),
            "matches_above_60": sum(1 for s in scores if s >= 60),
            "matches_below_40": sum(1 for s in scores if s < 40),
        }
    
    def export_results_to_dataframe(self, result: ICPAnalysisResult) -> pd.DataFrame:
        """
        Export analysis results to DataFrame.
        
        Args:
            result: Analysis result
            
        Returns:
            DataFrame with all matches
        """
        if not result.matches:
            return pd.DataFrame()
        
        data = []
        for match in result.matches:
            data.append({
                "Customer ID": match.customer_id,
                "Company Name": match.company_name,
                "ICP Score": match.score,
                "Confidence": match.confidence,
                "Matching Attributes": ", ".join(match.matching_attributes),
                "Gaps": ", ".join(match.gaps),
                "Reasoning": match.reasoning
            })
        
        return pd.DataFrame(data)


def quick_analyze(
    signup_data: pd.DataFrame,
    customer_data: pd.DataFrame,
    icp_criteria: Optional[Dict[str, Any]] = None
) -> ICPAnalysisResult:
    """
    Quick analysis function for convenience.
    
    Args:
        signup_data: Signup data representing ICP
        customer_data: Customer data to analyze
        icp_criteria: Optional explicit ICP criteria
        
    Returns:
        Analysis results
    """
    analyzer = ICPAnalyzer()
    return analyzer.analyze(signup_data, customer_data, icp_criteria)

