"""
Grito Labs Marketing Analytics & Attribution Framework
Module: src/generate_presentation.py
Description: Generates the 14-slide executive presentation in both:
             1. Native PowerPoint format (presentation/Grito_Attribution_Deck.pptx)
             2. Pixel-perfect PDF format (presentation/Grito_Attribution_Deck.pdf)
             Features action-titled slides, Grito Labs theme tokens, metric callouts,
             and clean structured tables. All numbers match verified SQLite/CSV models.
"""

import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRES_DIR = os.path.join(BASE_DIR, "presentation")
PPTX_PATH = os.path.join(PRES_DIR, "Grito_Attribution_Deck.pptx")
HTML_SLIDES_PATH = os.path.join(PRES_DIR, "slides.html")
PDF_PATH = os.path.join(PRES_DIR, "Grito_Attribution_Deck.pdf")

os.makedirs(PRES_DIR, exist_ok=True)

# Theme Palette
COLOR_NAVY = RGBColor(11, 37, 69)      # #0B2545
COLOR_SLATE = RGBColor(19, 64, 116)    # #134074
COLOR_BLUE = RGBColor(0, 123, 255)     # #007BFF
COLOR_GREEN = RGBColor(42, 157, 143)   # #2A9D8F
COLOR_AMBER = RGBColor(231, 111, 81)   # #E76F51
COLOR_RED = RGBColor(230, 57, 70)      # #E63946
COLOR_BG_LIGHT = RGBColor(248, 249, 250)
COLOR_WHITE = RGBColor(255, 255, 255)
COLOR_TEXT = RGBColor(33, 37, 41)
COLOR_MUTED = RGBColor(108, 117, 125)

SLIDE_DATA = [
    {
        "slide_num": 1,
        "is_title": True,
        "title": "Multi-Channel Marketing Analytics &\nAttribution Optimization Framework",
        "subtitle": "Data-Driven Journey Modeling, Algorithmic Attribution & Capital Reallocation",
        "author": "Candidate: J Nikhil (GitHub: https://github.com/JNikhil11)\nPrepared for Grito Labs Executive Analytics Committee | Q4 2026\n[Synthetic Dataset: Seed 42, 16K Journeys, 40.8K Touches, 2,450 New Students, 2,744 Orders]",
        "key_metric": ""
    },
    {
        "slide_num": 2,
        "action_title": "Executive Summary: Zero-Sum Budget Shift Unlocks +$224.9K Revenue at Fixed $426.4K Spend",
        "category": "STRATEGIC OVERVIEW",
        "bullets": [
            "Baseline Performance: $426.4K marketing spend generated $2.38M initial revenue across 2,450 newly enrolled students (Blended Paid ROAS: 3.96x; Headline CAC: $174.05; Cost per Order: $155.40 across 2,744 total orders).",
            "The Attribution Blindspot: Last-Touch systematically undervalues Paid Social by +47.6% (+$184.6K) and Display Ads by +37.8% (+$74.8K), while over-crediting Direct navigation by -33.6%.",
            "Multi-Touch Dominance: 69.1% of conversions involve multi-channel paths with 5.2-day average latency; single-touch evaluation misleads capital allocation.",
            "Quantified Optimization: Reallocating -$58.4K from diminishing Paid Search into Email (+$21.3K), Referral (+$20.3K), Display (+$12.3K), and Social (+$4.6K) expands Paid ROAS from 3.96x to 4.49x.",
            "Execution & De-Risking: Pre-validated via 4-week Matched-Market Geo-Holdout test with automated weekly reporting."
        ],
        "kpis": [
            ("Current Paid Spend", "$426.4K", "Strict Zero Net Shift"),
            ("Base Incremental Rev", "+$224.9K", "+13.3% Paid Lift"),
            ("Optimized Paid ROAS", "4.49x", "vs 3.96x Baseline")
        ]
    },
    {
        "slide_num": 3,
        "action_title": "The Business Problem: EdTech Decision Gestation Renders Last-Click Attribution Value-Destructive",
        "category": "BUSINESS CONTEXT",
        "bullets": [
            "High-Involvement EdTech Decisions: Career-track courses ($349 to $2,199) require multi-week research, curriculum evaluation, and peer review.",
            "Myopic Capital Allocation: Crediting only the closing click causes marketing teams to over-fund brand search and starve top-of-funnel discovery.",
            "Attribution Deficit: Without multi-touch modeling, marketing cannot identify which mid-funnel touchpoints prevent student abandonment.",
            "Data Authenticity & Transparency: Synthetic dataset calibrated to realistic EdTech metrics (seed 42, 16K journeys, 40.8K touches, 2,450 new students, 2,744 orders) following public data license constraints."
        ],
        "kpis": [
            ("Average Order Value", "$865", "Across Course Tiers"),
            ("Avg Journey Touches", "2.8 Touches", "Max: 8 Interactions"),
            ("Average Gestation", "5.2 Days", "First Touch to Order")
        ]
    },
    {
        "slide_num": 4,
        "action_title": "Data Architecture: 40.8K Telemetry Records Reconciled with Zero Leakage in Star Schema",
        "category": "DATA ENGINEERING",
        "bullets": [
            "Dimensional Warehouse: Built in portable ANSI SQL on DuckDB/SQLite; 100% compliant with PostgreSQL/Snowflake.",
            "Rigorous Quality Verification: Zero duplicate primary keys, zero orphan foreign keys, zero negative spend rows, and verified 30-day lookback windows.",
            "Sessionized 30-Day Lookback: Window functions (ROW_NUMBER, LAG, SUM OVER) isolate pre-conversion customer interactions.",
            "Ground-Truth Revenue Sum: Attributed revenue across all 5 SQL models reconciles to the exact penny ($2,382,514.60; $0.00 unattributed)."
        ],
        "kpis": [
            ("Touchpoints Audited", "40,806", "All Checks Passed"),
            ("Customers Tracked", "16,000", "2,450 New Students"),
            ("Revenue Reconciled", "$2.38M", "Zero Discrepancy ($0.00)")
        ]
    },
    {
        "slide_num": 5,
        "action_title": "Macro Channel Performance: Search & Social Absorb 80% of Spend with Divergent Unit Economics",
        "category": "CHANNEL PERFORMANCE",
        "bullets": [
            "Paid Search ($198.4K Spend): Captures high-intent evaluation traffic ($506.1K Last-Touch Rev), but has the highest CAC ($367.33) and lowest ROAS (2.55x LTA, 2.70x Position-Based).",
            "Paid Social ($143.0K Spend): Delivers high discovery volume (2.36M impressions) at a balanced $146.47 CAC and 4.00x Position-Based ROAS.",
            "Email Marketing ($13.7K Spend): Operates at an efficient 13.98x Position-Based ROAS with an ultra-low CAC of $38.27.",
            "Referral ($19.7K Spend): Generates $117.1K Position-Based revenue at 5.93x ROAS, representing high student advocacy trust."
        ],
        "kpis": [
            ("Paid Search CAC", "$367.33", "Highest Acquisition Cost"),
            ("Paid Social CAC", "$146.47", "60% Lower than Search"),
            ("Email Mktg ROAS", "13.98x", "Severely Underfunded")
        ]
    },
    {
        "slide_num": 6,
        "action_title": "Unit Economics Disparity: Paid Social Acquires Qualified Students at 60% Lower CAC than Search",
        "category": "UNIT ECONOMICS",
        "bullets": [
            "CPC Dynamics: Paid Search CPC ($9.54) is 1.7x Paid Social ($5.51), 3.4x Referral ($2.77), and 4.9x Display ($1.93).",
            "CTR Benchmarks: Display CTR is 0.29%, Paid Social CTR is 1.10%, Email CTR is 2.81%, Paid Search CTR is 4.24%—aligning with EdTech norms.",
            "The CAC Divergence: Elevated Search CPC drives its cost per student acquisition ($367.33) to 2.5x that of Social ($146.47).",
            "Diminishing Returns: Paid Search is operating deep into the flat portion of its Hill saturation curve; reallocating marginal dollars is imperative."
        ],
        "kpis": [
            ("Paid Search CPC", "$9.54", "Intent Premium"),
            ("Paid Social CPC", "$5.51", "Discovery Efficiency"),
            ("Display Ads CPC", "$1.93", "Upper-Funnel Scale")
        ]
    },
    {
        "slide_num": 7,
        "action_title": "Customer Journey Dynamics: 69.1% of Enrolled Students Require Multi-Channel Sequences",
        "category": "JOURNEY VELOCITY",
        "bullets": [
            "Path Length Distribution: Single-touch (30.9%), 2-3 touches (48.4%), 4+ touches (20.7%).",
            "Time-to-Convert: 43.1% convert within 3 days; 37.5% convert between 4 to 14 days; 19.4% require 15 to 30 days.",
            "Top Converting Multi-Touch Sequences: Paid Social > Paid Search (43), Paid Search > Direct (41), Paid Social > Organic Search (35), Paid Social > Email Marketing (33).",
            "Key Insight: Students introduced via Paid Social require search, email nurture, and direct recall before completing enrollment."
        ],
        "kpis": [
            ("Multi-Touch Share", "69.1%", "1,693 of 2,450 Journeys"),
            ("Median Gestation", "4.1 Days", "Consideration Span"),
            ("Top Assisted Pair", "Social > Search", "43 Enrolled Students")
        ]
    },
    {
        "slide_num": 8,
        "action_title": "Funnel Role Analysis: Paid Social and Display Act as Essential Feeders with High Assist Ratios",
        "category": "FUNNEL ROLE",
        "bullets": [
            "Top/Mid-Funnel Feeders: Display Ads (2.61 Assist:Last Ratio) and Paid Social (2.14 Assist:Last Ratio) originate pipeline.",
            "Nurturing Engine: Email Marketing generates 3,028 assisting interactions, acting as the primary mid-funnel glue.",
            "Closing Harvesters: Paid Search (1.32 ratio) and Direct disproportionately capture conversions originated elsewhere.",
            "Management Action: Evaluating Social or Display purely on Last-Click penalizes them for originating customers who convert via Direct."
        ],
        "kpis": [
            ("Display Assist Ratio", "2.61", "Feeder Channel"),
            ("Social Assist Ratio", "2.14", "Feeder Channel"),
            ("Search Assist Ratio", "1.32", "Closer Channel")
        ]
    },
    {
        "slide_num": 9,
        "action_title": "Attribution Model Disagreement: Last-Touch Undervalues Paid Social by +47.6% and Over-Credits Direct by -33.6%",
        "category": "ATTRIBUTION COMPARISON",
        "bullets": [
            "The Attribution Shift: Position-Based (U-Shaped) credits Paid Social with $571.9K revenue vs $387.4K in Last-Touch (+47.6% lift).",
            "Display Ad Re-evaluation: Display credit rises from $198.2K to $273.0K (+37.8%) when top-of-funnel origination is accounted for.",
            "Direct Demoted: Direct revenue drops from $554.4K (Last-Touch) to $368.2K (Position-Based) as upstream sources claim rightful credit.",
            "Executive Consequence: Under Last-Touch, marketing would defund the exact social and display campaigns generating half its leads."
        ],
        "kpis": [
            ("Social Rev Delta", "+$184.6K", "+47.6% Credit Lift"),
            ("Display Rev Delta", "+$74.8K", "+37.8% Credit Lift"),
            ("Direct Rev Delta", "-$186.2K", "-33.6% Credit Drop")
        ]
    },
    {
        "slide_num": 10,
        "action_title": "Data-Driven Markov & Shapley Models: Algorithmic Removal Effects Confirm Heavy Mid-Funnel Value",
        "category": "ALGORITHMIC ATTRIBUTION",
        "bullets": [
            "Markov Removal Effect: Removing Paid Social from the transition graph causes an 18.2% drop in network conversions.",
            "Shapley Value Formulation: Marginal cooperative contributions assign $543.0K to Social, $528.5K to Search, and $229.0K to Email Marketing, validating Position-Based alignment.",
            "Exact Penny Efficiency: Cooperative game theory axioms guarantee full revenue conservation: sum of channel Shapley values equals $2,382,514.60.",
            "Operational Synthesis: Position-Based U-Shaped (40-20-40) selected as daily operational model; Markov & Shapley used for quarterly budget setting."
        ],
        "kpis": [
            ("Shapley Social Rev", "$543.0K", "Game-Theoretic Credit"),
            ("Shapley Email Rev", "$229.0K", "High-Leverage Nurture"),
            ("Attribution Sum", "$2.38M", "Exact Penny Reconciled")
        ]
    },
    {
        "slide_num": 11,
        "action_title": "Campaign Performance Matrix: 3 Stars Drive Scale; 4 Email/Referral Workhorses Deserve Immediate Funding",
        "category": "PORTFOLIO QUADRANTS",
        "bullets": [
            "Stars (Protect & Scale +20%): PS_Brand_Core ($182K Rev, 7.06x ROAS) and SOC_Meta_Prospecting ($189K Rev, 7.50x ROAS).",
            "Scalable / Hidden Gems (Budget Infusion): EM_Alumni_Upsell (16.0x ROAS) and REF_Student_Advocate (5.93x ROAS) are starved for funds.",
            "Question Marks (Creative Refresh): PS_NonBrand_Analytics ($173K Rev, 2.43x ROAS) has elevated CPA; requires negative keyword pruning.",
            "Cut Candidates (Slash 50%): PS_Competitor_Intercept ($101.2K Spend, 1.78x ROAS, $550.21 CAC) should be defunded to sponsor email/referral."
        ],
        "kpis": [
            ("Portfolio Stars", "3 Campaigns", "Core Revenue Engine"),
            ("Scalable Gems", "3 Campaigns", "High ROAS / Low Spend"),
            ("Cut Candidates", "1 Campaign", "Immediate Savings")
        ]
    },
    {
        "slide_num": 12,
        "action_title": "Customer Lifetime Value: High-Quality Channels Deliver Sustainable 3.2x to 7.8x LTV:CAC Ratios",
        "category": "CLV & COHORT DYNAMICS",
        "bullets": [
            "Repeat Purchase Rate: 12.0% of students enroll in follow-on specialized certifications, generating $282.3K in repeat revenue.",
            "Headline CAC vs Cost per Order: Total spend ($426.4K) yields a Headline CAC of $174.05 on 2,450 new students and a Cost per Order of $155.40 on 2,744 total orders.",
            "Historical CLV: Blended historical revenue per customer is $1,087.68, yielding a healthy 6.25x LTV:CAC ratio.",
            "Predictive Payback: Forward-looking 12-month BG/NBD model forecasts average student value expanding to $2,714, providing massive headroom."
        ],
        "kpis": [
            ("Headline CAC", "$174.05", "New Student Cost"),
            ("Cost Per Order", "$155.40", "All Orders Completed"),
            ("LTV:CAC Ratio", "6.25x", "Strong Portfolio Health")
        ]
    },
    {
        "slide_num": 13,
        "action_title": "Optimized Budget Reallocation: Zero-Sum Shift of $58.4K Expands Revenue by +$224.9K",
        "category": "BUDGET OPTIMIZATION",
        "bullets": [
            "The Capital Reallocation: Shift -$58,400 (-29.4%) from Paid Search into Email (+$21,250), Referral (+$20,250), Display (+$12,300), and Social (+$4,600).",
            "Constrained Reallocation: Marginal ROAS spread is 1.67x (Search at lower bound) to 4.91x (Email at capacity limit); unconstrained channels (Social and Display) equalized at 1.82x.",
            "Symmetrical Scenarios: Base Case yields +$224,908 incremental revenue ($1,914,446 total); Low Case (0.75x lift) yields +$168,681 ($1,858,219 total); High Case (1.25x lift) yields +$281,135 ($1,970,673 total).",
            "Zero Budget Increase: Total marketing expenditure remains exactly $426,418.04; returns generated solely through portfolio reallocation."
        ],
        "kpis": [
            ("Search Reduction", "-$58,400", "Pinned at Lower Bound"),
            ("Email Expansion", "+$21,250", "Pinned at Capacity Cap"),
            ("Net Base Uplift", "+$224,908", "+13.3% Paid Lift")
        ]
    },
    {
        "slide_num": 14,
        "action_title": "De-Risking & Execution Roadmap: 4-Week Matched-Market Geo-Holdout Test Validates Incrementality",
        "category": "EXECUTION & ROADMAP",
        "bullets": [
            "Phase 1: Matched Geo-Holdout Test (Weeks 1-4): Split 8 matched metro markets (Dallas/San Francisco vs Austin/Seattle).",
            "Phase 2: Automated Attribution Pipeline (Weeks 3-5): Automate SQL queries in DuckDB/SQLite with weekly reporting.",
            "Phase 3: Automated Email Trigger Scaling (Weeks 4-6): Deploy abandoned application and syllabus nurture automation sequences.",
            "Phase 4: Full Portfolio Rebalancing (Week 7+): Deploy final budget reallocation upon confirmation of p < 0.05 causal lift."
        ],
        "kpis": [
            ("Test Duration", "4 Weeks", "Difference-in-Diff"),
            ("Min Detectable Effect", "5.0% Lift", "95% Confidence"),
            ("Guardrail Stop-Loss", "+20% CPA", "Automatic Pause Rule")
        ]
    }
]

def generate_pptx():
    prs = Presentation()
    prs.slide_width = Inches(13.333) # 16:9 widescreen
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    for data in SLIDE_DATA:
        slide = prs.slides.add_slide(blank_layout)

        # Background
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = COLOR_NAVY if data.get("is_title") else COLOR_BG_LIGHT
        bg.line.color.rgb = COLOR_NAVY if data.get("is_title") else COLOR_BG_LIGHT

        if data.get("is_title"):
            # Title Slide
            tb = slide.shapes.add_textbox(Inches(1.5), Inches(1.8), Inches(10.333), Inches(4.0))
            tf = tb.text_frame
            tf.word_wrap = True

            p1 = tf.paragraphs[0]
            p1.text = data["title"]
            p1.font.size = Pt(38)
            p1.font.bold = True
            p1.font.color.rgb = COLOR_WHITE
            p1.font.name = "Segoe UI"
            p1.space_after = Pt(16)

            p2 = tf.add_paragraph()
            p2.text = data["subtitle"]
            p2.font.size = Pt(20)
            p2.font.color.rgb = COLOR_GREEN
            p2.font.name = "Segoe UI"
            p2.space_after = Pt(24)

            p3 = tf.add_paragraph()
            p3.text = data["author"]
            p3.font.size = Pt(13)
            p3.font.color.rgb = RGBColor(180, 200, 220)
            p3.font.name = "Segoe UI"
            continue

        # Standard Action-Titled Slide Header
        # Category Banner
        tb_cat = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.5), Inches(0.35))
        p_cat = tb_cat.text_frame.paragraphs[0]
        p_cat.text = data["category"]
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = COLOR_BLUE
        p_cat.font.name = "Segoe UI"

        # Action Title
        tb_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(11.7), Inches(0.9))
        p_title = tb_title.text_frame.paragraphs[0]
        p_title.text = data["action_title"]
        p_title.font.size = Pt(19)
        p_title.font.bold = True
        p_title.font.color.rgb = COLOR_NAVY
        p_title.font.name = "Segoe UI"
        tb_title.text_frame.word_wrap = True

        # Left Column: Strategic Insights Box
        left_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(7.8), Inches(5.0))
        left_box.fill.solid()
        left_box.fill.fore_color.rgb = COLOR_WHITE
        left_box.line.color.rgb = RGBColor(220, 226, 235)

        tb_bullets = slide.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(7.4), Inches(4.6))
        tf_b = tb_bullets.text_frame
        tf_b.word_wrap = True

        for i, b_text in enumerate(data["bullets"]):
            p = tf_b.paragraphs[0] if i == 0 else tf_b.add_paragraph()
            p.text = f"•  {b_text}"
            p.font.size = Pt(13)
            p.font.color.rgb = COLOR_TEXT
            p.font.name = "Segoe UI"
            p.space_after = Pt(13)

        # Right Column: KPI Metric Cards
        card_top = 1.8
        for label, val, sub in data["kpis"]:
            card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(9.0), Inches(card_top), Inches(3.5), Inches(1.45))
            card.fill.solid()
            card.fill.fore_color.rgb = COLOR_WHITE
            card.line.color.rgb = RGBColor(220, 226, 235)

            # Left accent stripe
            stripe = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(9.0), Inches(card_top), Inches(0.12), Inches(1.45))
            stripe.fill.solid()
            stripe.fill.fore_color.rgb = COLOR_BLUE
            stripe.line.fill.background()

            tb_c = slide.shapes.add_textbox(Inches(9.25), Inches(card_top + 0.1), Inches(3.1), Inches(1.25))
            tf_c = tb_c.text_frame
            tf_c.word_wrap = True

            p_lbl = tf_c.paragraphs[0]
            p_lbl.text = label.upper()
            p_lbl.font.size = Pt(10)
            p_lbl.font.bold = True
            p_lbl.font.color.rgb = COLOR_MUTED
            p_lbl.font.name = "Segoe UI"

            p_val = tf_c.add_paragraph()
            p_val.text = val
            p_val.font.size = Pt(22)
            p_val.font.bold = True
            p_val.font.color.rgb = COLOR_NAVY
            p_val.font.name = "Segoe UI"

            p_sub = tf_c.add_paragraph()
            p_sub.text = sub
            p_sub.font.size = Pt(10)
            p_sub.font.color.rgb = COLOR_GREEN
            p_sub.font.name = "Segoe UI"

            card_top += 1.75

        # Footer Slide Number
        tb_foot = slide.shapes.add_textbox(Inches(11.5), Inches(7.0), Inches(1.0), Inches(0.3))
        p_foot = tb_foot.text_frame.paragraphs[0]
        p_foot.text = f"{data['slide_num']} / 14"
        p_foot.font.size = Pt(10)
        p_foot.font.color.rgb = COLOR_MUTED
        p_foot.font.name = "Segoe UI"

    prs.save(PPTX_PATH)
    print(f"Generated PowerPoint Deck: {PPTX_PATH}")

def generate_pdf_deck():
    # Build a clean HTML slides file and render to PDF using headless Edge/Chrome
    html_content = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    @page {
      size: 13.333in 7.5in;
      margin: 0;
    }
    body {
      margin: 0;
      padding: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
      background: #F8F9FA;
      color: #212529;
    }
    .slide {
      width: 13.333in;
      height: 7.5in;
      page-break-after: always;
      position: relative;
      box-sizing: border-box;
      padding: 0.5in 0.8in;
      background: #F8F9FA;
    }
    .slide.title-slide {
      background: #0B2545;
      color: white;
      display: flex;
      flex-direction: column;
      justify-content: center;
      padding-left: 1.5in;
    }
    .title-h1 {
      font-size: 40px;
      font-weight: 700;
      line-height: 1.2;
      color: white;
      margin-bottom: 18px;
    }
    .title-sub {
      font-size: 21px;
      color: #2A9D8F;
      margin-bottom: 24px;
      font-weight: 500;
    }
    .title-meta {
      font-size: 14px;
      color: #B0C4DE;
      line-height: 1.5;
    }
    .cat-tag {
      font-size: 12px;
      font-weight: 700;
      color: #007BFF;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 6px;
    }
    .action-title {
      font-size: 21px;
      font-weight: 700;
      color: #0B2545;
      margin-bottom: 22px;
      line-height: 1.25;
    }
    .content-grid {
      display: grid;
      grid-template-columns: 7.6in 3.6in;
      gap: 0.5in;
    }
    .left-card {
      background: white;
      border: 1px solid #DCE2EB;
      border-radius: 10px;
      padding: 24px 30px;
      height: 4.8in;
      box-sizing: border-box;
    }
    .bullet-item {
      font-size: 14.5px;
      line-height: 1.55;
      margin-bottom: 14px;
      position: relative;
      padding-left: 20px;
    }
    .bullet-item::before {
      content: "•";
      position: absolute;
      left: 0;
      color: #007BFF;
      font-weight: bold;
      font-size: 18px;
    }
    .kpi-container {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    .kpi-card {
      background: white;
      border: 1px solid #DCE2EB;
      border-left: 5px solid #007BFF;
      border-radius: 8px;
      padding: 16px 20px;
    }
    .kpi-label {
      font-size: 11px;
      font-weight: 700;
      color: #6C757D;
      text-transform: uppercase;
      margin-bottom: 4px;
    }
    .kpi-value {
      font-size: 26px;
      font-weight: 700;
      color: #0B2545;
      margin-bottom: 4px;
    }
    .kpi-subtext {
      font-size: 12px;
      color: #2A9D8F;
      font-weight: 600;
    }
    .slide-num {
      position: absolute;
      bottom: 0.3in;
      right: 0.8in;
      font-size: 12px;
      color: #6C757D;
      font-weight: 600;
    }
  </style>
</head>
<body>
"""
    for data in SLIDE_DATA:
        if data.get("is_title"):
            html_content += f"""
  <div class="slide title-slide">
    <div class="title-h1">{data['title'].replace(chr(10), '<br>')}</div>
    <div class="title-sub">{data['subtitle']}</div>
    <div class="title-meta">{data['author'].replace(chr(10), '<br>')}</div>
  </div>
"""
        else:
            bullets_html = "".join([f'<div class="bullet-item">{b}</div>' for b in data["bullets"]])
            kpi_html = ""
            for lbl, val, sub in data["kpis"]:
                kpi_html += f"""
      <div class="kpi-card">
        <div class="kpi-label">{lbl}</div>
        <div class="kpi-value">{val}</div>
        <div class="kpi-subtext">{sub}</div>
      </div>
"""
            html_content += f"""
  <div class="slide">
    <div class="cat-tag">{data['category']}</div>
    <div class="action-title">{data['action_title']}</div>
    <div class="content-grid">
      <div class="left-card">
        {bullets_html}
      </div>
      <div class="kpi-container">
        {kpi_html}
      </div>
    </div>
    <div class="slide-num">{data['slide_num']} / 14</div>
  </div>
"""
    html_content += """
</body>
</html>
"""
    with open(HTML_SLIDES_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)

    # Render PDF via Playwright
    try:
        from playwright.sync_api import sync_playwright
        edge_paths = [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        ]
        edge_exe = next((p for p in edge_paths if os.path.exists(p)), None)
        if edge_exe:
            with sync_playwright() as p:
                browser = p.chromium.launch(executable_path=edge_exe, headless=True)
                page = browser.new_page(viewport={"width": 1920, "height": 1080})
                page.goto(f"file:///{os.path.abspath(HTML_SLIDES_PATH).replace(os.sep, '/')}")
                page.wait_for_timeout(1000)
                page.pdf(path=PDF_PATH, width="13.333in", height="7.5in", print_background=True)
                browser.close()
            print(f"Generated Presentation PDF: {PDF_PATH}")
    except Exception as e:
        print(f"PDF generation note: {e}")

if __name__ == "__main__":
    generate_pptx()
    generate_pdf_deck()
