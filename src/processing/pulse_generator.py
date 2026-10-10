import json
from datetime import date

from groq import Groq
from pydantic import BaseModel

from src.processing.clusterer import ThemeCluster
from src.processing.scrubber import CleanReview
from src.utils.config import GROQ_API_KEY, LLM_MODEL
from src.utils.prompts import ACTION_IDEAS_PROMPT


class WeeklyPulse(BaseModel):
    week_ending: date
    top_themes: list[ThemeCluster]   # Top 3 by review count
    user_quotes: list[str]           # 3 verbatim quotes (PII-free)
    action_ideas: list[str]          # 3 LLM-generated action ideas
    word_count: int = 0

def generate_pulse(clusters: list[ThemeCluster], clean_reviews: list[CleanReview]) -> WeeklyPulse:
    """
    Builds the final weekly pulse from clusters.
    """
    client = Groq(api_key=GROQ_API_KEY)
    
    # Select top 3 clusters by count
    top_3_clusters = clusters[:3]
    
    # Map review ID to text for quick lookup
    review_dict = {r.id: r.text for r in clean_reviews}
    
    # Pick 1 quote per top theme
    user_quotes = []
    themes_text_lines = []
    
    for c in top_3_clusters:
        themes_text_lines.append(f"- {c.name}: {c.summary}")
        if c.review_ids:
            # Pick the first available review as a quote
            # (Could be randomized or selected by length)
            for rid in c.review_ids:
                if rid in review_dict:
                    user_quotes.append(f"[{c.name}] \"{review_dict[rid]}\"")
                    break
                    
    # Generate action ideas
    themes_text = "\n".join(themes_text_lines)
    base_prompt = ACTION_IDEAS_PROMPT.format(themes_text=themes_text)
    
    action_ideas = []
    retries = 2
    for attempt in range(retries + 1):
        prompt = base_prompt
        if attempt > 0:
            prompt += "\n\nCRITICAL: Keep your ideas EXTREMELY brief to ensure the final report is strictly under 250 words. Also, ensure you return strictly valid JSON."

        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        content = response.choices[0].message.content.strip()
        content = content.removeprefix("```json")
        content = content.removesuffix("```")
            
        try:
            parsed = json.loads(content)
            if not isinstance(parsed, list):
                parsed = ["Could not parse action ideas properly."]
            action_ideas = parsed[:3]
        except json.JSONDecodeError:
            action_ideas = ["Improve app stability.", "Enhance UI/UX.", "Investigate payment failures."]
            
        pulse = WeeklyPulse(
            week_ending=date.today(),
            top_themes=top_3_clusters,
            user_quotes=user_quotes[:3],
            action_ideas=action_ideas
        )
        
        # Quick estimate of rendered word count
        est_text = " ".join([t.summary for t in pulse.top_themes]) + " " + " ".join(pulse.user_quotes) + " " + " ".join(pulse.action_ideas)
        if len(est_text.split()) < 200: # Leaves some buffer for formatting words
            break
            
    return pulse

def render_pulse(pulse: WeeklyPulse) -> str:
    """
    Converts a WeeklyPulse to human-readable Markdown.
    Enforces <=250 words roughly (can truncate if needed).
    """
    md_lines = []
    md_lines.append(f"# Weekly Pulse — {pulse.week_ending}")
    md_lines.append("")
    
    md_lines.append("## Top Themes")
    for t in pulse.top_themes:
        md_lines.append(f"- **{t.name}** ({t.count} reviews): {t.summary}")
    md_lines.append("")
    
    md_lines.append("## Voice of the Customer")
    for q in pulse.user_quotes:
        md_lines.append(f"> {q}")
    md_lines.append("")
    
    md_lines.append("## Action Ideas")
    for i, act in enumerate(pulse.action_ideas, 1):
        md_lines.append(f"{i}. {act}")
        
    final_md = "\n".join(md_lines)
    
    # Check word count
    words = final_md.split()
    pulse.word_count = len(words)
    
    if pulse.word_count > 250:
        # Naive truncation to stay under 250 words
        truncated = words[:250]
        final_md = " ".join(truncated) + "\n... (truncated to 250 words)"
        pulse.word_count = 250
        
    return final_md
