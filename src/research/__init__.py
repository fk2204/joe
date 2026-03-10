# Research modules
from .idea_generator import IdeaGenerator
from .reddit import RedditResearcher
from .trends import TrendResearcher

# Enhanced Reddit researcher (optional - requires praw)
try:
    from .reddit_researcher import RedditPost
    from .reddit_researcher import RedditResearcher as EnhancedRedditResearcher
    from .reddit_researcher import RedditResearchReport, SubredditStats
    from .reddit_researcher import VideoIdea as RedditVideoIdea

    ENHANCED_REDDIT_AVAILABLE = True
except ImportError:
    ENHANCED_REDDIT_AVAILABLE = False
    EnhancedRedditResearcher = None
    RedditPost = None
    RedditVideoIdea = None
    RedditResearchReport = None
    SubredditStats = None

__all__ = [
    "TrendResearcher",
    "RedditResearcher",
    "IdeaGenerator",
    # Enhanced Reddit (optional)
    "EnhancedRedditResearcher",
    "RedditPost",
    "RedditVideoIdea",
    "RedditResearchReport",
    "SubredditStats",
    "ENHANCED_REDDIT_AVAILABLE",
]
