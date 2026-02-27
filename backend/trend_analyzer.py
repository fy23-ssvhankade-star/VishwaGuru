import logging
from typing import List, Dict, Any, Tuple
from collections import Counter
import re

from backend.models import Issue
from backend.spatial_utils import cluster_issues_dbscan, get_cluster_representative

logger = logging.getLogger(__name__)

class TrendAnalyzer:
    def __init__(self):
        self.stop_words = {
            "the", "a", "an", "in", "on", "at", "to", "for", "of", "and", "is", "are",
            "was", "were", "this", "that", "it", "with", "from", "by", "as", "be",
            "or", "not", "but", "if", "so", "my", "your", "its", "their", "there",
            "here", "when", "where", "why", "how", "all", "any", "some", "no",
            "issue", "problem", "complaint", "regarding", "please", "help", "fix",
            "near", "opposite", "behind", "front", "road", "street", "lane"
        }

    def analyze(self, issues: List[Issue]) -> Dict[str, Any]:
        """
        Analyze a list of issues to extract trends, keywords, and clusters.
        """
        if not issues:
            return {
                "top_keywords": [],
                "category_distribution": {},
                "clusters": [],
                "total_issues": 0
            }

        keywords = self._extract_keywords(issues)
        categories = self._analyze_categories(issues)
        clusters = self._analyze_clusters(issues)

        return {
            "top_keywords": keywords,
            "category_distribution": categories,
            "clusters": clusters,
            "total_issues": len(issues)
        }

    def _extract_keywords(self, issues: List[Issue]) -> List[Tuple[str, int]]:
        """
        Extract top 5 most common keywords from issue descriptions.
        """
        text = " ".join([issue.description.lower() for issue in issues if issue.description])
        # Simple tokenization: remove punctuation and split by whitespace
        words = re.findall(r'\b\w+\b', text)
        filtered_words = [w for w in words if w not in self.stop_words and len(w) > 2 and not w.isdigit()]

        counter = Counter(filtered_words)
        return counter.most_common(5)

    def _analyze_categories(self, issues: List[Issue]) -> Dict[str, int]:
        """
        Count occurrences of each category.
        """
        categories = [issue.category for issue in issues if issue.category]
        return dict(Counter(categories))

    def _analyze_clusters(self, issues: List[Issue]) -> List[Dict[str, Any]]:
        """
        Identify geographic clusters of issues using DBSCAN.
        Only returns clusters with at least 3 issues.
        """
        # Use DBSCAN from spatial_utils with 100m radius
        issue_clusters = cluster_issues_dbscan(issues, eps_meters=100.0)

        results = []
        for cluster in issue_clusters:
            if len(cluster) < 3:
                continue

            try:
                representative = get_cluster_representative(cluster)
                results.append({
                    "count": len(cluster),
                    "latitude": representative.latitude,
                    "longitude": representative.longitude,
                    "representative_category": representative.category,
                    "representative_desc": representative.description[:50] + "..." if representative.description else ""
                })
            except Exception as e:
                logger.error(f"Error processing cluster: {e}")

        # Sort by cluster size descending
        results.sort(key=lambda x: x['count'], reverse=True)
        return results

    def extract_category_keywords(self, issues: List[Issue]) -> Dict[str, List[Tuple[str, int]]]:
        """
        Analyze issues grouped by category to find common keywords within that category.
        Returns a dict: { category_name: [(keyword, count), ...] }
        """
        issues_by_cat = {}
        for issue in issues:
            if not issue.category or not issue.description:
                continue

            if issue.category not in issues_by_cat:
                issues_by_cat[issue.category] = []
            issues_by_cat[issue.category].append(issue)

        result = {}
        for category, cat_issues in issues_by_cat.items():
            # Skip categories with too few issues to form a pattern
            if len(cat_issues) < 5:
                continue

            keywords = self._extract_keywords(cat_issues)
            # Filter keywords that are just the category name itself
            clean_keywords = []
            for kw, count in keywords:
                if kw not in category.lower() and count >= 3: # Must appear at least 3 times
                    clean_keywords.append((kw, count))

            if clean_keywords:
                result[category] = clean_keywords

        return result

trend_analyzer = TrendAnalyzer()
