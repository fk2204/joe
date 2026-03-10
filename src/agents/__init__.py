# Joe Agents
#
# This module exports all agent classes for easy importing:
#
#   from src.agents import ResearchAgent, QualityAgent, AnalyticsAgent
#   from src.agents import ThumbnailAgent, RetentionOptimizerAgent, ValidatorAgent
#   from src.agents import WorkflowAgent, MonitorAgent, RecoveryAgent, SchedulerAgent
#
# Or import all:
#
#   from src.agents import *
#

from .accessibility_agent import AccessibilityAgent, AccessibilityResult
from .analytics_agent import AnalyticsAgent, AnalyticsResult, PerformanceMetrics
from .audio_quality_agent import AudioQualityAgent, AudioQualityResult

# Base Agent Infrastructure
from .base_agent import AgentError, AgentMessage, AgentResult, BaseAgent

# Quality Cluster Agents (NEW - 2026-01-19)
from .compliance_agent import ComplianceAgent, ComplianceResult
from .content_safety_agent import ContentSafetyAgent, RiskLevel, SafetyResult

# CrewAI Integration
from .crew import YouTubeCrew
from .monitor_agent import (
    APIStatus,
    HealthAlert,
    HealthResult,
    HealthStatus,
    MonitorAgent,
    ResourceUsage,
)
from .quality_agent import QualityAgent, QualityCheckItem, QualityResult
from .recovery_agent import (
    ErrorCategory,
    FailureRecord,
    RecoveryAgent,
    RecoveryResult,
    RecoveryStrategy,
)

# Core Agents
from .research_agent import ResearchAgent, ResearchResult
from .retention_optimizer_agent import RetentionOptimizerAgent, RetentionResult
from .scheduler_agent import JobStatus, JobType, ScheduledJob, SchedulerAgent, ScheduleResult

# SEO Agents
from .seo_agent import SEOAgent, SEOResult
from .seo_strategist import (
    ABTestManager,
    CompetitorAnalyzer,
    CompetitorReport,
    CompetitorVideo,
    ContentCalendar,
    CTRPrediction,
    KeywordData,
    KeywordResearcher,
    PerformancePredictor,
    RetentionPrediction,
    SearchIntent,
    SearchIntentAnalyzer,
    SEOStrategist,
    SEOStrategyResult,
    TitleVariant,
    TopicSuggestion,
)

# Production Agents (NEW - 2026-01-19)
from .thumbnail_agent import ThumbnailAgent, ThumbnailResult
from .validator_agent import ValidationCheck, ValidationResult, ValidatorAgent
from .video_quality_agent import VideoQualityAgent, VideoQualityResult

# Automation Cluster Agents (NEW - 2026-01-19)
from .workflow_agent import (
    WorkflowAgent,
    WorkflowResult,
    WorkflowState,
    WorkflowStatus,
    WorkflowStep,
)

__all__ = [
    # Base Infrastructure
    "BaseAgent",
    "AgentResult",
    "AgentMessage",
    "AgentError",
    # Core Agents
    "ResearchAgent",
    "ResearchResult",
    "QualityAgent",
    "QualityResult",
    "QualityCheckItem",
    "AnalyticsAgent",
    "AnalyticsResult",
    "PerformanceMetrics",
    # Production Agents (NEW - 2026-01-19)
    "ThumbnailAgent",
    "ThumbnailResult",
    "RetentionOptimizerAgent",
    "RetentionResult",
    "ValidatorAgent",
    "ValidationResult",
    "ValidationCheck",
    # Automation Cluster Agents (NEW - 2026-01-19)
    "WorkflowAgent",
    "WorkflowResult",
    "WorkflowState",
    "WorkflowStatus",
    "WorkflowStep",
    "MonitorAgent",
    "HealthResult",
    "HealthAlert",
    "APIStatus",
    "ResourceUsage",
    "HealthStatus",
    "RecoveryAgent",
    "RecoveryResult",
    "RecoveryStrategy",
    "ErrorCategory",
    "FailureRecord",
    "SchedulerAgent",
    "ScheduleResult",
    "ScheduledJob",
    "JobStatus",
    "JobType",
    # Quality Cluster Agents (NEW - 2026-01-19)
    "ComplianceAgent",
    "ComplianceResult",
    "ContentSafetyAgent",
    "SafetyResult",
    "RiskLevel",
    "AudioQualityAgent",
    "AudioQualityResult",
    "VideoQualityAgent",
    "VideoQualityResult",
    "AccessibilityAgent",
    "AccessibilityResult",
    # SEO Agents
    "SEOAgent",
    "SEOResult",
    "SEOStrategist",
    "SEOStrategyResult",
    # SEO Components (for advanced usage)
    "KeywordResearcher",
    "KeywordData",
    "SearchIntentAnalyzer",
    "SearchIntent",
    "CompetitorAnalyzer",
    "CompetitorReport",
    "CompetitorVideo",
    "PerformancePredictor",
    "CTRPrediction",
    "RetentionPrediction",
    "ABTestManager",
    "TitleVariant",
    "ContentCalendar",
    "TopicSuggestion",
    # CrewAI
    "YouTubeCrew",
]


# Version info
__version__ = "2.2.0"  # Updated with Quality Cluster Agents
__author__ = "Joe Team"
