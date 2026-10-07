#!/usr/bin/env python3
"""
Estrobolome Content Agent v2
Supports TikTok (Access-Token header), Instagram (container flow),
Facebook (Page feed), Pinterest (OAuth2 Bearer).
"""
import json
import os
import sys
from datetime import datetime

# Platform-specific posting
def post_to_tiktok(content, api_key):
    """Post to TikTok via Marketing API."""
    if not api_key:
        return {"status": "skipped", "reason": "no_api_key"}
    
    url = "https://business-api.tiktok.com/open_api/v1.3/aweme/v1/publish/"
    headers = {
        "Access-Token": api_key,  # TikTok uses custom header
        "Content-Type": "application/json",
    }
    payload = {
        "advertiser_id": os.environ.get("TIKTOK_ADVERTISER_ID", ""),
        "video": {
            "text": content[:150],  # TikTok caption limit
        }
    }
    
    # In production: requests.post(url, headers=headers, json=payload)
    print(f"  → TikTok: would post with Access-Token header")
    return {"status": "ready", "platform": "tiktok"}

def post_to_instagram(content, api_key):
    """Post to Instagram via Graph API container flow."""
    if not api_key:
        return {"status": "skipped", "reason": "no_api_key"}
    
    ig_user_id = os.environ.get("INSTAGRAM_USER_ID", "")
    
    # Step 1: Create container
    container_url = f"https://graph.facebook.com/v25.0/{ig_user_id}/media"
    # Step 2: Poll status
    # Step 3: Publish
    # In production: actual API calls here
    print(f"  → Instagram: container flow (2-step)")
    return {"status": "ready", "platform": "instagram"}

def post_to_facebook(content, api_key):
    """Post to Facebook Page via Graph API."""
    if not api_key:
        return {"status": "skipped", "reason": "no_api_key"}
    
    page_id = os.environ.get("FACEBOOK_PAGE_ID", "")
    url = f"https://graph.facebook.com/v25.0/{page_id}/feed"
    # POST with message + access_token
    print(f"  → Facebook: POST /{page_id}/feed")
    return {"status": "ready", "platform": "facebook"}

def post_to_pinterest(content, api_key, board_id):
    """Post pin to Pinterest."""
    if not api_key:
        return {"status": "skipped", "reason": "no_api_key"}
    
    url = "https://api.pinterest.com/v5/pins"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "board_id": board_id,
        "title": content[:100],
        "description": content[:800],
        "media_source": {"image_url": "https://yourimage.com/image.jpg"}
    }
    # In production: requests.post(url, headers=headers, json=payload)
    print(f"  → Pinterest: POST /v5/pins")
    return {"status": "ready", "platform": "pinterest"}

def generate_post_for_platform(idea, platform):
    """Generate a post tailored to a specific platform."""
    topic = idea.get("topic", "Gut health for women 45+")
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
    elif platform == "facebook":
        draft = f"""✨ {angle} ✨

Your gut bacteria control your hormones more than you think.

The estrobolome — the gut bacteria that metabolize estrogen — is the missing link in menopause health for women 45+.

💡 Do this today:
→ Add 1 serving fermented food (kefir, kimchi, sauerkraut)
→ Hit 30g fiber minimum
→ Drink 2L water

Your gut ↔ hormone connection starts here.

#Estrobolome #MenopauseHealth #GutHealth #WomenOver45 #HormoneBalance"""
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
        return None
    if "estrogen" in lowered:
        draft = draft + "\n\n⚠️ This is educational content, not medical advice."
    
    return draft

def main():
    print(f"=== Estrobolome Content Agent v2 ===")
    
    # Load trends if available
    try:
        with open("trend_output.json") as f:
            trends = json.load(f)
        ideas = trends.get("content_ideas", [{"topic": "How fiber feeds your estrobolome", "angle": "Fiber feeds your estrobolome"}])
    except FileNotFoundError:
        ideas = [{"topic": "Gut health for women 45+", "angle": "Gut health for women 45+"}]
    
    # Get API keys
    tiktok_key = os.environ.get("TIKTOK_API_KEY", "")
    instagram_key = os.environ.get("INSTAGRAM_API_KEY", "")
    facebook_key = os.environ.get("FACEBOOK_API_KEY", "")
    pinterest_key = os.environ.get("PINTEREST_API_KEY", "")
    pinterest_board = os.environ.get("PINTEREST_BOARD_ID", "")
    
    platforms = {
        "instagram": {"key": instagram_key, "post_fn": post_to_instagram},
        "tiktok": {"key": tiktok_key, "post_fn": post_to_tiktok},
        "facebook": {"key": facebook_key, "post_fn": post_to_facebook},
        "pinterest": {"key": pinterest_key, "board": pinterest_board, "post_fn": post_to_pinterest},
    }
    
    results = []
    
    for idea in ideas[:3]:
        for platform_name, platform in platforms.items():
            content = generate_post_for_platform(idea, platform_name)
            if not content:
                continue
            
            # Post via platform-specific function
            if platform_name == "pinterest":
                result = platform["post_fn"](content, platform["key"], platform.get("board", ""))
            else:
                result = platform["post_fn"](content, platform["key"])
            
            results.append({
                "topic": idea.get("topic", ""),
                "platform": platform_name,
                "content": content,
                "status": result["status"],
                "timestamp": str(datetime.now()),
            })
    
    # Save drafts for the post job
    with open("content_drafts.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nGenerated {len(results)} posts")
    for r in results:
        print(f"  [{r['platform']}] {r['content'][:60]}...")
    
    return results

if __name__ == "__main__":
    main()