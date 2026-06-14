import logging
from typing import List, Dict, Any, Tuple
from collections import Counter
import os

try:
    from sklearn.feature_extraction.text import CountVectorizer
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

from backend.models import Issue
from backend.spatial_utils import cluster_issues_dbscan, calculate_cluster_centroid

logger = logging.getLogger(__name__)

class TrendAnalyzer:
    """
    Analyzes civic issues to detect trends, keywords, and geographic clusters.
    """

    def analyze(self, issues: List[Issue]) -> Dict[str, Any]:
        """
        Perform comprehensive analysis on a list of issues.
        """
        if not issues:
            return {
                "total_issues": 0,
                "top_keywords": [],
                "category_distribution": {},
                "geographic_clusters": []
            }

        return {
            "total_issues": len(issues),
            "top_keywords": self._extract_keywords(issues),
            "category_distribution": self._analyze_categories(issues),
            "geographic_clusters": self._analyze_clusters(issues)
        }

    def _extract_keywords(self, issues: List[Issue], top_n: int = 5) -> List[Tuple[str, int]]:
        """Extracts top keywords from issue descriptions."""
        descriptions = [issue.description for issue in issues if issue.description]

        if not descriptions:
            return []

        if HAS_SKLEARN:
            try:
                # Use Scikit-Learn for efficient keyword extraction
                vectorizer = CountVectorizer(stop_words='english', max_features=top_n)
                X = vectorizer.fit_transform(descriptions)
                # Handle matrix output safely across numpy versions
                import numpy as np
                counts = np.asarray(X.sum(axis=0)).flatten()
                vocab = vectorizer.get_feature_names_out()

                # Zip and sort
                keywords = list(zip(vocab, counts))
                keywords.sort(key=lambda x: x[1], reverse=True)
                return keywords
            except Exception as e:
                logger.warning(f"Error using CountVectorizer: {e}. Falling back to simple counter.")

        # Fallback: Simple word counter
        all_words = []
        stopwords = set(['the', 'and', 'is', 'in', 'it', 'to', 'of', 'for', 'on', 'at', 'a', 'an', 'this', 'that', 'with'])

        for desc in descriptions:
            words = desc.lower().split()
            filtered = [w for w in words if w.isalpha() and w not in stopwords and len(w) > 3]
            all_words.extend(filtered)

        return Counter(all_words).most_common(top_n)

    def _analyze_categories(self, issues: List[Issue]) -> Dict[str, int]:
        """Calculates distribution of issues by category."""
        categories = [issue.category for issue in issues if issue.category]
        return dict(Counter(categories).most_common())

    def _analyze_clusters(self, issues: List[Issue]) -> List[Dict[str, Any]]:
        """Identifies geographic clusters of issues."""
        # Only consider issues with valid coordinates
        valid_issues = [i for i in issues if i.latitude is not None and i.longitude is not None]

        if not valid_issues:
            return []

        # Use DBSCAN from spatial_utils
        clusters = cluster_issues_dbscan(valid_issues, eps_meters=100.0) # 100m radius for trends

        cluster_info = []
        for cluster in clusters:
            if not cluster:
                continue

            centroid_lat, centroid_lon = calculate_cluster_centroid(cluster)

            # Find dominant category in cluster
            categories = [i.category for i in cluster if i.category]
            dominant_category = Counter(categories).most_common(1)[0][0] if categories else "Unknown"

            cluster_info.append({
                "centroid": {"lat": centroid_lat, "lon": centroid_lon},
                "size": len(cluster),
                "dominant_category": dominant_category,
                "issues": [i.id for i in cluster]
            })

        # Sort by size desc
        cluster_info.sort(key=lambda x: x["size"], reverse=True)
        return cluster_info

trend_analyzer = TrendAnalyzer()
