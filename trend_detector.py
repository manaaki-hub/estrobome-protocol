"""
Estrobolome Trend Detection Agent
Runs via GitHub Actions every 6 hours. Fetches trending health topics,
filters for gut health / menopause / women 45+ relevance, outputs content ideas.
"""
import feedparser
import json
from datetime import datetime

# Trending sources (health/wellness)
SOURCES = [
    "https://news.google.com/rss/search?q=menopause+health&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=gut+health+fiber&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=longevity+womens+health&hl=en-US&gl=US&ceid=US:en",
]

# Keywords that signal relevance to our niche
RELEVANT_KEYWORDS = [
    "menopause", "perimenopause", "estrogen", "gut health", "fiber",
    "estrobolome", "microbiome", "longevity", "bioidentical", "hormone",
    "bloating", "hot flashes", "brain fog", "weight loss", "inflammation",
    "probiotic", "prebiotic", "fermented", "digestive", "hormonal",
]

def fetch_trends():
    """Fetch trending health topics from RSS feeds."""
    trends = []
    for url in SOURCES:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]:
                trends.append({
                    "title": entry.title,
                    "link": entry.link,
                    "published": entry.get("published", ""),
                    "summary": entry.get("summary", "")[:200],
                })
        except Exception as e:
            print(f"Error fetching {url}: {e}")
    return trends

def filter_relevant(trends):
    """Filter trends for niche relevance."""
    relevant = []
    for t in trends:
        text = (t["title"] + " " + t.get("summary", "")).lower()
        score = sum(1 for kw in RELEVANT_KEYWORDS if kw in text)
        if score >= 2:
            t["relevance_score"] = score
            relevant.append(t)
    return sorted(relevant, key=lambda x: x["relevance_score"], reverse=True)

def generate_content_ideas(trends):
    """Turn trends into content ideas."""
    ideas = []
    for t in trends[:5]:
        ideas.append({
            "topic": t["title"],
            "content_type": "carousel" if t["relevance_score"] >= 3 else "single_post",
            "angle": f"Estrobolome angle on: {t['title']}",
            "platforms": ["instagram", "tiktok", "pinterest"],
        })
    return ideas

def main():
    print(f"=== Trend Detection Run: {datetime.now()} ===")
    trends = fetch_trends()
    print(f"Fetched {len(trends)} trends")
    
    relevant = filter_relevant(trends)
    print(f"Filtered to {len(relevant)} relevant to niche")
    
    ideas = generate_content_ideas(relevant)
    
    output = {
        "run_time": str(datetime.now()),
        "trends": relevant,
        "content_ideas": ideas,
    }
    
    # Save to file for the content agent to pick up
    with open("trend_output.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print("Output saved to trend_output.json")
    for idea in ideas:
        print(f"  → {idea['angle']} [{idea['content_type']}]")
    
    return output

if __name__ == "__main__":
    main()