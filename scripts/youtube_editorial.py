#!/usr/bin/env python3
"""Curated editorial schedule: unique substantive educational YouTube pieces.
14 Shorts and two initial long tutorials; no repeating published materials.
Add editorially reviewed episodes before the catalog is exhausted.
"""
from datetime import date, timedelta

SHORTS = [
 ("AI","RAG Is Not a Knowledge Database","Retrieval augmented generation","A retrieval system should find relevant evidence before the language model writes. Better prompting alone will not repair poor retrieval. Evaluate your chunk boundaries, metadata filters, and whether citations actually support the answer.","Check what the retriever found before judging the answer."),
 ("Amazon","The PPC Metric Behind High Spend","Ad cost versus unit velocity","If advertising spend rises but units stay flat, inspect search terms and unit conversion before raising bids. A healthy click through rate can still hide poorly matched shopper intent.","Compare units per click, not just orders."),
 ("AI","Agents Need Stop Conditions","Reliable AI agent design","AI agents can repeatedly call tools, but that does not make their decisions correct. Give each workflow a budget, maximum steps, validation rules, and a human escalation path for exceptions.","Every autonomous workflow needs an exit rule."),
 ("Amazon","TACOS Is Not the Whole Story","Measure contribution margin","TACOS relates ad spend to total sales, but profitable growth also depends on product margin, fees, returns and inventory. A low TACOS is not proof that a campaign strategy is working.","Evaluate profit and units alongside TACOS."),
 ("AI","Vector Search Can Miss the Answer","Hybrid retrieval","Semantic similarity is useful, but exact identifiers, numbers, and uncommon product names can be lost. Hybrid retrieval combines lexical and semantic signals, then reranks evidence before generation.","Test both keyword and semantic search."),
 ("Amazon","Search Terms Beat Target Keywords","Amazon advertising diagnosis","A targeting keyword describes your advertising rule. The actual customer search term describes the traffic that arrived. Review customer search terms at sufficient volume before choosing negatives or higher bids.","Optimize what shoppers actually typed."),
 ("AI","Why RAG Evaluations Fail","Groundedness vs usefulness","An answer may sound fluent yet fail to cite relevant evidence. Assess retrieval recall, answer faithfulness, and task success separately. A single satisfaction score can conceal the failure mode.","Measure retrieval and generation separately."),
 ("Amazon","Budget Caps Can Hide Demand","Campaign delivery","When a campaign reaches its budget limit early, performance averages can hide missed impressions later in the day. Check spending patterns, high-intent periods, and incremental profitability before adding budget.","Find when delivery stops, not only total spend."),
 ("AI","Guardrails Need Tests","LLM system safety","A system prompt is not a guarantee. Test structured output validation, tool permissions, adversarial inputs, and human review for irreversible actions. Log failures so the controls improve over time.","Treat guardrails as engineering, not a slogan."),
 ("Amazon","Product Images Affect PPC","Listing conversion","Paid traffic arrives at a product detail page. If the main image, offer, and benefits are unclear, more clicks may simply cost more. Improve listing clarity and then compare conversion at similar traffic quality.","Conversion can be the bottleneck, not bids."),
 ("AI","Agents Versus Workflows","Choose the right architecture","A deterministic workflow is often easier to audit than a free-form AI agent. Use agents when decisions truly require adaptation; use ordinary software for predictable steps like fetching and validating a report.","Autonomy should solve a real problem."),
 ("Amazon","Ranking Needs Relevant Demand","SEO and PPC together","Advertising may increase visibility, but the listing still needs to match customer intent and convert. Review search relevance, category expectations, pricing, and post-click behavior rather than treating bids as a ranking shortcut.","Relevance and conversion should guide scaling."),
 ("AI","LLM Context Is Not Memory","State management","A larger context window does not automatically create long-term memory. Store structured decisions, source references, and user-approved facts separately. Retrieve only what is necessary for the current task.","Good memory is designed, not assumed."),
 ("Amazon","Stockouts Change Ad Strategy","Inventory aware PPC","A campaign can perform well until inventory becomes constrained. Adjust pacing to available stock, fulfillment lead times and expected replenishment while protecting valuable search placements where justified.","Coordinate ads with the inventory plan.")
]

TUTORIALS = [
 ("Amazon","Diagnosing Rising Amazon PPC Spend Without More Unit Sales",[
  ("The question","We are going to investigate a common Amazon advertising problem: spend increased, clicks increased, but the number of units sold did not improve proportionately. The objective is not to blame the bidding strategy immediately. We want a repeatable diagnostic process that uses campaign evidence and avoids making decisions based on one headline metric."),
  ("Build a comparable baseline","Choose a meaningful baseline period and the period you want to investigate. Compare the same products where possible, and account for promotions, stock availability, seasonality, price changes and shipping promises. Use total units rather than only orders when units per order could change. If your data spans very different campaign configurations, disclose that limitation before attributing a result to a specific action."),
  ("Separate traffic and conversion","Start by calculating advertising spend, impressions, clicks, cost per click, orders, units and unit conversion rate for both periods. Unit conversion rate means ad attributed units divided by clicks. If clicks increased while unit conversion fell, that is fundamentally different from an unchanged conversion rate with higher click costs. Either pattern requires a different intervention. Use the same attribution definitions in both periods."),
  ("Inspect customer search terms","Next, investigate actual search terms and their match types. Compare the share of spending going to proven high intent search terms against the share going to exploratory or irrelevant traffic. A keyword may appear relevant in a campaign but attract a range of searches that convert differently. Do not immediately add negatives after a handful of clicks. Look for consistent poor performance with enough data to support a decision."),
  ("Check placements","Now compare top of search, rest of search and product page placements. Ask whether placement allocation changed, whether cost per click changed within each placement and whether conversion differences are large enough to matter. If placement mix did not meaningfully change, it is weak evidence to claim placements are the cause of the decline. We should make that distinction explicit in our report."),
  ("Review the product offer","Advertising is only part of the customer journey. Compare the main image, price, coupon, reviews, rating distribution, delivery promise, variations and competitor offers. An increase in sessions can coincide with weaker conversion because of changes in the offer, not necessarily because the traffic is poor. Use product detail page evidence before recommending more spending."),
  ("Calculate profitable room","Evaluate contribution margins and unit economics. Advertising cost of sales and total advertising cost of sales are helpful indicators, but neither replaces profitability. Consider selling fees, cost of goods, returns and promotions where available. A campaign generating more units can still be unattractive if incremental profit turns negative."),
  ("Plan controlled changes","Write down the diagnosis, its evidence and the proposed test. Limit simultaneous changes so the result remains interpretable. You might improve listing clarity, narrow poor search terms or adjust selected bids, but avoid changing every variable at once. Monitor results against comparable days and watch both conversion and unit velocity."),
  ("Conclude","The key lesson is that higher spend with flat units is a symptom, not a diagnosis. The investigation should move from comparable baselines to search intent, placements, offers and margin, then into a measurable action plan. That is a much stronger process than simply increasing or reducing campaign bids.")
 ]),
 ("AI","Building a Reliable Retrieval Augmented Generation Workflow",[
  ("The objective","Today we will build a conceptual design for a retrieval augmented generation workflow that answers questions using a controlled set of documents. The goal is grounded answers with traceable evidence, not merely fluent language. We will cover ingestion, indexing, retrieval, generation, evaluation and operational safeguards."),
  ("Define the use case","Begin by specifying the type of questions the system must answer, the documents it may use and the conditions under which it should decline. Some use cases require exact contract clauses or product identifiers, while others require broad semantic synthesis. Those requirements will influence retrieval architecture and evaluation criteria."),
  ("Prepare the documents","Extract text with its source identifier, document version, date and relevant section metadata. Preserve headings and relationships between tables and surrounding paragraphs. Do not blindly treat every fixed length chunk as an independent fact. A small amount of thoughtful structure can make retrieval more precise and easier to audit."),
  ("Index for multiple search patterns","An embedding index finds semantically similar passages. Lexical search can be better for exact terms, product codes and uncommon acronyms. A hybrid approach combines both and may use a reranker to select the passages most likely to answer the question. The point is not to add complexity by default. The point is to match the search strategy to real user questions."),
  ("Construct the prompt","Pass the retrieved passages with source markers into the language model. Explicitly distinguish the user's request from the retrieved data, because a retrieved document may contain irrelevant instructions. Tell the model to cite supporting excerpts and acknowledge when evidence is insufficient. Do not let the model invent citations for material it has not received."),
  ("Test the retriever separately","Create a dataset of realistic questions with known relevant documents or passages. Measure whether the retriever finds the right evidence before grading the final answer. If retrieval recall is poor, changing the generation prompt alone may not solve the actual problem. Include hard cases such as conflicting documents, stale versions and near duplicate passages."),
  ("Evaluate answer quality","Score factual faithfulness to the retrieved evidence, answer relevance to the user request, citation correctness and helpfulness. These dimensions are not identical. A concise answer can be faithful but incomplete; a detailed answer can be useful sounding but unsupported. Combine automatic tests with a small human evaluation panel for important tasks."),
  ("Add security boundaries","Enforce document permissions before retrieval, not only after generation. Limit what tools can do, avoid exposing secrets in logs and protect against prompt injection embedded in retrieved content. Where the system can trigger business actions, use confirmation gates and clear recovery procedures. A useful assistant is not necessarily authorized to make every decision."),
  ("Monitor and iterate","Track retrieval misses, user corrections, latency and recurring failure categories. Version the index, prompts and evaluation datasets so changes can be compared meaningfully. Refresh stale documents and make it possible to trace which version supported a specific answer."),
  ("Conclusion","A reliable RAG workflow is an evidence processing system. It succeeds when its knowledge sources are well managed, retrieval is tested, answers are grounded and permissions are respected. The model matters, but system design and evaluation determine whether the application is trustworthy.")
 ])
]

def scheduled_topic(day):
    # Start Friday 27 November 2026, 14 Shorts through 10 December.
    start=date(2026,11,27)
    index=(day-start).days
    if index < 0:
        return None
    if index >= len(SHORTS):
        return None
    kind,title,angle,body,takeaway=SHORTS[index]
    return {"id":f"short-{day.isoformat()}","kind":"short","category":kind,
            "title":title,"angle":angle,"narration":body,"takeaway":takeaway}

def scheduled_tutorial(day):
    # Saturday each week, 28 Nov and 5 Dec.
    if day.weekday()!=5:return None
    first=date(2026,11,28)
    index=(day-first).days//7
    if day<first or index>=len(TUTORIALS):return None
    kind,title,chapters=TUTORIALS[index]
    return {"id":f"tutorial-{day.isoformat()}","kind":"tutorial",
            "category":kind,"title":title,"chapters":chapters}
