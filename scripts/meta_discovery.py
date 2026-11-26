#!/usr/bin/env python3
"""Topic-specific Meta discoverability without hashtag stuffing or fake tagging.

Instagram captions may contain @mentions of verified, relevant accounts.
A Facebook caption with @username text is NOT equivalent to tagging a Page,
so do not manufacture mentions or imply official endorsement.
"""
import re

BRAND="#TheTechnozSolutions"
AI_TAGS=("#ArtificialIntelligence","#LLM","#AIAgents","#MachineLearning","#RAG","#GenerativeAI","#AIAutomation","#AIResearch")
AMAZON_TAGS=("#AmazonPPC","#AmazonPrivateLabel","#Ecommerce","#AmazonSEO","#AmazonAdvertising","#ConversionRate","#AmazonSeller","#RetailMedia")
TOPIC_SIGNALS={
    "rag": "#RAG", "retriev": "#RAG", "language model": "#LLM",
    "agent": "#AIAgents", "workflow": "#AIAutomation", "guardrail": "#AIResearch",
    "ranking": "#AmazonSEO", "keyword": "#AmazonSEO", "search term": "#AmazonPPC",
    "inventory": "#AmazonSeller", "stockout": "#AmazonSeller", "listing": "#AmazonPrivateLabel",
    "profit": "#ConversionRate", "margin": "#ConversionRate", "tacos": "#AmazonPPC",
    "ppc": "#AmazonPPC", "advertis": "#AmazonAdvertising", "conversion": "#ConversionRate",
}
def category_of(topic,body=""):
    label=(topic or "").casefold()
    if "amazon" in label or label=="ecommerce": return "amazon"
    if label in ("ai","llm","artificial intelligence"): return "ai"
    combined=(label+" "+(body or "")).casefold()
    return "amazon" if any(k in combined for k in ("amazon","ppc","product listing","tacos","seller central")) else "ai"

def tags_for(topic,headline,body=""):
    family=category_of(topic,headline+" "+body)
    pool=AMAZON_TAGS if family=="amazon" else AI_TAGS
    combined=(headline+" "+body).casefold()
    topical=[tag for signal,tag in TOPIC_SIGNALS.items() if signal in combined and tag in pool]
    ordered=[BRAND]+topical+list(pool)
    unique=[]
    for x in ordered:
        if x not in unique:unique.append(x)
    return unique[:5]

def strip_old_tags(caption):
    # Only remove standalone hashtag lines, preserving the original prose.
    lines=caption.splitlines()
    while lines and not lines[-1].strip():lines.pop()
    while lines and re.fullmatch(r"(?:\s*#[A-Za-z0-9_]+)+\s*",lines[-1]):
        lines.pop()
    return "\n".join(lines).rstrip()

def decorate(caption,topic):
    cleaned=strip_old_tags(caption)
    headline=cleaned.splitlines()[0] if cleaned else ""
    tags=tags_for(topic,headline,cleaned)
    return cleaned+"\n\n"+" ".join(tags)

def instagram_caption(caption,topic):
    cleaned=strip_old_tags(caption)
    lowered=cleaned.casefold()
    # Contextual, verified examples only. These are CAPTION mentions,
    # not media/user tags, invitations to collaborate, or endorsements.
    mention=None
    if category_of(topic,cleaned)=="ai" and re.search(r"\b(openai|chatgpt|gpt-[0-9]|sora)\b",lowered):
        mention="@openai"
    elif category_of(topic,cleaned)=="amazon" and re.search(r"\b(amazon ads|amazon advertising|seller central)\b",lowered):
        mention="@amazon"
    if mention and mention.casefold() not in lowered:
        cleaned+="\n\nRelevant platform: "+mention
    return decorate(cleaned,topic)
