"""
SEO Optimizer for YouTube Shorts

Optimizes video metadata for YouTube Shorts:
- Titles: 50-60 characters with niche-specific keywords
- Descriptions: Hook + timestamps + hashtags + CTA
- Tags: 5-8 targeted tags based on niche

Supports 4 main niches:
- money_blueprints: Passive income, side hustles, financial freedom, investing
- mind_unlocked: Psychology, dark psychology, self-improvement, human behavior
- neural_forge: AI tools, ChatGPT, AI tutorials, productivity
- prof8ssor_ai: AI tutorials, prompt engineering, productivity hacks, tutorials

Usage:
    from src.content.seo_optimizer import SEOOptimizer

    optimizer = SEOOptimizer()

    # Optimize title (50-60 chars)
    title = optimizer.optimize_title("Passive Income with AI", "money_blueprints", 120)

    # Optimize description with timestamps
    description = optimizer.optimize_description(
        hook="Wall Street doesn't want you to know this...",
        benefits=["Make $500/month", "Start with zero investment"],
        channel_niche="money_blueprints"
    )

    # Generate SEO tags
    tags = optimizer.optimize_tags("money_blueprints", hook, benefits)
"""

import re
from typing import List, Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class SEOMetadata:
    """Container for optimized SEO metadata"""

    title: str
    description: str
    tags: List[str]
    character_counts: Dict[str, int]

    def __repr__(self):
        return f"""SEOMetadata(
    title='{self.title}' ({len(self.title)} chars)
    description_len={len(self.description)} chars
    tags={len(self.tags)} tags
)"""


class SEOOptimizer:
    """Optimize YouTube Shorts metadata for maximum reach and CTR"""

    # Niche-specific keyword pools
    NICHE_KEYWORDS = {
        "money_blueprints": {
            "primary": ["passive income", "side hustle", "financial freedom", "investing"],
            "secondary": [
                "make money online",
                "wealth building",
                "stock market",
                "real estate",
                "dividends",
                "crypto",
                "forex",
                "entrepreneurship",
                "business ideas",
                "financial independence",
            ],
            "long_tail": [
                "how to make passive income",
                "side hustle ideas",
                "ways to earn money",
                "investment strategies",
                "wealth mindset",
            ],
        },
        "mind_unlocked": {
            "primary": ["psychology facts", "dark psychology", "self-improvement", "human behavior"],
            "secondary": [
                "manipulation tactics",
                "narcissist signs",
                "cognitive biases",
                "body language",
                "psychology tricks",
                "mindset",
                "motivation",
                "anxiety",
                "stoicism",
                "mental health",
            ],
            "long_tail": [
                "psychological manipulation",
                "how to spot a liar",
                "signs of a narcissist",
                "psychology behind",
                "mind control techniques",
            ],
        },
        "neural_forge": {
            "primary": ["AI tools", "artificial intelligence", "ChatGPT", "AI tutorial"],
            "secondary": [
                "machine learning",
                "deep learning",
                "neural networks",
                "AI automation",
                "AI productivity",
                "generative AI",
                "LLM",
                "prompt engineering",
                "AI business",
                "AI money making",
            ],
            "long_tail": [
                "how to use ChatGPT",
                "AI tools for business",
                "artificial intelligence tutorial",
                "AI automation tips",
                "ChatGPT prompts",
            ],
        },
        "prof8ssor_ai": {
            "primary": ["AI tutorial", "prompt engineering", "productivity hacks", "ChatGPT"],
            "secondary": [
                "AI tools tutorial",
                "ChatGPT tutorial",
                "AI learning",
                "automation tips",
                "productivity",
                "efficiency",
                "AI skills",
                "online learning",
                "tech tutorial",
                "AI course",
            ],
            "long_tail": [
                "how to learn AI",
                "ChatGPT tutorial for beginners",
                "productivity tips with AI",
                "AI tools explained",
                "prompt engineering guide",
            ],
        },
    }

    # Title formula patterns by niche (50-60 chars max)
    TITLE_FORMULAS = {
        "money_blueprints": [
            "{keyword}: {promise}",  # "Passive Income: $500/Month Guide"
            "{number} Ways to {verb} {keyword}",  # "5 Ways to Generate Passive Income"
            "{keyword} {number}X: {evidence}",  # "Passive Income 10X: How I Did It"
            "The ${amount} {keyword} Secret",  # "The $500 Passive Income Secret"
            "{keyword} in {timeframe}: {promise}",  # "Passive Income in 2026: Full Guide"
        ],
        "mind_unlocked": [
            "{number} Signs You're {condition}",  # "5 Signs You're Being Manipulated"
            "{keyword} {evidence}: {insight}",  # "Dark Psychology: What They Hide"
            "Why {group} {verb} {keyword}",  # "Why Narcissists Hide Psychology"
            "The {keyword} Trick {group} Uses",  # "The Psychology Trick Manipulators Use"
            "{keyword} Facts Nobody Tells You",  # "Psychology Facts Nobody Tells You"
        ],
        "neural_forge": [
            "{keyword} {evidence}: Beginner's Guide",  # "ChatGPT: Beginner's Complete Guide"
            "{number} {keyword} Tools That {promise}",  # "5 AI Tools That Save 10 Hours/Week"
            "{keyword} Automation in {timeframe}",  # "AI Automation in 2026: Full Setup"
            "Master {keyword} in {number} Minutes",  # "Master ChatGPT in 10 Minutes"
            "The {keyword} {evidence} {group} Use",  # "The AI Tools Professionals Use"
        ],
        "prof8ssor_ai": [
            "{keyword} Tutorial: {promise}",  # "ChatGPT Tutorial: $500/Month Guide"
            "Learn {keyword} {evidence} (Free)",  # "Learn AI Tools (Free & Easy)"
            "{number} {keyword} Hacks for {verb}",  # "5 ChatGPT Hacks for Writing"
            "{keyword}: From Zero to {promise}",  # "Prompt Engineering: Zero to Expert"
            "Beginner's {keyword} Masterclass",  # "Beginner's AI Tutorial Masterclass"
        ],
    }

    # Description structure template
    DESCRIPTION_TEMPLATE = """{hook}

TIMESTAMPS:
{timestamps}

RELATED:
{hashtags}

{cta}"""

    # Call-to-action variants by niche
    CTA_VARIANTS = {
        "money_blueprints": [
            "Subscribe for more wealth-building strategies",
            "Hit subscribe and turn on notifications for daily money tips",
            "Subscribe to unlock your financial freedom",
            "Like, subscribe, and share this with your future self",
        ],
        "mind_unlocked": [
            "Subscribe to unlock the secrets of human psychology",
            "Hit subscribe and join our growing psychology community",
            "Like and subscribe for daily psychology insights",
            "Subscribe for more mind-bending psychology facts",
        ],
        "neural_forge": [
            "Subscribe for AI tools and automation tutorials",
            "Hit subscribe for the latest AI tools and hacks",
            "Subscribe to master AI tools and automation",
            "Like, subscribe, and share AI knowledge",
        ],
        "prof8ssor_ai": [
            "Subscribe for free AI tutorials and productivity hacks",
            "Hit subscribe to learn AI from scratch",
            "Subscribe for daily AI and productivity tips",
            "Like and subscribe for expert tutorials",
        ],
    }

    def __init__(self):
        """Initialize SEO Optimizer"""
        self.validated_niches = list(self.NICHE_KEYWORDS.keys())

    def _validate_niche(self, niche: str) -> str:
        """Validate and normalize niche name"""
        if niche not in self.validated_niches:
            raise ValueError(
                f"Invalid niche '{niche}'. Must be one of: {', '.join(self.validated_niches)}"
            )
        return niche

    def optimize_title(self, topic: str, niche: str, duration_s: int = 45) -> str:
        """
        Generate SEO-optimized title (50-60 characters)

        Args:
            topic: Main topic/hook (e.g., "Passive Income with AI")
            niche: Channel niche (money_blueprints, mind_unlocked, neural_forge, prof8ssor_ai)
            duration_s: Video duration in seconds (for context)

        Returns:
            Optimized title string (50-60 chars)
        """
        niche = self._validate_niche(niche)

        # Extract keywords from topic
        keywords = self._extract_keywords(topic, niche)
        primary_keyword = keywords[0] if keywords else topic

        # Select appropriate formula
        formulas = self.TITLE_FORMULAS.get(niche, self.TITLE_FORMULAS["money_blueprints"])
        formula = formulas[len(topic) % len(formulas)]

        # Generate title candidates
        candidates = []

        # Formula-based titles
        title1 = self._format_title_formula(formula, primary_keyword, topic, niche)
        candidates.append(title1)

        # Direct hook format
        if len(topic) <= 55:
            candidates.append(topic)

        # Numbers attract clicks
        for num in ["3", "5", "7", "10"]:
            candidate = f"{num} {primary_keyword} Tips"
            candidates.append(candidate)

        # Urgency/scarcity
        urgency_titles = [
            f"The {primary_keyword} Secret Nobody Tells",
            f"Why You're Losing at {primary_keyword}",
            f"The Hidden {primary_keyword} Truth",
        ]
        candidates.extend(urgency_titles)

        # Select best candidate (target 50-60 chars)
        best = self._select_best_title(candidates)
        return best[:60]  # Hard limit

    def optimize_description(
        self,
        hook: str,
        benefits: List[str],
        channel_niche: str,
        duration_s: int = 45,
    ) -> str:
        """
        Generate SEO-optimized description with timestamps and CTAs

        Args:
            hook: Opening hook from script (e.g., "Wall Street doesn't want you to know...")
            benefits: List of key benefits/points (e.g., ["Make $500/month", "Zero investment"])
            channel_niche: Channel niche
            duration_s: Video duration in seconds

        Returns:
            Formatted description with timestamps, hashtags, and CTA
        """
        channel_niche = self._validate_niche(channel_niche)

        # Create timestamps section
        timestamps = self._generate_timestamps(benefits, duration_s)

        # Create hashtags from niche keywords
        hashtags = self._generate_hashtags(channel_niche, hook, benefits)

        # Select appropriate CTA
        cta_options = self.CTA_VARIANTS.get(channel_niche, self.CTA_VARIANTS["money_blueprints"])
        cta = cta_options[len(hook) % len(cta_options)]

        # Format description
        description = self.DESCRIPTION_TEMPLATE.format(
            hook=hook,
            timestamps=timestamps,
            hashtags=hashtags,
            cta=cta,
        )

        return description

    def optimize_tags(self, niche: str, hook: str = "", benefits: List[str] = None) -> List[str]:
        """
        Generate 5-8 SEO-optimized tags for maximum reach

        Args:
            niche: Channel niche
            hook: Video hook (for context)
            benefits: List of benefits (for context)

        Returns:
            List of 5-8 optimized tags
        """
        niche = self._validate_niche(niche)
        benefits = benefits or []

        tags = []

        # 1. Primary keywords (highest priority)
        primary_keywords = self.NICHE_KEYWORDS[niche]["primary"]
        tags.extend(primary_keywords[:2])

        # 2. Secondary keywords (medium priority)
        secondary_keywords = self.NICHE_KEYWORDS[niche]["secondary"]
        tags.extend(secondary_keywords[: 3 if len(tags) < 5 else 2])

        # 3. Long-tail keywords (lower competition)
        long_tail = self.NICHE_KEYWORDS[niche]["long_tail"]
        remaining = 8 - len(tags)
        tags.extend(long_tail[:remaining])

        # 4. Context-specific tags from benefits
        for benefit in benefits[:2]:
            keyword = benefit.split(":")[0].strip().lower()
            if len(keyword) > 3 and keyword not in tags:
                tags.append(keyword)

        # Ensure we have exactly 5-8 tags
        tags = list(dict.fromkeys(tags))  # Remove duplicates
        tags = tags[:8]  # Cap at 8

        # Pad to minimum 5 if needed
        if len(tags) < 5:
            tags.extend(long_tail[: 5 - len(tags)])

        return list(dict.fromkeys(tags))[:8]

    # ============================================================
    # HELPER METHODS
    # ============================================================

    def _extract_keywords(self, text: str, niche: str) -> List[str]:
        """Extract relevant keywords from text"""
        text_lower = text.lower()
        keywords = []

        # Check for primary and secondary keywords
        all_keywords = (
            self.NICHE_KEYWORDS[niche]["primary"] + self.NICHE_KEYWORDS[niche]["secondary"]
        )

        for keyword in all_keywords:
            if keyword.lower() in text_lower:
                keywords.append(keyword)

        return keywords

    def _format_title_formula(self, formula: str, primary_keyword: str, topic: str, niche: str) -> str:
        """Format title formula with actual values"""
        # Replace placeholders
        title = formula

        replacements = {
            "{keyword}": primary_keyword,
            "{number}": "5",
            "{promise}": "Complete Guide",
            "{verb}": "earn",
            "{evidence}": "Proven Method",
            "{group}": "Experts",
            "{condition}": "Being Manipulated",
            "{amount}": "500",
            "{timeframe}": "2026",
            "{insight}": "Full Breakdown",
        }

        for placeholder, value in replacements.items():
            title = title.replace(placeholder, value)

        # Clean up
        title = re.sub(r"\s+", " ", title).strip()

        return title

    def _select_best_title(self, candidates: List[str]) -> str:
        """Select best title based on length and quality heuristics"""
        # Prefer titles between 50-60 characters
        best = candidates[0]
        best_score = abs(len(best) - 55)

        for candidate in candidates[1:]:
            score = abs(len(candidate) - 55)
            # Prefer shorter if equal score (easier to read)
            if score < best_score or (score == best_score and len(candidate) < len(best)):
                best = candidate
                best_score = score

        return best

    def _generate_timestamps(self, benefits: List[str], duration_s: int) -> str:
        """Generate YouTube-style timestamps"""
        timestamps = ["0:00 - Introduction"]

        if len(benefits) > 0:
            mid_point = duration_s // 2
            timestamps.append(f"{mid_point // 60}:{mid_point % 60:02d} - Key Points")

        timestamps.append(f"{duration_s // 60}:{duration_s % 60:02d} - Conclusion")

        return "\n".join(timestamps)

    def _generate_hashtags(self, niche: str, hook: str, benefits: List[str]) -> str:
        """Generate hashtags from niche keywords and content"""
        hashtags = set()

        # Add primary keywords as hashtags
        primary = self.NICHE_KEYWORDS[niche]["primary"]
        for keyword in primary[:3]:
            # Convert to hashtag
            hashtag = "#" + keyword.replace(" ", "")
            hashtags.add(hashtag)

        # Add benefit-based hashtags
        for benefit in benefits[:2]:
            # Extract words from benefit
            words = benefit.lower().split()
            for word in words[:2]:
                if len(word) > 3 and word.isalpha():
                    hashtags.add(f"#{word}")

        # Add trending general hashtags
        hashtags.add("#YouTube")
        hashtags.add("#Shorts")

        # Format as comma-separated
        return " ".join(sorted(hashtags)[:8])

    def get_full_metadata(
        self,
        topic: str,
        hook: str,
        benefits: List[str],
        niche: str,
        duration_s: int = 45,
    ) -> SEOMetadata:
        """
        Generate complete SEO metadata package

        Args:
            topic: Video topic
            hook: Opening hook
            benefits: List of key benefits
            niche: Channel niche
            duration_s: Video duration in seconds

        Returns:
            SEOMetadata object with title, description, and tags
        """
        title = self.optimize_title(topic, niche, duration_s)
        description = self.optimize_description(hook, benefits, niche, duration_s)
        tags = self.optimize_tags(niche, hook, benefits)

        return SEOMetadata(
            title=title,
            description=description,
            tags=tags,
            character_counts={
                "title": len(title),
                "description": len(description),
                "tags": len(tags),
            },
        )


# ============================================================
# MODULE INTERFACE
# ============================================================


def get_seo_optimizer() -> SEOOptimizer:
    """Get SEO optimizer instance"""
    return SEOOptimizer()


if __name__ == "__main__":
    # Demo: Test SEO optimization for all 4 channels
    optimizer = SEOOptimizer()

    test_cases = [
        {
            "niche": "money_blueprints",
            "topic": "Passive Income with AI in 2026",
            "hook": "Wall Street doesn't want you to know these tricks...",
            "benefits": ["Earn $500-$10,000/month", "Start with zero investment"],
            "duration": 120,
        },
        {
            "niche": "mind_unlocked",
            "topic": "Dark Psychology Manipulation Tactics",
            "hook": "Narcissists use these 5 tricks to control you...",
            "benefits": ["Recognize manipulation instantly", "Protect yourself from toxic people"],
            "duration": 600,
        },
        {
            "niche": "neural_forge",
            "topic": "ChatGPT Automation for Beginners",
            "hook": "This AI tool can save you 20 hours per week...",
            "benefits": ["Automate 80% of your work", "No coding required"],
            "duration": 600,
        },
        {
            "niche": "prof8ssor_ai",
            "topic": "Prompt Engineering Masterclass",
            "hook": "Learn the exact prompts top AI experts use...",
            "benefits": ["Write perfect prompts every time", "10X your AI productivity"],
            "duration": 900,
        },
    ]

    print("\n" + "=" * 80)
    print("SEO OPTIMIZER DEMO - YouTube Shorts Metadata")
    print("=" * 80)

    for i, test in enumerate(test_cases, 1):
        niche = test["niche"]
        print(f"\n[TEST {i}] {niche.upper()}")
        print("-" * 80)

        metadata = optimizer.get_full_metadata(
            topic=test["topic"],
            hook=test["hook"],
            benefits=test["benefits"],
            niche=niche,
            duration_s=test["duration"],
        )

        print(f"\nTitle ({metadata.character_counts['title']} chars, target 50-60):")
        print(f"  > {metadata.title}")

        print(f"\nDescription ({metadata.character_counts['description']} chars):")
        print(metadata.description)

        print(f"\nTags ({len(metadata.tags)} tags):")
        print(f"  > {', '.join(metadata.tags)}")

        # Show before/after comparison
        print(f"\n[OK] Metadata optimized for maximum YouTube reach and CTR")
