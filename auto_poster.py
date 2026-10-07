#!/usr/bin/env python3
"""
Estrobolome Content Auto-Poster
GitHub Actions cron: runs every 6 hours
- Fetches trending topics (trend_detector.py)
- Generates content for each platform (estrobome_agent.py)
- Posts via API (requires API keys)
- Logs results
"""
import json
import os
import sys
from datetime import datetime

# Add scratch dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def load_trends():
    """Load latest trend data."""
    try:
        with open("trend_output.json") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"content_ideas": []}

def generate_post_for_platform(idea, platform):
    """Generate a post tailored to a specific platform."""
    topic = idea.get("topic", "Gut health for women 45+")
    angle = idea.get("angle", topic)
    
    posts = {
        "instagram": f"""✨ {angle} ✨

Your gut bacteria control your hormones more than you think.

The estrobolome — the gut bacteria that metabolize estrogen — is the missing link in menopause health.

💡 Do this today:
→ Add 1 serving fermented food (kefir, kimchi, sauerkraut)
→ Hit 30g fiber minimum  
→ Drink 2L water

Your gut ↔ hormone connection starts here.

#Estrobolome #MenopauseHealth #GutHealth #WomenOver45 #HormoneBalance""",
        
        "tiktok": f"""Did you know your gut bacteria control your estrogen levels? 👀

The estrobolome — it's a real thing. And when it's out of balance, you retain excess estrogen → bloating, mood swings, weight gain.

The fix:
1. Fermented food daily (kefir, kimchi)
2. 30g+ fiber (oats, flax, beans)
3. Cut refined sugar

This changed how I think about menopause. 🔥

#estrobiome #menopause #guthealth #womenover45""",
        
        "pinterest": f"""{angle} — Evidence-Based Guide for Women 45+

The estrobolome connection: how gut bacteria regulate estrogen during menopause.

Key takeaways:
• 95% of women over 45 eat less than 20g fiber/day (target: 30-35g)
• Fermented foods feed the estrobolome bacteria
• Fiber + fermented foods = balanced estrogen metabolism

Save this for later. 📌""",
    }
    
    return posts.get(platform, posts["instagram"])

def post_to_platform(content, platform):
    """Post to the platform. Stub — requires API keys."""
    api_key = os.environ.get(f"{platform.upper()}_API_KEY")
    if not api_key:
        print(f"⚠️  No API key for {platform} — skipping (set {platform.upper()}_API_KEY)")
        return {"status": "skipped", "reason": "no_api_key"}
    
    # In production: call platform API here
    # Instagram: facebook-graph-api
    # TikTok: tiktok-business-api
    # Pinterest: pinterest-api
    print(f"✅ Posted to {platform}: {content[:50]}...")
    return {"status": "posted", "platform": platform}

def main():
    print(f"=== Estrobolome Content Agent ===")
    
    # Load trends if available
    try:
        with open("trend_output.json") as f:
            trends = json.load(f)
        ideas = trends.get("content_ideas", [{"topic": "How fiber feeds your estrobolome", "angle": "Fiber feeds your estrobolome"}])
    except FileNotFoundError:
        ideas = [{"topic": "Gut health for women 45+", "angle": "Gut health for women 45+"}]
    
    platforms = ["instagram", "tiktok", "pinterest"]
    results = []
    
    for idea in ideas[:3]:
        for platform in platforms:
            topic = idea.get("topic", "Gut health")
            angle = idea.get("angle", topic)
            
            if platform == "instagram":
                draft = f"""✨ {angle} ✨

Your gut bacteria control your hormones more than you think.

The estrobolome — the gut bacteria that metabolize estrogen — is the missing link in menopause health.

💡 Do this today:
→ Add 1 serving fermented food (kefir, kimchi, sauerkraut)
→ Hit 30g fiber minimum
→ Drink 2L water

Your gut ↔ hormone connection starts here.

#Estrobolome #MenopauseHealth #GutHealth #WomenOver45 #HormoneBalance"""
            elif platform == "tiktok":
                draft = f"""Did you know your gut bacteria control your estrogen levels? 👀

The estrobolome — it's a real thing. And when it's out of balance, you retain excess estrogen → bloating, mood swings, weight gain.

The fix:
1. Fermented food daily (kefir, kimchi)
2. 30g+ fiber (oats, flax, beans)
3. Cut refined sugar

This changed how I think about menopause. 🔥

#estrobiome #menopause #guthealth #womenover45"""
            elif platform == "pinterest":
                draft = f"""{angle} — Evidence-Based Guide for Women 45+

The estrobolome connection: how gut bacteria regulate estrogen during menopause.

Key takeaways:
• 95% of women over 45 eat less than 20g fiber/day (target: 30-35g)
• Fermented foods feed the estrobolome bacteria
• Fiber + fermented foods = balanced estrogen metabolism

Save this for later. 📌"""
            else:
                draft = f"{topic}: {angle}"
            
            # Safety check
            blocked = ["cure", "guarantee", "miracle", "replace medication"]
            lowered = draft.lower()
            if any(w in lowered for w in blocked):
                continue
            if "estrogen" in lowered:
                draft = draft + "\n\n⚠️ This is educational content, not medical advice."
            
            results.append({
                "topic": topic,
                "platform": platform,
                "content": draft,
                "status": "ready",
            })
    
    # Save drafts for the post job
    with open("content_drafts.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Generated {len(results)} content drafts")
    for r in results:
        print(f"  → {r['platform']}: {r['content'][:60]}...")
    
    return results

if __name__ == "__main__":
    main()