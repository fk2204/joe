# Utils module

from src.utils.best_practices import (
    HOOK_FORMULAS,
    IMPACT_FORMULA,
    NICHE_METRICS,
    POWER_WORDS,
    RETENTION_BEST_PRACTICES,
    SEO_PATTERNS,
    VIRAL_TITLE_PATTERNS,
    ChecklistItem,
    PrePublishChecklist,
    ValidationResult,
    get_best_practices,
    get_hook_for_niche,
    get_niche_metrics,
    get_viral_title_templates,
    pre_publish_checklist,
    suggest_improvements,
    validate_hook,
    validate_title,
)
from src.utils.db_optimizer import (
    ConnectionPool,
    DatabaseOptimizer,
    IndexRecommendation,
    QueryCache,
    QueryStats,
    TableInfo,
    optimize_all_databases,
    print_optimization_summary,
)
from src.utils.profiler import (
    AggregatedStats,
    Profiler,
    ProfileResult,
    TimingContext,
    clear,
    get_report,
    profile,
    profile_func,
    timed,
)
from src.utils.segment_cache import (
    SegmentCache,
    SegmentCacheStats,
    SegmentEntry,
    print_segment_cache_stats,
)

__all__ = [
    # Validation functions
    "validate_title",
    "validate_hook",
    "get_best_practices",
    "suggest_improvements",
    "pre_publish_checklist",
    "get_niche_metrics",
    "get_hook_for_niche",
    "get_viral_title_templates",
    # Data classes
    "ValidationResult",
    "PrePublishChecklist",
    "ChecklistItem",
    # Constants
    "NICHE_METRICS",
    "VIRAL_TITLE_PATTERNS",
    "HOOK_FORMULAS",
    "POWER_WORDS",
    "SEO_PATTERNS",
    "RETENTION_BEST_PRACTICES",
    "IMPACT_FORMULA",
    # Segment cache
    "SegmentCache",
    "SegmentEntry",
    "SegmentCacheStats",
    "print_segment_cache_stats",
    # Database optimization
    "DatabaseOptimizer",
    "ConnectionPool",
    "QueryCache",
    "QueryStats",
    "TableInfo",
    "IndexRecommendation",
    "optimize_all_databases",
    "print_optimization_summary",
    # Profiler
    "Profiler",
    "ProfileResult",
    "AggregatedStats",
    "TimingContext",
    "timed",
    "profile",
    "profile_func",
    "get_report",
    "clear",
]
