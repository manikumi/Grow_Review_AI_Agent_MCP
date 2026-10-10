import os
from datetime import date

from rich.console import Console

from src.ingestion.fetcher import fetch_reviews
from src.processing.clusterer import cluster_themes
from src.processing.pulse_generator import generate_pulse, render_pulse
from src.processing.scrubber import scrub
from src.utils.config import GROWW_APP_ID, REVIEW_LOOKBACK_WEEKS, REVIEW_MAX_COUNT

console = Console()

def run():
    """
    Orchestrates the full pipeline:
    fetch -> scrub -> cluster -> generate_pulse -> render_pulse -> deliver
    """
    console.print("[bold magenta]Starting Groww Review AI Agent...[/bold magenta]")
    
    # 1. Fetch
    console.print("\n[bold]Step 1: Fetching Reviews[/bold]")
    raw_reviews = fetch_reviews(GROWW_APP_ID, lookback_weeks=REVIEW_LOOKBACK_WEEKS, max_count=REVIEW_MAX_COUNT)
    if not raw_reviews:
        console.print("[red]No reviews fetched. Exiting.[/red]")
        return
        
    # 2. Scrub
    console.print("\n[bold]Step 2: Scrubbing PII[/bold]")
    clean_reviews = scrub(raw_reviews)
    console.print(f"Scrubbed {len(raw_reviews) - len(clean_reviews)} reviews completely. {len(clean_reviews)} remain.")
    if not clean_reviews:
        console.print("[red]No clean reviews left after scrubbing. Exiting.[/red]")
        return
        
    # 3. Cluster Themes
    console.print("\n[bold]Step 3: Clustering Themes (via LLM)[/bold]")
    clusters = cluster_themes(clean_reviews)
    console.print(f"Discovered {len(clusters)} themes.")
    for c in clusters:
        console.print(f" - {c.name} ({c.count} reviews)")
        
    # 4. Generate Pulse
    console.print("\n[bold]Step 4: Generating Weekly Pulse[/bold]")
    pulse = generate_pulse(clusters, clean_reviews)
    
    # 5. Render Pulse
    console.print("\n[bold]Step 5: Rendering Markdown[/bold]")
    md_output = render_pulse(pulse)
    
    # 6. Delivery via MCP
    console.print("\n[bold]Step 6: Delivery (MCP Google Docs & Gmail)[/bold]")
    try:
        from src.mcp.router import mcp_router
        from src.utils.config import PULSE_RECIPIENT_EMAIL
        
        today = date.today().isoformat()
        doc_title = f"Groww Weekly Pulse - {today}"
        
        # Call Docs MCP
        console.print("[cyan]Creating Google Doc...[/cyan]")
        doc_url = mcp_router.create_doc(title=doc_title, content=md_output)
        console.print(f"[bold green]Doc created:[/bold green] {doc_url}")
        
        # Call Gmail MCP
        if PULSE_RECIPIENT_EMAIL:
            console.print(f"[cyan]Creating Gmail draft for {PULSE_RECIPIENT_EMAIL}...[/cyan]")
            draft_id = mcp_router.create_gmail_draft(to=PULSE_RECIPIENT_EMAIL, doc_url=doc_url)
            console.print(f"[bold green]Draft created with ID:[/bold green] {draft_id}")
        else:
            console.print("[yellow]No PULSE_RECIPIENT_EMAIL configured, skipping Gmail draft.[/yellow]")
            
    except Exception as e:
        console.print(f"[bold red]Failed to deliver via MCP:[/bold red] {e}")
        # Fallback to local save
        os.makedirs("output", exist_ok=True)
        today = date.today().isoformat()
        filepath = os.path.join("output", f"pulse_{today}.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md_output)
        console.print(f"[bold green]Fallback: Pulse saved locally to: {filepath}[/bold green]")
        
    console.print("\n[bold cyan]--- Final Pulse Output ---[/bold cyan]\n")
    console.print(md_output)
    console.print(f"\n[cyan]Word count: {pulse.word_count} words[/cyan]")
    console.print("\n[bold magenta]Agent run completed successfully![/bold magenta]")

if __name__ == "__main__":
    run()
