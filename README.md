# LinkedIn Content Automation

**AI-assisted thought leadership planning for marketing leaders.** A portfolio-ready example of a practical content operations workflow: consistent cadence, varied topics, paste-safe formatting, quality checks, and human review.

> **Demo scope:** This repository **generates and validates drafts**. It does **not** publish to LinkedIn, generate finished images, or connect to Metricool. Those are optional future integrations. The sample topic history is synthetic/project-level example data, not evidence of publication.

## Workflow

```text
GitHub Actions (Monday) / manual run
            |
       Read topic history
            |
       OpenAI generates 2 drafts
            |
  Normalize LinkedIn spacing
            |
  Check duplicates and content QA
            |
    Save JSON + artifact
            |
       Human reviews drafts
            |
 Optional design + scheduler integration
```

## Features

- **Two posts per week**, Tuesday and Thursday at **11:00 AM Pacific**, with no third post.
- **Topic rotation** across affiliate marketing, growth, AI, leadership, retention, attribution, creators, and business impact.
- **Deduplication** against a configurable content history and against posts in the same batch (exact normalized title matches).
- **LinkedIn-ready copy** using the invisible Unicode Braille blank (U+2800) between paragraphs, selective Unicode emphasis, tight bullets, and 3–5 hashtags.
- **QA gates** for basic length, spacing, Markdown artifacts, hashtags, duplicate titles, generic AI phrases, and missing graphic concepts.
- **Graphic concepts** paired with captions (not image generation).
- **GitHub Actions artifact** with a structured JSON plan. Failed QA causes the run to fail instead of silently accepting bad copy.

## Quick start

Requires Python 3.12+ and an OpenAI API key.

```bash
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

Set `OPENAI_API_KEY` in your environment (or use a local `.env` file with a loader of your choice; this example does not automatically load `.env`).

```bash
export OPENAI_API_KEY="your_api_key"
python src/linkedin_automation.py
python -m unittest discover -s tests -v
```

Generated drafts: `data/latest_plan.json` (ignored from the repository by default if you add it to `.gitignore`; the GitHub workflow stores it as a downloadable artifact).

## GitHub Actions setup

1. Open **Settings → Secrets and variables → Actions**.
2. Create a repository secret named `OPENAI_API_KEY`.
3. Open **Actions → Weekly LinkedIn Drafts → Run workflow**, or wait for the Monday scheduled run.
4. Download the `linkedin-weekly-plan` artifact and review the captions and concepts.

The GitHub Actions cron uses UTC; `0 16 * * 1` runs Mondays at 16:00 UTC. That is **9:00 AM PDT or 8:00 AM PST**, depending on daylight saving time. Post dates and timezone are calculated using `America/Los_Angeles`.

## Example output

```json
{
  "week": "2026-11-02",
  "posts": [
    {
      "day": "Tuesday",
      "date": "2026-11-03",
      "time": "11:00",
      "pillar": "measurement and attribution",
      "topic": "Where attribution models leave gaps",
      "caption": "Draft text...",
      "graphic_concept": "A simple visual contrasting measured and unmeasured influence",
      "qa_notes": "Proofread for clarity and unsupported claims"
    }
  ],
  "qa": {
    "passed": true,
    "issues": [],
    "human_review_required": true
  }
}
```

Actual runs require **exactly two posts**; the abbreviated example above shows the shape of one entry.

## Files

| Path | Purpose |
|---|---|
| `src/linkedin_automation.py` | Generate, normalize, and validate posts |
| `data/content_history.json` | Recent topic examples used to avoid repetition |
| `tests/test_formatting.py` | Basic tests for spacing and duplicate detection |
| `.github/workflows/weekly-linkedin.yml` | Scheduled draft generation and artifact upload |
| `.env.example` | Environment variable names |
| `requirements.txt` | Python dependency |

## Limitations and next steps

The QA layer is a **first-pass automated check**, not a guarantee of factual accuracy or polished writing. A person must verify all personal claims, numbers, company references, grammar, graphic wording, and accessibility. The deduplication check catches exact normalized topic titles; semantic duplication still needs editorial review. The sample history is static unless you update it.

To extend this into a production workflow, add:

1. A reviewer approval step before publishing.
2. Image generation or a Canva design pipeline with visual QA.
3. An authenticated scheduler integration (e.g., Metricool), including API permissions, idempotency keys, and duplicate checks against already scheduled posts.
4. A durable content history updated **only after confirmed publication**.
5. Delivery/error monitoring, retry handling, and audit logs.

**Never commit API keys, tokens, or private account data.**

## Portfolio takeaway

Demonstrates how marketing strategy, AI prompting, quality controls, content governance, and workflow automation can work together to build a sustainable thought-leadership engine—without optimizing for posting volume alone.

---
Built as an illustrative marketing automation project.
