"""
STEM Pathfinder v2 — STEM Career Path Explorer
NJ TSA Coding 2026

Recommendation logic:
  Raw score = (1.0 × interest tag matches) + (1.5 × strength-derived tag matches)
  Normalized to 0–100 across all careers. Ties broken by technical skill count.
  Deterministic, transparent, and explainable.
"""

import json, os
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "stempath-v2-secret-key-2026")

CAREERS_PATH = os.path.join(os.path.dirname(__file__), "data", "careers.json")

# ── Interest options shown on quiz ────────────────────────────────────────────
INTEREST_OPTIONS = [
    ("coding",          "Coding",           "fa-solid fa-code"),
    ("math",            "Math",             "fa-solid fa-calculator"),
    ("biology",         "Biology",          "fa-solid fa-microscope"),
    ("building",        "Building Things",  "fa-solid fa-hammer"),
    ("environment",     "Environment",      "fa-solid fa-leaf"),
    ("security",        "Security",         "fa-solid fa-shield-halved"),
    ("robotics",        "Robotics",         "fa-solid fa-robot"),
    ("data",            "Data",             "fa-solid fa-chart-bar"),
    ("design",          "Design",           "fa-solid fa-pen-ruler"),
    ("communication",   "Communication",    "fa-solid fa-comments"),
    ("leadership",      "Leadership",       "fa-solid fa-users"),
    ("research",        "Research",         "fa-solid fa-flask"),
    ("problem-solving", "Problem Solving",  "fa-solid fa-lightbulb"),
]

STRENGTH_OPTIONS = [
    ("analytical thinking", "Analytical Thinking", "fa-solid fa-brain"),
    ("creativity",          "Creativity",          "fa-solid fa-palette"),
    ("teamwork",            "Teamwork",            "fa-solid fa-handshake"),
    ("communication",       "Communication",       "fa-solid fa-comment-dots"),
    ("perseverance",        "Perseverance",        "fa-solid fa-fire"),
    ("attention to detail", "Attention to Detail", "fa-solid fa-magnifying-glass"),
    ("curiosity",           "Curiosity",           "fa-solid fa-star"),
    ("ethics",              "Ethics",              "fa-solid fa-scale-balanced"),
]

WORK_STYLE_OPTIONS = [
    ("analytical",      "Analytical",       "fa-solid fa-chart-pie"),
    ("creative",        "Creative",         "fa-solid fa-wand-magic-sparkles"),
    ("hands-on",        "Hands-On",         "fa-solid fa-wrench"),
    ("collaborative",   "Collaborative",    "fa-solid fa-people-group"),
    ("curious",         "Curious",          "fa-solid fa-telescope"),
    ("detail-oriented", "Detail-Oriented",  "fa-solid fa-list-check"),
    ("ethical",         "Ethical",          "fa-solid fa-heart"),
]

# Strength → interest tag mapping for scoring
STRENGTH_TAG_MAP = {
    "analytical thinking": ["math", "data", "research", "problem-solving", "coding"],
    "creativity":          ["design", "building", "robotics"],
    "teamwork":            ["communication", "leadership"],
    "communication":       ["communication", "leadership", "design"],
    "perseverance":        ["research", "security", "biology", "robotics"],
    "attention to detail": ["security", "data", "research", "biology", "coding"],
    "curiosity":           ["research", "biology", "data", "environment", "robotics"],
    "ethics":              ["security", "biology", "environment"],
}


def load_careers():
    with open(CAREERS_PATH) as f:
        return json.load(f)


def score_careers(careers, interests, strengths, work_styles):
    user_interests = set(interests)
    strength_tags = set()
    for s in strengths:
        for t in STRENGTH_TAG_MAP.get(s, []):
            strength_tags.add(t)

    user_work_styles = set(work_styles)
    scored = []
    for c in careers:
        tags = set(c.get("tags", []))
        interest_score = len(tags & user_interests) * 1.0
        strength_score = len(tags & strength_tags) * 1.5
        style_score    = len(set(c.get("work_styles", [])) & user_work_styles) * 0.5
        raw = interest_score + strength_score + style_score
        tech_count = len(c.get("skills", {}).get("technical", []))
        scored.append({"career": c, "raw": raw, "tech": tech_count})

    max_raw = max((s["raw"] for s in scored), default=1) or 1
    for s in scored:
        s["score"] = round((s["raw"] / max_raw) * 100)

    scored.sort(key=lambda x: (-x["score"], -x["tech"]))
    return scored


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def home():
    return render_template("home.html",
        interest_options=INTEREST_OPTIONS,
        strength_options=STRENGTH_OPTIONS,
        work_style_options=WORK_STYLE_OPTIONS,
        sel_interests=session.get("interests", []),
        sel_strengths=session.get("strengths", []),
        sel_styles=session.get("work_styles", []),
    )


@app.route("/recommend", methods=["POST"])
def recommend():
    interests   = request.form.getlist("interests")
    strengths   = request.form.getlist("strengths")
    work_styles = request.form.getlist("work_styles")
    grade       = request.form.get("grade", "")

    session.update({"interests": interests, "strengths": strengths,
                    "work_styles": work_styles, "grade": grade})

    careers = load_careers()
    scored  = score_careers(careers, interests, strengths, work_styles)
    all_tags = sorted({t for c in careers for t in c.get("tags", [])})

    return render_template("recommend.html",
        scored=scored, interests=interests, strengths=strengths,
        all_tags=all_tags,
        bookmarks=session.get("bookmarks", []),
        compare_list=session.get("compare_list", []),
    )


@app.route("/careers")
def careers():
    all_careers = load_careers()
    all_tags    = sorted({t for c in all_careers for t in c.get("tags", [])})
    return render_template("careers.html",
        careers=all_careers, all_tags=all_tags,
        bookmarks=session.get("bookmarks", []),
        compare_list=session.get("compare_list", []),
    )


@app.route("/career/<cid>")
def career_detail(cid):
    careers = load_careers()
    career  = next((c for c in careers if c["id"] == cid), None)
    if not career:
        flash("Career not found.", "warning")
        return redirect(url_for("careers"))

    tags = set(career.get("tags", []))
    similar = [c for c in careers
               if c["id"] != cid and len(set(c.get("tags", [])) & tags) >= 2][:4]

    return render_template("career_detail.html",
        career=career, similar=similar,
        bookmarks=session.get("bookmarks", []),
        compare_list=session.get("compare_list", []),
    )


@app.route("/bookmark/<cid>", methods=["POST"])
def bookmark(cid):
    bm = session.get("bookmarks", [])
    if cid in bm: bm.remove(cid)
    else: bm.append(cid)
    session["bookmarks"] = bm
    return redirect(request.form.get("next") or url_for("careers"))


@app.route("/compare/toggle/<cid>", methods=["POST"])
def compare_toggle(cid):
    cl = session.get("compare_list", [])
    if cid in cl:
        cl.remove(cid)
    elif len(cl) < 3:
        cl.append(cid)
    else:
        flash("You can compare up to 3 careers at once.", "info")
    session["compare_list"] = cl
    return redirect(request.form.get("next") or url_for("careers"))


@app.route("/compare")
def compare():
    careers = load_careers()
    cl = session.get("compare_list", [])
    selected = [c for c in careers if c["id"] in cl]
    return render_template("compare.html", careers=selected, compare_list=cl)


@app.route("/roadmap")
def roadmap():
    interests   = session.get("interests", [])
    strengths   = session.get("strengths", [])
    work_styles = session.get("work_styles", [])
    bookmarks   = session.get("bookmarks", [])

    careers = load_careers()
    scored  = score_careers(careers, interests, strengths, work_styles)

    bm_scored = [s for s in scored if s["career"]["id"] in bookmarks]
    primary = bm_scored[0] if bm_scored else (scored[0] if scored else None)

    return render_template("roadmap.html",
        primary=primary, scored=scored[:6],
        interests=interests, strengths=strengths,
        interest_options=INTEREST_OPTIONS,
        strength_options=STRENGTH_OPTIONS,
    )


@app.route("/about")
def about():
    return render_template("about.html")


@app.context_processor
def globals():
    bm = session.get("bookmarks", [])
    cl = session.get("compare_list", [])
    return {"bookmark_count": len(bm), "compare_count": len(cl),
            "bookmarks": bm, "compare_list": cl}


if __name__ == "__main__":
    app.run(debug=True)
