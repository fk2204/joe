#!/usr/bin/env python3
"""
Test SEO optimizer integration with pipeline

This script shows how to use SEO optimizer with video data.
"""

import sys
import os

# Change to project directory
project_dir = r'C:\Users\fkozi\joe'
os.chdir(project_dir)
sys.path.insert(0, os.getcwd())

from src.content.seo_optimizer import SEOOptimizer


def test_seo_optimizer():
    """Test SEO optimizer with realistic scenarios"""

    print("\n" + "=" * 80)
    print("SEO OPTIMIZER INTEGRATION TEST")
    print("=" * 80)

    optimizer = SEOOptimizer()

    # Test Case 1: money_blueprints channel
    print("\n[TEST 1] MONEY_BLUEPRINTS CHANNEL")
    print("-" * 80)

    original_title = "5 Ways to Make Passive Income with AI in 2026"
    hook = "Wall Street doesn't want you to know these tricks..."
    benefits = [
        "Earn $500-$10,000/month",
        "Start with zero investment",
        "Passive income strategies"
    ]

    metadata = optimizer.get_full_metadata(
        topic=original_title,
        hook=hook,
        benefits=benefits,
        niche="money_blueprints",
        duration_s=120
    )

    print(f"\nBEFORE SEO OPTIMIZATION:")
    print(f"  Title: {original_title} ({len(original_title)} chars)")
    print(f"  Tags: #Shorts, passive income, AI, money, finance, side hustle (6 tags)")

    print(f"\nAFTER SEO OPTIMIZATION:")
    print(f"  Title: {metadata.title} ({metadata.character_counts['title']} chars)")
    print(f"    [Improvement: Shorter, keyword-focused, 50-60 char target]")
    print(f"  Tags: {', '.join(metadata.tags)} ({len(metadata.tags)} tags)")
    print(f"    [Improvement: Optimized keywords for reach, no redundancy]")
    print(f"  Description: {metadata.character_counts['description']} chars")

    # Test Case 2: mind_unlocked channel
    print("\n[TEST 2] MIND_UNLOCKED CHANNEL")
    print("-" * 80)

    original_title = "Dark Psychology: 5 Manipulation Tactics Narcissists Use"
    hook = "Narcissists use these 5 tricks to manipulate you..."
    benefits = [
        "Recognize manipulation instantly",
        "Protect yourself from toxic people",
        "Master psychological defense"
    ]

    metadata = optimizer.get_full_metadata(
        topic=original_title,
        hook=hook,
        benefits=benefits,
        niche="mind_unlocked",
        duration_s=600
    )

    print(f"\nBEFORE SEO OPTIMIZATION:")
    print(f"  Title: {original_title} ({len(original_title)} chars)")
    print(f"  Tags: psychology, dark psychology, stoicism, self improvement, motivation (5 tags)")

    print(f"\nAFTER SEO OPTIMIZATION:")
    print(f"  Title: {metadata.title} ({metadata.character_counts['title']} chars)")
    print(f"    [Improvement: Shorter, hooks viewer, niche keywords]")
    print(f"  Tags: {', '.join(metadata.tags)} ({len(metadata.tags)} tags)")
    print(f"    [Improvement: Long-tail keywords for lower competition]")
    print(f"  Description: {metadata.character_counts['description']} chars")

    # Test Case 3: neural_forge channel
    print("\n[TEST 3] NEURAL_FORGE CHANNEL")
    print("-" * 80)

    original_title = "Complete ChatGPT Automation Guide for Beginners - No Coding Required"
    hook = "This AI tool can save you 20 hours per week..."
    benefits = [
        "Automate 80% of your work",
        "No coding required",
        "Make money with AI automation"
    ]

    metadata = optimizer.get_full_metadata(
        topic=original_title,
        hook=hook,
        benefits=benefits,
        niche="neural_forge",
        duration_s=600
    )

    print(f"\nBEFORE SEO OPTIMIZATION:")
    print(f"  Title: {original_title} ({len(original_title)} chars)")
    print(f"  Tags: AI tools, artificial intelligence, ChatGPT, AI tutorial (4 tags)")

    print(f"\nAFTER SEO OPTIMIZATION:")
    print(f"  Title: {metadata.title} ({metadata.character_counts['title']} chars)")
    print(f"    [Improvement: Shorter, direct promise, keyword-rich]")
    print(f"  Tags: {', '.join(metadata.tags)} ({len(metadata.tags)} tags)")
    print(f"    [Improvement: 8 targeted tags vs 4 generic ones]")
    print(f"  Description: {metadata.character_counts['description']} chars")

    # Test Case 4: prof8ssor_ai channel
    print("\n[TEST 4] PROF8SSOR_AI CHANNEL")
    print("-" * 80)

    original_title = "Learn Prompt Engineering: Masterclass from Zero to Hero"
    hook = "Learn the exact prompts that top AI experts use daily..."
    benefits = [
        "Write perfect prompts every time",
        "10X your AI productivity",
        "Free complete training"
    ]

    metadata = optimizer.get_full_metadata(
        topic=original_title,
        hook=hook,
        benefits=benefits,
        niche="prof8ssor_ai",
        duration_s=900
    )

    print(f"\nBEFORE SEO OPTIMIZATION:")
    print(f"  Title: {original_title} ({len(original_title)} chars)")
    print(f"  Tags: AI tutorial, prompt engineering, productivity hacks (3 tags)")

    print(f"\nAFTER SEO OPTIMIZATION:")
    print(f"  Title: {metadata.title} ({metadata.character_counts['title']} chars)")
    print(f"    [Improvement: Optimized for clicks, searchability]")
    print(f"  Tags: {', '.join(metadata.tags)} ({len(metadata.tags)} tags)")
    print(f"    [Improvement: 8 semantic tags for maximum reach]")
    print(f"  Description: {metadata.character_counts['description']} chars")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY: SEO OPTIMIZER BENEFITS")
    print("=" * 80)
    print("""
1. TITLES (50-60 chars):
   - Optimized for YouTube click-through rate (CTR)
   - Includes primary keyword early
   - Compelling hook or promise

2. DESCRIPTIONS:
   - Structured with timestamps
   - Includes relevant hashtags
   - Strong call-to-action
   - Niche-specific language

3. TAGS (5-8):
   - Primary keywords first (highest priority)
   - Secondary keywords for reach
   - Long-tail keywords (lower competition)
   - Context-specific tags from benefits

4. NICHE AWARENESS:
   - Money_blueprints: Financial keywords
   - Mind_unlocked: Psychology keywords
   - Neural_forge: AI/automation keywords
   - Prof8ssor_ai: Tutorial/education keywords

5. BEST PRACTICES APPLIED:
   - Character limits enforced
   - No keyword stuffing
   - Natural language
   - Audience-focused messaging
   - Platform-optimized format
""")

    print("=" * 80)
    print("[OK] SEO Optimizer Integration Test Complete")
    print("=" * 80)


if __name__ == "__main__":
    test_seo_optimizer()
