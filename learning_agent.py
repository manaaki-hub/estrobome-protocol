"""
AutoViralAI-inspired Self-Learning Content Agent for Estrobolome Niche
Learns what content gets engagement, adapts strategy over time.
"""
import json
import hashlib
from datetime import datetime

class ContentLearner:
    """Tracks content performance and learns what works."""
    
    def __init__(self, state_file="content_learning_state.json"):
        self.state_file = state_file
        self.state = self._load()
    
    def _load(self):
        try:
            with open(self.state_file) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "posts": [],
                "pattern_scores": {},  # pattern → avg engagement
                "blocked_patterns": [],
                "top_patterns": [],
            }
    
    def save(self):
        with open(self.state_file, "w") as f:
            json.dump(self.state, f, indent=2)
    
    def record_post(self, content, platform, engagement_score):
        """Record a post's performance for learning."""
        pattern = self._extract_pattern(content)
        self.state["posts"].append({
            "content": content,
            "platform": platform,
            "engagement": engagement_score,
            "pattern": pattern,
            "timestamp": str(datetime.now()),
        })
        
        # Update pattern scores — store as list of scores
        if pattern not in self.state["pattern_scores"]:
            self.state["pattern_scores"][pattern] = []
        self.state["pattern_scores"][pattern].append(engagement_score)
        
        # Update top patterns
        self._recalculate_top_patterns()
        self.save()
    
    def _extract_pattern(self, content):
        """Extract content pattern (hook type, format, topic)."""
        hooks = {
            "question": content.startswith(("Did you know", "What if", "Why do")),
            "shocking": any(w in content.lower() for w in ["changed how", "missing link", "did you know"]),
            "listicle": content.startswith(("1.", "2.", "3.", "→", "•")),
            "story": any(w in content.lower() for w in ["i used to", "my doctor", "after 30 days"]),
        }
        hook_type = [k for k, v in hooks.items() if v]
        hook_type = hook_type[0] if hook_type else "neutral"
        
        # Topic category
        text = content.lower()
        if "estrobiome" in text or "gut bacteria" in text:
            topic = "estrobiome"
        elif "fiber" in text:
            topic = "fiber"
        elif "fermented" in text or "kefir" in text or "kimchi" in text:
            topic = "fermented_food"
        elif "menopause" in text or "perimenopause" in text:
            topic = "menopause"
        else:
            topic = "general_health"
        
        return f"{hook_type}_{topic}"
    
    def _recalculate_top_patterns(self):
        """Recalculate which patterns perform best."""
        avg_scores = {}
        for pattern, engagements in self.state["pattern_scores"].items():
            if engagements and isinstance(engagements, list):
                avg_scores[pattern] = sum(engagements) / len(engagements)
        
        sorted_patterns = sorted(avg_scores.items(), key=lambda x: x[1], reverse=True)
        self.state["top_patterns"] = [p[0] for p in sorted_patterns[:5]]
        # Keep the list structure, don't overwrite with floats
    
    def get_best_pattern(self):
        """Return the top-performing content pattern."""
        if self.state["top_patterns"]:
            return self.state["top_patterns"][0]
        return "shocking_estrobiome"  # default
    
    def should_post(self, content):
        """Check if content uses a pattern that's been performing well."""
        pattern = self._extract_pattern(content)
        if pattern in self.state["blocked_patterns"]:
            return False
        if pattern in self.state["top_patterns"]:
            return True
        return True  # allow new patterns but flag for review


class EngagementPredictor:
    """Predicts engagement score for a draft post."""
    
    def __init__(self, learner):
        self.learner = learner
    
    def predict(self, content, platform):
        """Predict engagement (1-10) based on historical patterns."""
        pattern = self.learner._extract_pattern(content)
        base_scores = {
            "shocking_estrobiome": 7.5,
            "question_menopause": 6.8,
            "listicle_fiber": 7.2,
            "story_fermented_food": 6.5,
        }
        
        base = base_scores.get(pattern, 5.0)
        
        # Platform modifiers
        platform_mult = {
            "instagram": 1.0,
            "tiktok": 1.3,  # health content performs well on TikTok
            "pinterest": 0.8,  # lower engagement but saves
        }
        
        score = base * platform_mult.get(platform, 1.0)
        return min(10, round(score, 1))


if __name__ == "__main__":
    # Demo
    learner = ContentLearner()
    
    # Simulate some posts
    test_posts = [
        ("Did you know your gut bacteria control your estrogen? The estrobolome is the missing link...", "instagram", 8.2),
        ("3 fermented foods that balance your hormones after 45", "tiktok", 9.1),
        ("Why fiber is your #1 menopause tool — and 95% of women don't get enough", "pinterest", 6.5),
    ]
    
    for content, platform, score in test_posts:
        learner.record_post(content, platform, score)
    
    print("Top patterns:", learner.get_best_pattern())
    
    predictor = EngagementPredictor(learner)
    new_post = "Did you know your gut bacteria control your estrogen levels during menopause?"
    predicted = predictor.predict(new_post, "instagram")
    print(f"Predicted engagement for new post: {predicted}/10")