#!/usr/bin/env python3
"""Topic-specific animated Q&A Shorts for TheTechnoz Solutions.

Each supported episode has independently authored scene text and diagram labels.
No recycled slideshow; unreviewed topics fail closed rather than use a fallback.
"""
from datetime import date, timedelta

# Fields: question, scene 1 label/subtitle, scene 2, scene 3,
# takeaway, closing audience question, and visual metaphor for each scene.
SPECS = [
 ("Why can a RAG answer still be wrong?",
  ("RETRIEVE", "Find passages related to the question.", "retrieval"),
  ("EXAMINE", "Check whether those passages support the claim.", "evidence"),
  ("GENERATE", "Give the model the evidence and source IDs.", "generation"),
  "Retrieval helps, but it never guarantees correctness.",
  "Would you trust an answer without checking its sources?"),
 ("Why can higher PPC spend fail to grow unit sales?",
  ("TRAFFIC", "More spend can buy more clicks.", "traffic"),
  ("CONVERSION", "Clicks matter only if shoppers buy.", "conversion"),
  ("DIAGNOSE", "Compare units per click and search intent.", "diagnose"),
  "Optimize unit sales, not spend alone.",
  "Would you raise bids before checking conversion?"),
 ("What stops an AI agent from looping forever?",
  ("TOOLS", "An agent can repeatedly call external tools.", "agent"),
  ("BOUNDARIES", "Set time, cost and step limits.", "limits"),
  ("ESCALATION", "Stop safely when a check fails.", "stop"),
  "Every autonomous agent needs a stopping rule.",
  "Does your agent know when to ask a human?"),
 ("Does low TACOS always mean better profit?",
  ("MEASURE", "TACOS compares ad spend with total sales.", "tacos"),
  ("COSTS", "Fees, margin and returns change profitability.", "margin"),
  ("DECIDE", "Compare contribution and units as well.", "profit"),
  "Low TACOS does not prove high profit.",
  "Are you tracking margin alongside TACOS?"),
 ("Why might vector search miss an exact answer?",
  ("SEMANTIC", "Embeddings prioritize meaning, not exact strings.", "vectors"),
  ("LEXICAL", "Exact codes and terms may need keyword search.", "lexical"),
  ("HYBRID", "Combine retrieval signals, then rerank.", "hybrid"),
  "Use retrieval that matches your question type.",
  "Could an exact product code get missed?"),
 ("What is more useful than a PPC target keyword?",
  ("TARGET", "The target defines an advertising rule.", "target"),
  ("SEARCH TERM", "The search term shows what shoppers entered.", "query"),
  ("ACTION", "Analyze intent before changing bids or negatives.", "diagnose"),
  "Optimize the traffic that actually arrived.",
  "Are your real search terms matching intent?"),
 ("Why can a RAG evaluation look good but fail?",
  ("RETRIEVAL", "Test whether relevant passages were found.", "retrieval"),
  ("FAITHFULNESS", "Check whether the answer follows the evidence.", "evidence"),
  ("TASK SUCCESS", "Measure whether the user got a useful answer.", "eval"),
  "Test retrieval and generation separately.",
  "Which failure would one score hide?"),
 ("Can an Amazon PPC budget cap hide demand?",
  ("BUDGET", "A campaign can exhaust its daily budget early.", "budget"),
  ("DELIVERY", "Later high-intent searches may be missed.", "timeline"),
  ("PROFIT", "Check incremental returns before raising limits.", "profit"),
  "Budget changes should follow demand evidence.",
  "Do you know when your ads stop showing?"),
 ("Is a system prompt enough to secure an agent?",
  ("PROMPT", "Instructions alone cannot enforce permissions.", "agent"),
  ("VALIDATE", "Check outputs and restrict tool access.", "limits"),
  ("TEST", "Test adversarial cases and escalation paths.", "stop"),
  "Guardrails must be tested like software.",
  "What happens when a guardrail fails?"),
 ("Can product images change advertising results?",
  ("CLICK", "Your ad brings shoppers to a product page.", "traffic"),
  ("LISTING", "Images must explain the product clearly.", "listing"),
  ("CONVERSION", "Compare unit conversion after the change.", "conversion"),
  "A listing bottleneck cannot be fixed by bids alone.",
  "Would you improve the page before spending more?"),
 ("When should you build an agent instead of a workflow?",
  ("WORKFLOW", "Fixed steps are easier to test and audit.", "workflow"),
  ("AGENT", "Agents adapt when decisions vary.", "agent"),
  ("CONTROL", "Limit what autonomy can change.", "limits"),
  "Choose autonomy only when it solves a real need.",
  "Is your process truly unpredictable?"),
 ("Can higher PPC bids guarantee organic ranking?",
  ("VISIBILITY", "Advertising can increase paid visibility.", "traffic"),
  ("RELEVANCE", "The listing must meet shopper intent.", "listing"),
  ("CONVERSION", "Measure what shoppers do after clicking.", "conversion"),
  "Ranking requires more than raising bids.",
  "Is your traffic converting well?"),
 ("Does a larger context window equal memory?",
  ("CONTEXT", "A prompt holds limited working information.", "memory"),
  ("STORAGE", "Long-term facts need separate maintained storage.", "storage"),
  ("RETRIEVAL", "Fetch only what the current task needs.", "retrieval"),
  "Memory requires deliberate system design.",
  "What should an agent remember between sessions?"),
 ("Should you scale PPC when stock is running low?",
  ("DEMAND", "Ads can accelerate sales faster than planned.", "traffic"),
  ("STOCK", "Compare demand against available inventory.", "inventory"),
  ("PACE", "Adjust ads around replenishment lead times.", "timeline"),
  "Ad strategy must follow inventory reality.",
  "Do your ads know your stock position?"),
]

def episode(day):
    from youtube_editorial import scheduled_topic
    doc=scheduled_topic(day)
    if doc is None: return None
    idx=(day-date(2026,11,27)).days
    if not 0 <= idx < len(SPECS):
        raise RuntimeError("No bespoke animated lesson prepared for this topic")
    question,one,two,three,takeaway,closing=SPECS[idx]
    return {**doc,"question":question,"scenes":(one,two,three),
            "spoken_takeaway":takeaway,"closing_question":closing}
