# src/utils/prompts.py

CLUSTERING_PROMPT = """
You are a product analyst categorising app reviews.
You are given a list of app reviews. Each review has an ID and a text.
Group them into at most 5 themes.

Rules:
1. Try to use broad categories like "Payments", "UI/UX", "Customer Support", "Performance", "Account Verification".
2. You MUST return a strictly valid JSON response in the following schema:
{{
  "clusters": [
    {{
      "name": "Theme Name",
      "review_ids": ["id1", "id2"],
      "summary": "1-2 sentence summary of this theme."
    }}
  ]
}}
3. ONLY output JSON, without any markdown blocks or explanations.
4. Ensure no more than 5 themes are created.
5. All reviews must belong to at least one theme, if possible. A review can belong to multiple themes but try to pick the most relevant one.

Reviews:
{reviews_json}
"""

ACTION_IDEAS_PROMPT = """
You are a senior product manager reviewing the top user themes for the week.
Here are the top themes and their summaries:

{themes_text}

Generate exactly 3 actionable product or engineering ideas based on these themes to improve the app.
Keep each idea concise (under 2 sentences) and highly relevant.

Rules:
1. Provide ONLY a strictly valid JSON object in the following schema:
{{
  "action_ideas": [
    "Action Idea 1",
    "Action Idea 2",
    "Action Idea 3"
  ]
}}
2. DO NOT wrap the output in markdown. ONLY valid JSON.
"""

