"""AI-assisted LinkedIn content planning. Drafts only: never publishes."""
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SPACER = "\u2800"
PILLARS = [
    "affiliate and partnership marketing", "growth and performance marketing",
    "AI in marketing", "marketing leadership", "revenue and business impact",
    "creator strategy", "measurement and attribution", "lifecycle and retention",
    "cross-functional leadership", "real-world marketing lessons",
]
BANNED_PHRASES = ("in today's fast-paced", "game-changer", "unlock the power",
                  "ever-evolving landscape", "delve into", "revolutionize")

def current_monday():
    today = datetime.now(ZoneInfo("America/Los_Angeles")).date()
    return today - timedelta(days=today.weekday())

def history():
    path = DATA / "content_history.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []

def normalize_spacing(text):
    """Use Braille blank spacer on empty lines to survive LinkedIn paste."""
    result = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            result.append(line.rstrip())
        elif result and result[-1] != SPACER:
            result.append(SPACER)
    return "\n".join(result).strip("\n" + SPACER)

def validate(plan, previous):
    issues = []
    posts = plan.get("posts")
    if not isinstance(posts, list) or len(posts) != 2:
        return ["Exactly two posts are required."]
    old_topics = {x.get("topic", "").strip().casefold() for x in previous}
    seen = set()
    for idx, post in enumerate(posts):
        day = ["Tuesday", "Thursday"][idx]
        if post.get("day") != day:
            issues.append(f"Post {idx+1} must be {day}.")
        topic = post.get("topic", "").strip()
        if not topic or topic.casefold() in seen or topic.casefold() in old_topics:
            issues.append(f"Missing or repeated topic: {topic!r}")
        seen.add(topic.casefold())
        caption = post.get("caption", "")
        if len(caption) < 250 or len(caption) > 2500:
            issues.append(f"{day}: caption length outside 250-2500 characters.")
        if "**" in caption or "__" in caption or "\\n" in caption:
            issues.append(f"{day}: Markdown or literal newline escapes detected.")
        tags = re.findall(r"(?<!\w)#[A-Za-z][A-Za-z0-9_]*", caption)
        if not 3 <= len(tags) <= 5:
            issues.append(f"{day}: use 3-5 hashtags.")
        if any(phrase in caption.casefold() for phrase in BANNED_PHRASES):
            issues.append(f"{day}: generic AI phrase detected.")
        if not post.get("graphic_concept", "").strip():
            issues.append(f"{day}: missing graphic concept.")
    return issues

def generate():
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("Set OPENAI_API_KEY as a GitHub secret or environment variable.")
    prior = history()
    monday = current_monday()
    dates = [(monday + timedelta(days=n)).isoformat() for n in (1, 3)]
    recent = [x.get("topic", "") for x in prior[-24:]]
    system = (
        "You are a senior marketing thought-leadership editor. "
        "Write credible, specific, human-sounding LinkedIn posts. "
        "Never invent personal achievements, named clients, revenue figures, "
        "employment details or results. Use no Markdown. "
        "Provide a graphic concept that complements the caption rather than repeats it. "
        "Proofread spelling, punctuation, repetition, claims and awkward AI phrasing. "
        "Return one valid JSON object only."
    )
    request = {
        "task": "Draft exactly two posts for Tuesday and Thursday, 11:00 America/Los_Angeles.",
        "week_start": monday.isoformat(), "dates": dates,
        "pillars": PILLARS, "avoid_recent_topics": recent,
        "voice": "Senior marketing leader, practical, strategic, specific, no hype.",
        "format": {
            "week": monday.isoformat(),
            "posts": [{
                "day": "Tuesday or Thursday", "date": "YYYY-MM-DD",
                "time": "11:00", "pillar": "content pillar",
                "topic": "specific original angle",
                "caption": "250-2500 characters, 3-5 hashtags, short paragraphs",
                "graphic_concept": "visual direction and short graphic headline",
                "qa_notes": "what was checked"
            }]
        },
        "caption_rules": [
            "Short readable paragraphs and tight bullet lists",
            "Use a literal blank line between sections; local code converts it to Unicode spacer",
            "Selective Unicode bold/italic only for short emphasis, not entire paragraphs",
            "Do not claim experiences not in the supplied context"
        ]
    }
    client = OpenAI()
    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        input=[{"role": "system", "content": system},
               {"role": "user", "content": json.dumps(request, ensure_ascii=False)}],
        text={"format": {"type": "json_object"}},
    )
    plan = json.loads(response.output_text)
    for i, post in enumerate(plan.get("posts", [])):
        post["caption"] = normalize_spacing(post.get("caption", ""))
        post["date"] = dates[i] if i < 2 else post.get("date")
        post["time"] = "11:00"
    plan["week"] = monday.isoformat()
    issues = validate(plan, prior)
    plan["qa"] = {"passed": not issues, "issues": issues, "human_review_required": True}
    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / "latest_plan.json").write_text(
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if issues:
        raise RuntimeError("QA failed: " + "; ".join(issues))
    print("Created two reviewed drafts at data/latest_plan.json. No posts published.")

if __name__ == "__main__":
    generate()
