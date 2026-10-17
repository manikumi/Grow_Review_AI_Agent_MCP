import json

from groq import APIStatusError, Groq
from pydantic import BaseModel

from src.processing.scrubber import CleanReview
from src.utils.config import GROQ_API_KEY, LLM_EXTRA_PARAMS, LLM_MODEL
from src.utils.prompts import CLUSTERING_PROMPT


class ThemeCluster(BaseModel):
    name: str                  # e.g. "Payments"
    review_ids: list[str]
    count: int = 0             # We can default this or calculate it
    summary: str               # 1-2 sentence LLM summary of the cluster

def cluster_themes(reviews: list[CleanReview]) -> list[ThemeCluster]:
    """
    Calls Groq to assign themes to reviews.
    Enforces a max of 5 themes post-parse.
    Batches reviews into chunks if count > 200 to stay within context limits.
    """
    if not reviews:
        return []

    client = Groq(api_key=GROQ_API_KEY)
    
    # We will process in chunks of 200
    chunk_size = 200
    all_clusters_dict = {}  # cluster_name -> ThemeCluster
    
    for i in range(0, len(reviews), chunk_size):
        chunk = reviews[i:i + chunk_size]
        
        # Token budget guard (estimate 1 token = 4 chars, max ~4000 tokens)
        while chunk:
            reviews_json = json.dumps([{"id": r.id, "text": r.text} for r in chunk])
            if len(reviews_json) <= 16000:
                break
            # Truncate review batch if estimated tokens exceed
            chunk = chunk[:-1]
            
        if not chunk:
            continue
            
        base_prompt = CLUSTERING_PROMPT.format(reviews_json=reviews_json)
        
        clusters_data = []
        retries = 2
        for attempt in range(retries + 1):
            prompt = base_prompt
            if attempt > 0:
                prompt += "\n\nCRITICAL: You MUST return strictly valid JSON matching the requested schema. Do not output anything else."
                
            try:
                response = client.chat.completions.create(
                    model=LLM_MODEL,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.0,
                    response_format={"type": "json_object"},
                    max_tokens=2000,
                    **LLM_EXTRA_PARAMS,
                )
            except APIStatusError as e:
                # e.g. 400 json_validate_failed when the model returns no/invalid JSON
                if attempt == retries:
                    raise
                print(f"[WARN] Groq clustering attempt {attempt + 1} failed: {e}")
                continue

            
            if hasattr(response, "usage") and response.usage:
                print(f"[Groq LLM] Clustering tokens: prompt={response.usage.prompt_tokens}, completion={response.usage.completion_tokens}, total={response.usage.total_tokens}")

            
            content = (response.choices[0].message.content or "").strip()
            
            # Strip potential markdown code blocks if the LLM misbehaves
            content = content.removeprefix("```json")
            content = content.removesuffix("```")
                
            try:
                data = json.loads(content)
                clusters_data = data.get("clusters", [])
                break # Success
            except json.JSONDecodeError:
                if attempt == retries:
                    print(f"[WARN] Failed to parse JSON from LLM after {retries} retries")
                continue
                
        if not clusters_data:
            continue
            
        # Merge into global clusters
        for c in clusters_data:
            c_name = c.get("name", "Other")
            c_summary = c.get("summary", "")
            c_ids = c.get("review_ids", [])
            
            if c_name in all_clusters_dict:
                all_clusters_dict[c_name].review_ids.extend(c_ids)
                all_clusters_dict[c_name].count += len(c_ids)
            else:
                all_clusters_dict[c_name] = ThemeCluster(
                    name=c_name,
                    review_ids=c_ids,
                    count=len(c_ids),
                    summary=c_summary
                )
                
    clusters_list = list(all_clusters_dict.values())
    
    # Enforce max 5 themes post-parse
    if len(clusters_list) > 5:
        # Sort by count descending
        clusters_list.sort(key=lambda x: x.count, reverse=True)
        top_4 = clusters_list[:4]
        overflow = clusters_list[4:]
        
        # Merge overflow into an "Other" category or just the 5th
        other_ids = []
        for o in overflow:
            other_ids.extend(o.review_ids)
            
        top_4.append(ThemeCluster(
            name="Other",
            review_ids=other_ids,
            count=len(other_ids),
            summary="Miscellaneous themes and long-tail issues."
        ))
        clusters_list = top_4
    else:
        clusters_list.sort(key=lambda x: x.count, reverse=True)
        
    return clusters_list
