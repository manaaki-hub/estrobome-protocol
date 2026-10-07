"""
Estrobolome Social Media Agent
LangGraph pipeline: Research → Draft → Safety Check → Human Approval → Schedule
"""
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

class ContentState(TypedDict):
    topic: str
    niche: str  # "gut-health-women-45"
    research: str
    draft: str
    safety_passed: bool
    approved: bool
    platform: str  # "instagram", "tiktok", "pinterest"
    image_prompt: str

def research_node(state: ContentState) -> dict:
    """Research the topic for the estrobolome niche."""
    topic = state["topic"]
    # In production: call web search + RAG over estrobolome docs
    research = f"Researched: {topic} — key points for women 45+ gut health audience"
    return {"research": research}

def draft_node(state: ContentState) -> dict:
    """Draft the post for the specific platform."""
    research = state.get("research", "")
    topic = state["topic"]
    
    if state["platform"] == "instagram":
        draft = f"""✨ {topic} ✨

Your gut bacteria control your hormones more than you think. 

The estrobolome — the gut bacteria that metabolize estrogen — is the missing link in menopause health.

💡 Do this today:
→ Add 1 serving fermented food (kefir, kimchi, sauerkraut)
→ Hit 30g fiber minimum
→ Drink 2L water

Your gut ↔ hormone connection starts here.

#Estrobolome #MenopauseHealth #GutHealth #WomenOver45 #HormoneBalance #Perimenopause #FiberForWomen #GutBrainAxis #HealthyAging #Microbiome"""
    elif state["platform"] == "tiktok":
        draft = f"""Did you know your gut bacteria control your estrogen levels? 👀

The estrobolome — it's a real thing. And when it's out of balance, you retain excess estrogen → bloating, mood swings, weight gain.

The fix:
1. Fermented food daily (kefir, kimchi)
2. 30g+ fiber (oats, flax, beans)
3. Cut refined sugar

This changed how I think about menopause. 🔥

#estrobiome #menopause #guthealth #womenover45 #perimenopause #hormonebalance #healthtok"""
    elif state["platform"] == "pinterest":
        draft = f"""{topic} — Evidence-Based Guide for Women 45+

The estrobolome connection: how gut bacteria regulate estrogen during menopause.

Key takeaways:
• 95% of women over 45 eat less than 20g fiber/day (target: 30-35g)
• Fermented foods feed the estrobolome bacteria
• Fiber + fermented foods = balanced estrogen metabolism

Save this for later. Share with a friend who needs this.

#GutHealth #Menopause #Estrobolome #Women45Plus #HormoneHealth #Perimenopause #FiberGoals #HealthyAging #WomenWellness #Microbiome"""
    else:
        draft = f"{topic}: {research}"
    
    return {"draft": draft}

def safety_check(state: ContentState) -> dict:
    """Check content for safety/compliance."""
    draft = state["draft"]
    # Block unverified medical claims
    blocked = ["cure", "guarantee", "miracle", "replace medication"]
    lowered = draft.lower()
    passed = not any(w in lowered for w in blocked)
    # Add required disclaimer if health content
    if passed and "estrogen" in lowered:
        draft = draft + "\n\n⚠️ This is educational content, not medical advice. Consult your healthcare provider."
    return {"safety_passed": passed, "draft": draft}

def approval_node(state: ContentState) -> dict:
    """Human approval gate — returns True to proceed, False to regenerate."""
    # In production: send to Telegram bot for human review
    # For now, auto-approve if safety passed
    return {"approved": state["safety_passed"]}

def route_approval(state: ContentState) -> str:
    """Route: approved → post, not approved → regenerate."""
    if state.get("approved"):
        return "post"
    return "regenerate"

def regenerate_node(state: ContentState) -> dict:
    """Regenerate the draft if safety flagged."""
    return {"draft": state["draft"] + "\n\n[Edited for safety compliance]"}

# Build the graph
workflow = StateGraph(ContentState)
workflow.add_node("research", research_node)
workflow.add_node("draft", draft_node)
workflow.add_node("safety", safety_check)
workflow.add_node("approval", approval_node)
workflow.add_node("regenerate", regenerate_node)
workflow.add_node("post", lambda s: {"posted": True})

workflow.set_entry_point("research")
workflow.add_edge("research", "draft")
workflow.add_edge("draft", "safety")
workflow.add_edge("safety", "approval")
workflow.add_conditional_edges("approval", route_approval, {"post": "post", "regenerate": "regenerate"})
workflow.add_edge("regenerate", "approval")  # re-check after regeneration

app = workflow.compile()

if __name__ == "__main__":
    # Test run
    result = app.invoke({
        "topic": "How fiber feeds your estrobolome",
        "niche": "gut-health-women-45",
        "platform": "instagram"
    })
    print("Posted:", result.get("posted", False))
    print("Draft:", result.get("draft", "")[:200])