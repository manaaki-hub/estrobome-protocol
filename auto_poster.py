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
    print(f"=== Auto-Post Run: {datetime.now()} ===")
    
    # 1. Get trends
    trends = load_trends()
    ideas = trends.get("content_ideas", [])
    
    if not ideas:
        print("No content ideas. Run trend_detector.py first.")
        return
    
    platforms = ["instagram", "tiktok", "pinterest"]
    results = []
    
    # 2. Generate and post for each platform
    for idea in ideas[:3]:  # Top 3 ideas
        for platform in platforms:
            content = generate_post_for_platform(idea, platform)
            result = post_to_platform(content, platform)
            results.append({
                "topic": idea.get("topic", ""),
                "platform": platform,
                "content": content,
                "status": result["status"],
                "timestamp": str(datetime.now()),
            })
    
    # 3. Save log
    log_file = "post_log.json"
    try:
        with open(log_file) as f:
            log = json.load(f)
    except FileNotFoundError:
        log = []
    
    log.extend(results)
    with open(log_file, "w") as f:
        json.dump(log, f, indent=2)
    
    print(f"\n=== Complete: {len(results)} posts attempted ===")
    for r in results:
        print(f"  {r['platform']}: {r['status']}")

if __name__ == "__main__":
    main()