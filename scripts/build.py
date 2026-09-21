#!/usr/bin/env python3
"""
Static site generator for Community Partners Initiatives (cpinitiatives.org).

Pure front-end, no build tooling required at runtime — this script just keeps
every page's nav/footer/data in sync from one source of truth, then writes
plain .html files that GitHub Pages serves as-is. Re-run after editing DATA
or the templates below: `python3 scripts/build.py`.
"""

import json
import os
import re
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_URL = "https://cpinitiatives.org"
ORG_NAME = "Community Partners Initiatives"
ORG_SHORT = "CPI"

MISSION_STATEMENT = (
    "Community Partners Initiatives is founded on the conviction that no single "
    "organization can solve systemic recidivism or institutional vulnerability in "
    "isolation. By establishing a shared standard of unity, transparency, and "
    "resource convergence at cpinitiatives.org, we align local institutions into a "
    "unified support network—ensuring that every person returning to our "
    "community meets an open door, a stable home, and an accessible path to "
    "self-determination."
)

# --------------------------------------------------------------------------
# DATA (placeholder launch-slice content — replace with real partner data
# before go-live; see README.md)
# --------------------------------------------------------------------------

CATEGORIES = [
    {
        "slug": "housing",
        "name": "Housing Stability",
        "icon": "\U0001F3E0",
        "desc": "Housing navigation, transitional housing, supportive housing, permanent housing.",
    },
    {
        "slug": "workforce",
        "name": "Workforce & Economic Mobility",
        "icon": "\U0001F4BC",
        "desc": "Training, credentialing, employment, entrepreneurship, fair-chance opportunities.",
    },
    {
        "slug": "health",
        "name": "Health & Wellness",
        "icon": "\U0001FA7A",
        "desc": "Behavioral health, recovery, healthcare, trauma-informed care.",
    },
    {
        "slug": "whole-person",
        "name": "Whole-Person Support",
        "icon": "\U0001F91D",
        "desc": "Legal services, transportation, food access, financial support, family services.",
    },
]
CAT_BY_SLUG = {c["slug"]: c for c in CATEGORIES}

LOCATIONS = ["Compton", "South Los Angeles", "Watts", "Gardena", "Inglewood", "Long Beach", "Carson"]

PARTNERS = [
    {
        "slug": "community-hope-center",
        "name": "Community Hope Center",
        "short": "Housing navigation and transitional placements for people returning to the community.",
        "description": (
            "Community Hope Center provides housing navigation, transitional housing beds, and "
            "reentry case management for individuals and families across South Los Angeles. Their "
            "team coordinates directly with local jails, courts, and probation to ensure a stable "
            "home is ready before release."
        ),
        "categories": ["housing", "whole-person"],
        "locations": ["Compton", "South Los Angeles"],
        "population_served": "Justice-impacted adults, families exiting homelessness",
        "languages": ["English", "Spanish"],
        "accepting_referrals": True,
        "verification_status": "Verified CPI Partner",
        "last_verified": "2026-08-01",
        "website": "#",
        "email": "hello@communityhopecenter.example.org",
        "hours": "Mon–Fri, 9am–5pm",
        "eligibility": "Open to adults referred by CPI partner agencies, courts, or self-referral.",
        "referral_info": "Submit a warm-handoff request through the CPI partner network or call during business hours.",
    },
    {
        "slug": "horizon-workforce-alliance",
        "name": "Horizon Workforce Alliance",
        "short": "Job training, credentialing, and employer placement for the South Bay.",
        "description": (
            "Horizon Workforce Alliance runs credentialing cohorts in logistics, construction, and "
            "healthcare support, paired with direct placement pipelines to fair-chance employers "
            "across Long Beach and Carson."
        ),
        "categories": ["workforce"],
        "locations": ["Long Beach", "Carson"],
        "population_served": "Adults seeking employment, fair-chance job seekers",
        "languages": ["English", "Spanish", "Khmer"],
        "accepting_referrals": True,
        "verification_status": "Verified CPI Partner",
        "last_verified": "2026-07-18",
        "website": "#",
        "email": "intake@horizonworkforce.example.org",
        "hours": "Mon–Sat, 8am–6pm",
        "eligibility": "18+, authorized to work in the U.S. No conviction history exclusions.",
        "referral_info": "Partner agencies can refer directly; walk-ins welcome for intake days.",
    },
    {
        "slug": "watts-wellness-collective",
        "name": "Watts Wellness Collective",
        "short": "Behavioral health, recovery support, and trauma-informed care.",
        "description": (
            "Watts Wellness Collective delivers outpatient behavioral health, substance-use "
            "recovery groups, and trauma-informed counseling, with mobile outreach into "
            "underserved pockets of South Los Angeles."
        ),
        "categories": ["health"],
        "locations": ["Watts", "South Los Angeles"],
        "population_served": "Adults and youth needing behavioral health or recovery support",
        "languages": ["English", "Spanish"],
        "accepting_referrals": True,
        "verification_status": "Verified CPI Partner",
        "last_verified": "2026-08-10",
        "website": "#",
        "email": "care@wattswellness.example.org",
        "hours": "Mon–Fri, 8am–7pm; mobile unit weekends",
        "eligibility": "Open referral, sliding-scale fees, Medi-Cal accepted.",
        "referral_info": "Clinical partners can submit a warm referral; self-referral by phone or walk-in.",
    },
    {
        "slug": "gardena-family-resource-network",
        "name": "Gardena Family Resource Network",
        "short": "Legal aid, food access, and family stabilization services.",
        "description": (
            "Gardena Family Resource Network connects families to legal aid clinics, food "
            "assistance, and financial-literacy coaching, with a focus on keeping families intact "
            "through reentry and economic hardship."
        ),
        "categories": ["whole-person"],
        "locations": ["Gardena", "Inglewood"],
        "population_served": "Families, caregivers, justice-impacted parents",
        "languages": ["English", "Spanish", "Tagalog"],
        "accepting_referrals": True,
        "verification_status": "Verified CPI Partner",
        "last_verified": "2026-06-22",
        "website": "#",
        "email": "info@gardenafrn.example.org",
        "hours": "Tue–Sat, 10am–6pm",
        "eligibility": "Families and individuals residing in South Bay / South LA service area.",
        "referral_info": "Referrals accepted from any CPI partner or direct community request.",
    },
    {
        "slug": "second-chance-works",
        "name": "Second Chance Works",
        "short": "Fair-chance employment placement and employer partnerships.",
        "description": (
            "Second Chance Works builds direct partnerships with fair-chance employers and "
            "provides job-readiness coaching, mentorship, and post-placement retention support "
            "for people returning from incarceration."
        ),
        "categories": ["workforce", "whole-person"],
        "locations": ["Compton", "Long Beach"],
        "population_served": "Justice-impacted job seekers",
        "languages": ["English", "Spanish"],
        "accepting_referrals": True,
        "verification_status": "Verified CPI Partner",
        "last_verified": "2026-08-05",
        "website": "#",
        "email": "connect@secondchanceworks.example.org",
        "hours": "Mon–Fri, 9am–5pm",
        "eligibility": "Justice-impacted adults, no exclusions by conviction type.",
        "referral_info": "Warm handoffs from reentry, probation, or parole partners preferred.",
    },
    {
        "slug": "south-bay-health-partners",
        "name": "South Bay Health Partners",
        "short": "Primary and preventive healthcare across the South Bay.",
        "description": (
            "South Bay Health Partners operates community health clinics offering primary care, "
            "preventive screenings, and care coordination for uninsured and underinsured "
            "residents across Carson, Gardena, and Long Beach."
        ),
        "categories": ["health"],
        "locations": ["Carson", "Gardena", "Long Beach"],
        "population_served": "Uninsured and underinsured residents",
        "languages": ["English", "Spanish", "Khmer", "Tagalog"],
        "accepting_referrals": True,
        "verification_status": "Verified CPI Partner",
        "last_verified": "2026-07-29",
        "website": "#",
        "email": "referrals@southbayhealth.example.org",
        "hours": "Mon–Fri, 8am–5:30pm",
        "eligibility": "Open to all residents regardless of insurance status.",
        "referral_info": "Accepts referrals from any partner organization or self-referral by phone.",
    },
]
PARTNER_BY_SLUG = {p["slug"]: p for p in PARTNERS}

INITIATIVES = [
    {
        "slug": "transitional-housing-expansion",
        "title": "Transitional Housing Expansion",
        "status": "active",
        "category": "housing",
        "summary": "Expanding transitional and supportive housing capacity across South Los Angeles.",
        "problem": (
            "Demand for transitional beds in South Los Angeles regularly outpaces supply, leaving "
            "people returning from incarceration or homelessness without a stable place to land in "
            "their first critical weeks."
        ),
        "goal": "Add 40 new transitional and supportive housing placements within 12 months.",
        "community_served": "Justice-impacted adults and families exiting homelessness",
        "geography": "South Los Angeles, Compton",
        "lead_organization": "community-hope-center",
        "partners": ["community-hope-center", "gardena-family-resource-network"],
        "needs": ["Housing providers", "Property partners", "Funders", "Transportation support"],
        "start_date": "2026-03-01",
        "target_date": "2027-03-01",
        "progress": 55,
    },
    {
        "slug": "fair-chance-employer-network",
        "title": "Fair-Chance Employer Network",
        "status": "forming",
        "category": "workforce",
        "summary": "Building a coalition of employers committed to fair-chance hiring across the South Bay.",
        "problem": (
            "Job seekers with conviction histories face systemic barriers to employment even after "
            "completing training, and employers willing to hire fair-chance often work in "
            "isolation without shared pipelines or mentorship support."
        ),
        "goal": "Recruit 15 committed fair-chance employers and place 100 job seekers in year one.",
        "community_served": "Justice-impacted job seekers",
        "geography": "Compton, Long Beach, Carson",
        "lead_organization": "second-chance-works",
        "partners": ["second-chance-works", "horizon-workforce-alliance"],
        "needs": ["Employers", "Job training partners", "Mentors", "Recruiters"],
        "start_date": "2026-05-01",
        "target_date": "2027-05-01",
        "progress": 20,
    },
    {
        "slug": "mobile-behavioral-health-access",
        "title": "Mobile Behavioral Health Access",
        "status": "open",
        "category": "health",
        "summary": "Bringing behavioral health and recovery support directly into underserved neighborhoods.",
        "problem": (
            "Many residents in need of behavioral health or recovery support cannot reach a clinic "
            "due to transportation barriers, work schedules, or trust gaps with formal institutions."
        ),
        "goal": "Launch a mobile behavioral health unit serving 6 neighborhoods on a weekly rotation.",
        "community_served": "Adults and youth needing behavioral health or recovery support",
        "geography": "Watts, South Los Angeles",
        "lead_organization": "watts-wellness-collective",
        "partners": ["watts-wellness-collective"],
        "needs": ["Clinical partners", "Community outreach partners", "Transportation", "Funding"],
        "start_date": "2026-09-01",
        "target_date": None,
        "progress": 10,
    },
]
INITIATIVE_BY_SLUG = {i["slug"]: i for i in INITIATIVES}

STATUS_LABELS = {
    "open": "Open",
    "forming": "Forming",
    "active": "Active",
    "funded": "Funded",
    "delivering": "Delivering",
    "completed": "Completed",
}

NEEDS = [
    {
        "id": "cpi-need-0024",
        "title": "Laptops for Workforce Training Cohort",
        "category": "equipment",
        "quantity": 10,
        "location": "Los Angeles County",
        "initiative": "fair-chance-employer-network",
        "status": "open",
        "support_type": "Supplies Needed",
    },
    {
        "id": "cpi-need-0025",
        "title": "Housing Partner Needed for 4 Transitional Placements",
        "category": "housing",
        "quantity": 4,
        "location": "South Los Angeles",
        "initiative": "transitional-housing-expansion",
        "status": "open",
        "support_type": "Housing Needed",
    },
    {
        "id": "cpi-need-0026",
        "title": "Employer Seeking Partnership With Fair-Chance Training Provider",
        "category": "employer",
        "quantity": 1,
        "location": "Long Beach",
        "initiative": "fair-chance-employer-network",
        "status": "open",
        "support_type": "Employer Needed",
    },
    {
        "id": "cpi-need-0027",
        "title": "Volunteer Transportation Requested for Weekly Appointments",
        "category": "transportation",
        "quantity": 6,
        "location": "Watts",
        "initiative": "mobile-behavioral-health-access",
        "status": "open",
        "support_type": "Transportation Needed",
    },
    {
        "id": "cpi-need-0028",
        "title": "Clinical Organization Needed for Behavioral Health Initiative",
        "category": "partner",
        "quantity": 1,
        "location": "South Los Angeles",
        "initiative": "mobile-behavioral-health-access",
        "status": "open",
        "support_type": "Partner Needed",
    },
]

RESOURCE_CATEGORIES = [
    "Reentry", "Housing", "Employment", "Benefits", "Health", "Behavioral Health",
    "Education", "Transportation", "Legal", "Financial Literacy", "Family Support",
]

RESOURCES = [
    {
        "title": "211 LA County",
        "category": "Reentry",
        "desc": "Free, confidential referral line and directory connecting residents to housing, food, health, and reentry services across LA County.",
        "url": "https://www.211la.org/",
    },
    {
        "title": "California EDD — Job Services",
        "category": "Employment",
        "desc": "State job search assistance, unemployment benefits, and workforce development programs.",
        "url": "https://edd.ca.gov/",
    },
    {
        "title": "LA County Department of Public Social Services",
        "category": "Benefits",
        "desc": "CalFresh, CalWORKs, General Relief, and other public benefits applications and case information.",
        "url": "https://dpss.lacounty.gov/",
    },
    {
        "title": "National Reentry Resource Center",
        "category": "Reentry",
        "desc": "National clearinghouse of reentry research, funding opportunities, and practice guides.",
        "url": "https://nationalreentryresourcecenter.org/",
    },
    {
        "title": "California Department of Rehabilitation",
        "category": "Employment",
        "desc": "Vocational rehabilitation services, job training, and independent living support.",
        "url": "https://www.dor.ca.gov/",
    },
    {
        "title": "LA County Department of Mental Health",
        "category": "Behavioral Health",
        "desc": "Countywide behavioral health services, crisis lines, and provider directory.",
        "url": "https://dmh.lacounty.gov/",
    },
    {
        "title": "Bet Tzedek Legal Services",
        "category": "Legal",
        "desc": "Free legal aid for low-income residents across Los Angeles County.",
        "url": "https://www.bettzedek.org/",
    },
    {
        "title": "Metro LA — Transportation Assistance",
        "category": "Transportation",
        "desc": "Reduced-fare programs and transit planning for LA County residents.",
        "url": "https://www.metro.net/",
    },
]

NAV_LINKS = [
    ("/", "Home"),
    ("/find-support.html", "Find Support"),
    ("/partners/", "Partners"),
    ("/initiatives/", "Initiatives"),
    ("/resources/", "Resources"),
    ("/about.html", "About"),
]

FOOTER_COLUMNS = [
    ("Explore", [
        ("/find-support.html", "Find Support"),
        ("/partners/", "Partners"),
        ("/initiatives/", "Initiatives"),
        ("/needs/", "Needs"),
    ]),
    ("Organization", [
        ("/about.html", "About"),
        ("/resources/", "Resources"),
        ("/get-involved.html", "Get Involved"),
    ]),
    ("Take Action", [
        ("/donate.html", "Donate"),
        ("/join.html", "Join CPI"),
        ("/contact.html", "Contact"),
        ("/portal.html", "Partner Portal"),
    ]),
]

GOOGLE_FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">'
)


def esc(s):
    if s is None:
        return ""
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def rel_prefix(depth):
    """Return the relative path prefix ('' , '../', '../../') for a page at given depth from root."""
    return "../" * depth


def nav_html(active_path, depth):
    p = rel_prefix(depth)

    def href(path):
        return p + path.lstrip("/") if path != "/" else (p if p else "./")

    links = []
    for path, label in NAV_LINKS:
        current = ' aria-current="page"' if path == active_path else ""
        links.append(f'<a href="{href(path)}"{current}>{label}</a>')

    mobile_links = []
    mobile_extra = [
        ("/needs/", "Community Needs"),
        ("/get-involved.html", "Get Involved"),
    ]
    for path, label in NAV_LINKS + mobile_extra:
        mobile_links.append(f'<a href="{href(path)}">{label}</a>')

    return f"""
<a class="skip-link" href="#main">Skip to content</a>
<header class="navbar">
  <div class="container navbar-inner">
    <a class="brand" href="{href('/')}">
      <span class="brand-mark">CPI</span>
      <span>Community Partners Initiatives</span>
    </a>
    <nav class="nav-links" aria-label="Primary">
      {''.join(links)}
    </nav>
    <div class="nav-utility">
      <a class="btn btn-tertiary" style="text-decoration:none" href="{href('/join.html')}">Join CPI</a>
      <a class="btn btn-primary donate-btn-nav" href="{href('/donate.html')}">Donate</a>
    </div>
    <button class="nav-toggle" aria-expanded="false" aria-controls="mobile-menu" aria-label="Open menu" data-nav-toggle>
      <span></span>
    </button>
  </div>
</header>
<div class="mobile-menu" id="mobile-menu" data-mobile-menu>
  <div class="container">
    {''.join(mobile_links)}
    <a class="btn btn-primary btn-block" href="{href('/donate.html')}">Donate</a>
    <a class="btn btn-secondary btn-block mt-16" href="{href('/join.html')}">Join CPI</a>
  </div>
</div>
<div class="mobile-sticky-cta">
  <a class="btn btn-primary btn-block" href="{href('/donate.html')}">Donate to CPI</a>
</div>
"""


def footer_html(depth):
    p = rel_prefix(depth)

    def href(path):
        return p + path.lstrip("/") if path != "/" else (p if p else "./")

    cols = []
    for title, items in FOOTER_COLUMNS:
        links = "".join(f'<a href="{href(path)}">{label}</a>' for path, label in items)
        cols.append(f'<div class="footer-col"><h4>{title}</h4>{links}</div>')

    return f"""
<footer class="site-footer">
  <div class="container footer-top">
    <div class="footer-grid">
      <div class="footer-brand">
        <div class="brand"><span class="brand-mark">CPI</span><span>Community Partners Initiatives</span></div>
        <p>One community. Connected. CPI unites housing, workforce, health, and reentry
        organizations into a single network so no one falls through the cracks.</p>
      </div>
      {''.join(cols)}
    </div>
  </div>
  <div class="container footer-bottom">
    <span>&copy; <span data-year>2026</span> Community Partners Initiatives. People &bull; Partnerships &bull; Progress.</span>
    <span>cpinitiatives.org</span>
  </div>
</footer>
"""


def page(title, description, active_path, depth, body, extra_head="", body_class="", schema=None):
    p = rel_prefix(depth)
    css_href = p + "assets/css/style.css"
    js_main = p + "assets/js/main.js"
    canonical = SITE_URL + (active_path if active_path != "/" else "/")
    schema_tag = f'<script type="application/ld+json">{json.dumps(schema)}</script>' if schema else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="Community Partners Initiatives">
<meta name="twitter:card" content="summary">
{GOOGLE_FONTS}
<link rel="stylesheet" href="{css_href}">
{extra_head}
{schema_tag}
</head>
<body class="{body_class}">
{nav_html(active_path, depth)}
<main id="main">
{body}
</main>
{footer_html(depth)}
<script src="{js_main}"></script>
</body>
</html>
"""


# --------------------------------------------------------------------------
# Shared component renderers
# --------------------------------------------------------------------------

def status_badge(status):
    label = STATUS_LABELS.get(status, status.title())
    return f'<span class="status-badge status-{status}">{label}</span>'


def service_chips(cat_slugs):
    chips = "".join(f'<span class="service-chip">{CAT_BY_SLUG[c]["name"]}</span>' for c in cat_slugs if c in CAT_BY_SLUG)
    return f'<div class="service-chip-row">{chips}</div>'


def partner_card(p_, depth):
    href = rel_prefix(depth) + f"partners/{p_['slug']}/"
    initials = "".join(w[0] for w in p_["name"].split()[:2]).upper()
    referral = '<span class="referral-badge">Accepting Referrals</span>' if p_["accepting_referrals"] else ""
    return f"""
<article class="partner-card" data-name="{esc(p_['name'].lower())}" data-categories="{','.join(p_['categories'])}" data-locations="{','.join(l.lower() for l in p_['locations'])}">
  <div class="card-logo">{initials}</div>
  <h3 class="card-title">{esc(p_['name'])}</h3>
  {service_chips(p_['categories'])}
  <p class="card-meta">Serving: {', '.join(p_['locations'])}</p>
  <div class="badge-row">
    {referral}
    <span class="verification-badge">&#10003; Verified CPI Partner</span>
  </div>
  <p class="card-meta">{esc(p_['short'])}</p>
  <a class="card-footer-link" href="{href}">View Organization &rarr;</a>
</article>
"""


def initiative_card(i, depth):
    href = rel_prefix(depth) + f"initiatives/{i['slug']}/"
    return f"""
<article class="initiative-card" data-title="{esc(i['title'].lower())}" data-category="{i['category']}" data-status="{i['status']}">
  {status_badge(i['status'])}
  {service_chips([i['category']])}
  <h3 class="card-title">{esc(i['title'])}</h3>
  <p class="card-meta">{esc(i['summary'])}</p>
  <p class="card-meta"><strong>Geography:</strong> {esc(i['geography'])}</p>
  <p class="card-meta"><strong>Needed:</strong> {', '.join(i['needs'])}</p>
  <a class="card-footer-link" href="{href}">Partner on This Initiative &rarr;</a>
</article>
"""


def need_card(n, depth):
    init = INITIATIVE_BY_SLUG.get(n["initiative"])
    init_link = ""
    if init:
        href = rel_prefix(depth) + f"initiatives/{init['slug']}/"
        init_link = f'<a class="card-footer-link" href="{href}">Related Initiative &rarr;</a>'
    return f"""
<article class="need-card" data-title="{esc(n['title'].lower())}" data-support="{n['support_type']}" data-location="{n['location'].lower()}">
  <span class="status-badge status-open">{esc(n['support_type'])}</span>
  <h3 class="card-title">{esc(n['title'])}</h3>
  <p class="card-meta">Quantity: <span class="need-qty">{n['quantity']}</span> &middot; {esc(n['location'])}</p>
  {init_link}
</article>
"""


def resource_card(r):
    return f"""
<article class="resource-card" data-category="{esc(r['category'])}" data-title="{esc(r['title'].lower())}">
  <span class="service-chip">{esc(r['category'])}</span>
  <h3 class="card-title">{esc(r['title'])}</h3>
  <p class="card-meta">{esc(r['desc'])}</p>
  <a class="card-footer-link" href="{esc(r['url'])}" target="_blank" rel="noopener noreferrer">Visit Resource &rarr;</a>
</article>
"""


# --------------------------------------------------------------------------
# Page builders
# --------------------------------------------------------------------------

def build_home():
    depth = 0
    pillar_cards = "".join(f"""
<a class="pillar-card" href="{rel_prefix(depth)}find-support.html?category={c['slug']}">
  <div class="pillar-icon">{c['icon']}</div>
  <h3>{c['name']}</h3>
  <p>{c['desc']}</p>
</a>""" for c in CATEGORIES)

    partner_previews = "".join(partner_card(p, depth) for p in PARTNERS[:3])
    initiative_previews = "".join(initiative_card(i, depth) for i in INITIATIVES)
    need_previews = "".join(need_card(n, depth) for n in NEEDS[:3])

    body = f"""
<section class="hero">
  <div class="container">
    <span class="hero-eyebrow">Community Partners Initiatives</span>
    <h1>Connecting People.<br>Uniting Partners.<br>Creating Opportunity.</h1>
    <p class="hero-sub">CPI connects community organizations across housing, workforce development,
    health, reentry, and wraparound services so people can reach the right support and
    organizations can accomplish more together.</p>
    <blockquote class="mission-quote">&ldquo;{MISSION_STATEMENT}&rdquo;</blockquote>
    <div class="hero-ctas">
      <a class="btn btn-primary" href="donate.html">Give Now</a>
      <a class="btn btn-secondary" href="join.html">Join as a Community Partner</a>
      <a class="btn btn-tertiary" href="initiatives/">Explore Current Initiatives</a>
    </div>
  </div>
</section>

<section>
  <div class="container">
    <div class="section-heading">
      <span class="eyebrow">What We Do</span>
      <h2>Four Pillars of Community Support</h2>
      <p>Every partner in the CPI network operates within one or more of these shared areas of support.</p>
    </div>
    <div class="pillar-grid">{pillar_cards}</div>
  </div>
</section>

<section class="section-surface">
  <div class="container">
    <div class="find-support">
      <div class="section-heading">
        <span class="eyebrow" style="color:#8ec3ff">Find Support</span>
        <h2>Find Community Support</h2>
        <p>No account required. Tell us what you need and where, and we'll surface verified partners.</p>
      </div>
      <form class="find-support-form" action="find-support.html" method="get">
        <div class="field">
          <label for="need-input">What do you need help with?</label>
          <input type="text" id="need-input" name="q" placeholder="e.g. housing, job training, behavioral health">
        </div>
        <div class="field">
          <label for="zip-input">Location / ZIP</label>
          <input type="text" id="zip-input" name="loc" placeholder="City or ZIP code">
        </div>
        <button class="btn btn-primary" type="submit">Find Partners</button>
      </form>
      <div class="chip-row" role="group" aria-label="Quick categories">
        {''.join(f'<a class="chip" href="find-support.html?category={c["slug"]}">{c["name"]}</a>' for c in CATEGORIES)}
      </div>
    </div>
  </div>
</section>

<section>
  <div class="container">
    <div class="section-heading-row">
      <div class="section-heading" style="margin-bottom:0">
        <span class="eyebrow">Partner Network</span>
        <h2>Organizations Working Together</h2>
        <p>Explore verified community organizations participating in the CPI network.</p>
      </div>
      <a class="btn btn-secondary" href="partners/">View Partner Network</a>
    </div>
    <div class="card-grid cols-3">{partner_previews}</div>
    <div class="text-center mt-32">
      <a class="btn btn-primary" href="join.html">Become a Partner</a>
    </div>
  </div>
</section>

<section class="section-surface">
  <div class="container">
    <div class="section-heading-row">
      <div class="section-heading" style="margin-bottom:0">
        <span class="eyebrow">Initiatives</span>
        <h2>Active CPI Initiatives</h2>
        <p>The community has needs right now. See what organizations are building and where you can help.</p>
      </div>
      <a class="btn btn-secondary" href="initiatives/">View All Initiatives</a>
    </div>
    <div class="card-grid cols-3">{initiative_previews}</div>
  </div>
</section>

<section>
  <div class="container">
    <div class="section-heading-row">
      <div class="section-heading" style="margin-bottom:0">
        <span class="eyebrow">Needs Board</span>
        <h2>Current Community Needs</h2>
        <p>Concrete, specific needs from partners right now &mdash; no need to guess how to help.</p>
      </div>
      <a class="btn btn-secondary" href="needs/">View Needs Board</a>
    </div>
    <div class="card-grid cols-3">{need_previews}</div>
  </div>
</section>

<section class="section-surface">
  <div class="container">
    <div class="section-heading">
      <span class="eyebrow">How CPI Works</span>
      <h2>Discover. Connect. Coordinate. Measure. Improve.</h2>
    </div>
    <div class="steps">
      <div class="step"><div class="num">1</div><h4>Discover</h4><p>Find verified organizations and active initiatives across the network.</p></div>
      <div class="step"><div class="num">2</div><h4>Connect</h4><p>Reach the right partner directly &mdash; no cold calls into the void.</p></div>
      <div class="step"><div class="num">3</div><h4>Coordinate</h4><p>Join initiatives and respond to concrete, published needs.</p></div>
      <div class="step"><div class="num">4</div><h4>Measure</h4><p>Track connections and outcomes across the network.</p></div>
      <div class="step"><div class="num">5</div><h4>Improve</h4><p>Feed what's working back into the next initiative.</p></div>
    </div>
  </div>
</section>

<section>
  <div class="container">
    <div class="section-heading">
      <span class="eyebrow">Network Activity</span>
      <h2>Building the Founding CPI Network</h2>
    </div>
    <div class="metric-grid">
      <div class="metric"><div class="value">{len(PARTNERS)}</div><div class="label">Partner Organizations</div></div>
      <div class="metric"><div class="value">{len(INITIATIVES)}</div><div class="label">Active Initiatives</div></div>
      <div class="metric"><div class="value">{len(NEEDS)}</div><div class="label">Open Community Needs</div></div>
      <div class="metric"><div class="value">{len(set(l for p in PARTNERS for l in p['locations']))}</div><div class="label">Communities Served</div></div>
    </div>
  </div>
</section>

<section class="section-surface">
  <div class="container">
    <div class="cta-section">
      <h2>Your organization should not have to solve everything alone.</h2>
      <p>Join a growing network of community organizations sharing resources, referrals,
      initiatives, and opportunities.</p>
      <div class="hero-ctas">
        <a class="btn btn-primary" href="join.html">Join the CPI Network</a>
        <a class="btn btn-secondary" href="donate.html">Give Now</a>
      </div>
    </div>
  </div>
</section>
"""
    schema = {
        "@context": "https://schema.org",
        "@type": "NGO",
        "name": ORG_NAME,
        "url": SITE_URL,
        "description": "Community Partners Initiatives connects housing, workforce, health, and reentry organizations into one coordinated support network.",
    }
    return page(
        "Community Partners Initiatives — People. Partnerships. Progress.",
        "CPI connects community organizations across housing, workforce, health, reentry, and "
        "wraparound services so people can reach the right support and organizations can "
        "accomplish more together.",
        "/", depth, body, schema=schema,
    )


def build_find_support():
    depth = 0
    partner_cards = "".join(partner_card(p, depth) for p in PARTNERS)
    body = f"""
<section class="page-header">
  <div class="container">
    <span class="hero-eyebrow">Find Support</span>
    <h1>Find Community Support</h1>
    <p class="hero-sub">Search verified CPI partner organizations by service, category, or location. No account required.</p>
  </div>
</section>
<section class="light-page">
  <div class="container">
    <div class="toolbar">
      <div class="search-bar">
        <span class="icon">&#128269;</span>
        <input type="text" id="partner-search" placeholder="Search organizations, programs, or services" aria-label="Search partners">
      </div>
      <div class="chip-row" role="group" aria-label="Filter by category" id="category-chips">
        <button class="chip" data-cat="all" aria-pressed="true">All Categories</button>
        {''.join(f'<button class="chip" data-cat="{c["slug"]}" aria-pressed="false">{c["name"]}</button>' for c in CATEGORIES)}
      </div>
      <p class="results-count" id="results-count"></p>
    </div>
    <div class="card-grid cols-3" id="partner-results">{partner_cards}</div>
    <p class="empty-state" id="empty-state" hidden>No partners match that search yet. Try a different category or keyword.</p>
  </div>
</section>
"""
    return page(
        "Find Community Support — CPI",
        "Search verified CPI partner organizations by service, category, or location.",
        "/find-support.html", depth, body,
        extra_head=f'<script src="{rel_prefix(depth)}assets/js/find-support.js" defer></script>',
    )


def build_partners_index():
    depth = 1
    cards = "".join(partner_card(p, depth) for p in PARTNERS)
    body = f"""
<section class="page-header">
  <div class="container">
    <span class="hero-eyebrow">Partner Network</span>
    <h1>Organizations Working Together</h1>
    <p class="hero-sub">Explore verified community organizations participating in the CPI network across housing, workforce, health, and whole-person support.</p>
    <div class="hero-ctas">
      <a class="btn btn-primary" href="{rel_prefix(depth)}join.html">Become a Partner</a>
    </div>
  </div>
</section>
<section class="light-page">
  <div class="container">
    <div class="toolbar">
      <div class="search-bar">
        <span class="icon">&#128269;</span>
        <input type="text" id="partner-search" placeholder="Search organizations, programs, or services" aria-label="Search partners">
      </div>
      <div class="filter-row">
        <select id="filter-category" aria-label="Filter by service category">
          <option value="all">All Services</option>
          {''.join(f'<option value="{c["slug"]}">{c["name"]}</option>' for c in CATEGORIES)}
        </select>
        <select id="filter-location" aria-label="Filter by location">
          <option value="all">All Locations</option>
          {''.join(f'<option value="{l.lower()}">{l}</option>' for l in LOCATIONS)}
        </select>
      </div>
      <p class="results-count" id="results-count"></p>
    </div>
    <div class="card-grid cols-3" id="partner-results">{cards}</div>
    <p class="empty-state" id="empty-state" hidden>No partners match those filters yet.</p>
  </div>
</section>
"""
    return page(
        "Partner Directory — CPI",
        "Search and filter verified Community Partners Initiatives organizations by service, population, and location.",
        "/partners/", depth, body,
        extra_head=f'<script src="{rel_prefix(depth)}assets/js/partners.js" defer></script>',
    )


def build_partner_detail(p_):
    depth = 2
    other_initiatives = [i for i in INITIATIVES if p_["slug"] in i["partners"]]
    init_html = "".join(f"""
<li><a href="{rel_prefix(depth)}initiatives/{i['slug']}/">{esc(i['title'])}</a> &mdash; {status_badge(i['status'])}</li>
""" for i in other_initiatives) or "<li>No active initiatives listed yet.</li>"

    body = f"""
<section class="page-header">
  <div class="container">
    <p class="breadcrumb"><a href="{rel_prefix(depth)}partners/">Partners</a> / {esc(p_['name'])}</p>
    <span class="hero-eyebrow">{'&nbsp;'.join(CAT_BY_SLUG[c]['name'] for c in p_['categories'])}</span>
    <h1>{esc(p_['name'])}</h1>
    <p class="hero-sub">{esc(p_['short'])}</p>
    <div class="badge-row mt-16">
      <span class="verification-badge">&#10003; Verified CPI Partner</span>
      {'<span class="referral-badge">Accepting Referrals</span>' if p_['accepting_referrals'] else ''}
    </div>
  </div>
</section>
<section class="light-page">
  <div class="container">
    <div class="detail-layout">
      <div>
        <div class="detail-block">
          <h2>About</h2>
          <p>{esc(p_['description'])}</p>
        </div>
        <div class="detail-block">
          <h2>Services</h2>
          {service_chips(p_['categories'])}
        </div>
        <div class="detail-block">
          <h2>Population Served</h2>
          <p>{esc(p_['population_served'])}</p>
        </div>
        <div class="detail-block">
          <h2>Eligibility</h2>
          <p>{esc(p_['eligibility'])}</p>
        </div>
        <div class="detail-block">
          <h2>Referral Information</h2>
          <p>{esc(p_['referral_info'])}</p>
        </div>
        <div class="detail-block">
          <h2>Active CPI Initiatives</h2>
          <ul>{init_html}</ul>
        </div>
      </div>
      <aside>
        <div class="sidebar-card">
          <h3>Organization Details</h3>
          <div class="kv-row"><span class="k">Locations</span><span class="v">{', '.join(p_['locations'])}</span></div>
          <div class="kv-row"><span class="k">Languages</span><span class="v">{', '.join(p_['languages'])}</span></div>
          <div class="kv-row"><span class="k">Hours</span><span class="v">{esc(p_['hours'])}</span></div>
          <div class="kv-row"><span class="k">Last Verified</span><span class="v">{esc(p_['last_verified'])}</span></div>
        </div>
        <div class="sidebar-card">
          <h3>Contact</h3>
          <div class="stack">
            <a class="btn btn-primary btn-block" href="{esc(p_['website'])}" target="_blank" rel="noopener noreferrer">Visit Organization</a>
            <a class="btn btn-secondary btn-block" href="mailto:{esc(p_['email'])}">Request Connection</a>
          </div>
        </div>
      </aside>
    </div>
  </div>
</section>
"""
    schema = {
        "@context": "https://schema.org",
        "@type": "NGO",
        "name": p_["name"],
        "description": p_["short"],
        "areaServed": p_["locations"],
    }
    return page(
        f"{p_['name']} — CPI Verified Partner",
        p_["short"],
        f"/partners/{p_['slug']}/", depth, body, schema=schema,
    )


def build_initiatives_index():
    depth = 1
    cards = "".join(initiative_card(i, depth) for i in INITIATIVES)
    body = f"""
<section class="page-header">
  <div class="container">
    <span class="hero-eyebrow">Initiatives</span>
    <h1>The Community Has Needs Right Now</h1>
    <p class="hero-sub">See what organizations are building, what resources are missing, and where you can help.</p>
  </div>
</section>
<section class="light-page">
  <div class="container">
    <div class="toolbar">
      <div class="filter-row">
        <select id="filter-category" aria-label="Filter by category">
          <option value="all">All Categories</option>
          {''.join(f'<option value="{c["slug"]}">{c["name"]}</option>' for c in CATEGORIES)}
        </select>
        <select id="filter-status" aria-label="Filter by status">
          <option value="all">All Statuses</option>
          {''.join(f'<option value="{s}">{label}</option>' for s, label in STATUS_LABELS.items())}
        </select>
      </div>
      <p class="results-count" id="results-count"></p>
    </div>
    <div class="card-grid cols-3" id="initiative-results">{cards}</div>
    <p class="empty-state" id="empty-state" hidden>No initiatives match those filters yet.</p>
  </div>
</section>
"""
    return page(
        "Initiatives — CPI",
        "Explore active Community Partners Initiatives projects and see where your organization or support is needed.",
        "/initiatives/", depth, body,
        extra_head=f'<script src="{rel_prefix(depth)}assets/js/initiatives.js" defer></script>',
    )


def build_initiative_detail(i):
    depth = 2
    lead = PARTNER_BY_SLUG.get(i["lead_organization"])
    partner_list = "".join(
        f'<li><a href="{rel_prefix(depth)}partners/{s}/">{esc(PARTNER_BY_SLUG[s]["name"])}</a></li>'
        for s in i["partners"] if s in PARTNER_BY_SLUG
    )
    needs_list = "".join(f"<li>{esc(n)}</li>" for n in i["needs"])
    target = i["target_date"] or "Ongoing"

    body = f"""
<section class="page-header">
  <div class="container">
    <p class="breadcrumb"><a href="{rel_prefix(depth)}initiatives/">Initiatives</a> / {esc(i['title'])}</p>
    <div class="badge-row">
      {status_badge(i['status'])}
      <span class="service-chip">{CAT_BY_SLUG[i['category']]['name']}</span>
    </div>
    <h1 class="mt-16">{esc(i['title'])}</h1>
    <p class="hero-sub">{esc(i['summary'])}</p>
  </div>
</section>
<section class="light-page">
  <div class="container">
    <div class="detail-layout">
      <div>
        <div class="detail-block">
          <h2>Problem</h2>
          <p>{esc(i['problem'])}</p>
        </div>
        <div class="detail-block">
          <h2>Goal</h2>
          <p>{esc(i['goal'])}</p>
        </div>
        <div class="detail-block">
          <h2>Current Partners</h2>
          <ul>{partner_list}</ul>
        </div>
        <div class="detail-block">
          <h2>What We Need</h2>
          <ul>{needs_list}</ul>
        </div>
        <div class="detail-block">
          <h2>Join This Initiative</h2>
          <p>Choose how you'd like to help and we'll connect you with the lead organization.</p>
          <div class="hero-ctas">
            <a class="btn btn-primary" href="{rel_prefix(depth)}join.html?initiative={i['slug']}">I Can Help</a>
          </div>
        </div>
      </div>
      <aside>
        <div class="sidebar-card">
          <h3>Initiative Details</h3>
          <div class="kv-row"><span class="k">Lead Organization</span><span class="v">{f'<a href="{rel_prefix(depth)}partners/{lead["slug"]}/">{esc(lead["name"])}</a>' if lead else 'CPI'}</span></div>
          <div class="kv-row"><span class="k">Community Served</span><span class="v">{esc(i['community_served'])}</span></div>
          <div class="kv-row"><span class="k">Geography</span><span class="v">{esc(i['geography'])}</span></div>
          <div class="kv-row"><span class="k">Start Date</span><span class="v">{esc(i['start_date'])}</span></div>
          <div class="kv-row"><span class="k">Target Date</span><span class="v">{esc(target)}</span></div>
        </div>
        <div class="sidebar-card">
          <h3>Progress</h3>
          <div class="kv-row"><span class="k">Toward Goal</span><span class="v">{i['progress']}%</span></div>
          <div class="progress-track"><div class="progress-fill" style="width:{i['progress']}%"></div></div>
        </div>
      </aside>
    </div>
  </div>
</section>
"""
    schema = {
        "@context": "https://schema.org",
        "@type": "Project",
        "name": i["title"],
        "description": i["summary"],
        "areaServed": i["geography"],
    }
    return page(
        f"{i['title']} — CPI Initiative",
        i["summary"],
        f"/initiatives/{i['slug']}/", depth, body, schema=schema,
    )


def build_needs_index():
    depth = 1
    cards = "".join(need_card(n, depth) for n in NEEDS)
    support_types = sorted(set(n["support_type"] for n in NEEDS))
    body = f"""
<section class="page-header">
  <div class="container">
    <span class="hero-eyebrow">Needs Board</span>
    <h1>Current Community Needs</h1>
    <p class="hero-sub">A lightweight public bulletin board of concrete partner needs — no need to guess how to help.</p>
  </div>
</section>
<section class="light-page">
  <div class="container">
    <div class="toolbar">
      <div class="filter-row">
        <select id="filter-support" aria-label="Filter by support type">
          <option value="all">All Support Types</option>
          {''.join(f'<option value="{s}">{s}</option>' for s in support_types)}
        </select>
      </div>
      <p class="results-count" id="results-count"></p>
    </div>
    <div class="card-grid cols-3" id="need-results">{cards}</div>
    <p class="empty-state" id="empty-state" hidden>No open needs match that filter right now.</p>
  </div>
</section>
"""
    return page(
        "Needs Board — CPI",
        "Concrete, current needs from Community Partners Initiatives partner organizations — supplies, housing, employers, transportation, and more.",
        "/needs/", depth, body,
        extra_head=f'<script src="{rel_prefix(depth)}assets/js/needs.js" defer></script>',
    )


def build_resources_index():
    depth = 1
    cards = "".join(resource_card(r) for r in RESOURCES)
    body = f"""
<section class="page-header">
  <div class="container">
    <span class="hero-eyebrow">Resources</span>
    <h1>Community Resources</h1>
    <p class="hero-sub">Guides, directories, and trusted external links across the areas CPI partners serve.</p>
  </div>
</section>
<section class="light-page">
  <div class="container">
    <div class="category-pill-grid mt-16" id="resource-categories" style="margin-bottom:28px">
      <button class="category-pill is-active" data-cat="all">All</button>
      {''.join(f'<button class="category-pill" data-cat="{esc(c)}">{esc(c)}</button>' for c in RESOURCE_CATEGORIES)}
    </div>
    <div class="card-grid cols-3" id="resource-results">{cards}</div>
    <p class="empty-state" id="empty-state" hidden>No resources in this category yet.</p>
  </div>
</section>
"""
    return page(
        "Resources — CPI",
        "Trusted community resources across reentry, housing, employment, benefits, health, and more.",
        "/resources/", depth, body,
        extra_head=f'<script src="{rel_prefix(depth)}assets/js/resources.js" defer></script>',
    )


def build_about():
    depth = 0
    body = f"""
<section class="page-header">
  <div class="container">
    <span class="hero-eyebrow">About CPI</span>
    <h1>One Community. Connected.</h1>
    <p class="hero-sub">Strong organizations already exist. The missing layer is coordination.</p>
  </div>
</section>
<section class="light-page">
  <div class="container">
    <div class="two-col">
      <div class="stack">
        <div>
          <h2>Why CPI Exists</h2>
          <p class="mt-8">Fragmentation creates barriers. People navigating reentry, housing instability,
          or behavioral health crises are too often asked to find their own way between organizations
          that don't talk to each other. CPI exists to make the community's existing capabilities
          visible, trusted, navigable, and collaborative.</p>
        </div>
        <blockquote class="quote-block">{MISSION_STATEMENT}</blockquote>
      </div>
      <div>
        <h2>Our Model</h2>
        <div class="model-flow mt-16">
          <span class="node">Discover</span><span class="arrow">&rarr;</span>
          <span class="node">Connect</span><span class="arrow">&rarr;</span>
          <span class="node">Coordinate</span><span class="arrow">&rarr;</span>
          <span class="node">Measure</span><span class="arrow">&rarr;</span>
          <span class="node">Improve</span>
        </div>
        <h2 class="mt-32">Founding Thesis</h2>
        <p class="mt-8">The community already contains extraordinary organizations. CPI exists to
        make them easier to find, trust, and work with.</p>
        <h2 class="mt-32">Operating Principle</h2>
        <p class="mt-8">A referral is not an outcome. A connection is complete only when another
        organization accepts the handoff.</p>
      </div>
    </div>
  </div>
</section>
<section class="section-surface">
  <div class="container">
    <div class="cta-section">
      <h2>Community works better when we work together.</h2>
      <p>Whether you lead an organization, fund community work, or want to volunteer &mdash;
      there's a place for you in the CPI network.</p>
      <div class="hero-ctas">
        <a class="btn btn-primary" href="join.html">Join CPI</a>
        <a class="btn btn-secondary" href="donate.html">Give Now</a>
      </div>
    </div>
  </div>
</section>
"""
    return page(
        "About — Community Partners Initiatives",
        "Why CPI exists, our coordination model, and our founding thesis: the community already contains extraordinary organizations.",
        "/about.html", depth, body,
    )


def build_get_involved():
    depth = 0
    identities = [
        ("Organization", "join.html", "Bring your programs into the network and start receiving warm referrals."),
        ("Employer", "join.html?as=employer", "Join the Fair-Chance Employer Network and hire from our workforce pipeline."),
        ("Funder", "donate.html", "See what initiatives need funding and how CPI reports on outcomes."),
        ("Volunteer", "join.html?as=volunteer", "Offer time, transportation, mentorship, or specific skills."),
        ("Community Member", "find-support.html", "Find the support you need right now."),
        ("Professional", "join.html?as=professional", "Offer pro-bono legal, clinical, or advisory expertise."),
        ("Government / Institution", "contact.html", "Explore how your agency can plug into the CPI network."),
    ]
    cards = "".join(f"""
<a class="pillar-card" href="{path}">
  <h3>{label}</h3>
  <p>{desc}</p>
</a>""" for label, path, desc in identities)
    body = f"""
<section class="page-header">
  <div class="container">
    <span class="hero-eyebrow">Get Involved</span>
    <h1>What Can You Help With Right Now?</h1>
    <p class="hero-sub">Choose the option that best describes you and we'll point you to the right next step.</p>
  </div>
</section>
<section class="light-page">
  <div class="container">
    <div class="pillar-grid" style="grid-template-columns:repeat(auto-fit,minmax(220px,1fr))">{cards}</div>
  </div>
</section>
"""
    return page(
        "Get Involved — CPI",
        "Organizations, employers, funders, volunteers, and community members can all find their next step with CPI.",
        "/get-involved.html", depth, body,
    )


def build_join():
    depth = 0
    steps = [
        "Organization",
        "Services",
        "Population",
        "Geography",
        "Participation",
        "Review",
    ]
    dots = "".join(f'<div class="wizard-step-dot" data-step-dot="{idx}">{idx+1}. {label}</div>' for idx, label in enumerate(steps))
    participation_options = [
        "Receive referrals", "Send referrals", "Join initiatives", "Offer services",
        "Hire participants", "Provide funding", "Provide facilities", "Volunteer", "Other",
    ]
    body = f"""
<section class="page-header">
  <div class="container">
    <span class="hero-eyebrow">Join CPI</span>
    <h1>Join the CPI Network</h1>
    <p class="hero-sub">CPI brings community organizations together around shared needs, shared infrastructure, and real collaboration.</p>
  </div>
</section>
<section class="light-page">
  <div class="container">
    <div class="wizard">
      <div class="wizard-steps">{dots}</div>
      <form id="join-form" novalidate>
        <div class="wizard-panel is-active" data-panel="0">
          <div class="form-grid">
            <div class="field"><label for="org-name">Organization Name *</label><input type="text" id="org-name" name="org_name" required><span class="error-text">Please enter your organization's name.</span></div>
            <div class="field"><label for="org-website">Website</label><input type="url" id="org-website" name="website" placeholder="https://"></div>
            <div class="field"><label for="contact-name">Primary Contact *</label><input type="text" id="contact-name" name="contact_name" required><span class="error-text">Please enter a primary contact.</span></div>
            <div class="field"><label for="contact-email">Email *</label><input type="email" id="contact-email" name="email" required><span class="error-text">Please enter a valid email.</span></div>
            <div class="field"><label for="contact-phone">Phone</label><input type="tel" id="contact-phone" name="phone"></div>
          </div>
        </div>
        <div class="wizard-panel" data-panel="1">
          <div class="field"><label for="services">What services do you provide? *</label>
          <textarea id="services" name="services" required placeholder="e.g. transitional housing, job training, behavioral health counseling"></textarea>
          <span class="error-text">Please describe your services.</span></div>
        </div>
        <div class="wizard-panel" data-panel="2">
          <div class="field"><label for="population">Who do you serve? *</label>
          <textarea id="population" name="population" required placeholder="e.g. justice-impacted adults, families, youth"></textarea>
          <span class="error-text">Please describe who you serve.</span></div>
        </div>
        <div class="wizard-panel" data-panel="3">
          <div class="field"><label for="geography">Where do you operate? *</label>
          <textarea id="geography" name="geography" required placeholder="Cities, neighborhoods, or service area"></textarea>
          <span class="error-text">Please describe your service area.</span></div>
        </div>
        <div class="wizard-panel" data-panel="4">
          <div class="field">
            <label>How would you like to participate? *</label>
            <div class="checkbox-grid">
              {''.join(f'<label class="checkbox-tile"><input type="checkbox" name="participation" value="{o}">{o}</label>' for o in participation_options)}
            </div>
            <span class="error-text" id="participation-error">Please select at least one option.</span>
          </div>
        </div>
        <div class="wizard-panel" data-panel="5">
          <h2 style="font-size:1.1rem">Review &amp; Submit</h2>
          <div id="review-summary" class="stack mt-16"></div>
        </div>
        <div class="wizard-panel" data-panel="confirmation">
          <div class="confirmation-panel">
            <h2>Thank you for joining the CPI network.</h2>
            <p class="mt-16">Our team will review your organization and contact you regarding
            verification and next steps. If your email client doesn't open automatically,
            use the button below to send your application.</p>
            <div class="confirmation-id" id="application-id"></div>
            <div class="hero-ctas text-center mt-24" style="justify-content:center">
              <a class="btn btn-primary" id="email-application-btn" href="#">Email My Application</a>
              <a class="btn btn-secondary" href="{rel_prefix(depth)}index.html">Return Home</a>
            </div>
          </div>
        </div>
        <div class="wizard-actions" data-wizard-actions>
          <button type="button" class="btn btn-secondary" data-wizard-back disabled>Back</button>
          <button type="button" class="btn btn-primary" data-wizard-next>Continue</button>
          <button type="submit" class="btn btn-primary" data-wizard-submit hidden>Submit Partner Application</button>
        </div>
      </form>
    </div>
  </div>
</section>
"""
    return page(
        "Join the CPI Network — Partner Application",
        "Apply to join Community Partners Initiatives as a verified partner organization.",
        "/join.html", depth, body,
        extra_head=f'<script src="{rel_prefix(depth)}assets/js/join.js" defer></script>',
    )


def build_donate():
    depth = 0
    body = f"""
<section class="page-header">
  <div class="container">
    <span class="hero-eyebrow">Give to CPI</span>
    <h1>Fund the Connective Infrastructure</h1>
    <p class="hero-sub">Every gift helps CPI keep the network open, verified, and moving &mdash;
    so the organizations doing the work can reach the people who need them.</p>
  </div>
</section>
<section class="light-page">
  <div class="container">
    <div class="two-col">
      <div>
        <blockquote class="quote-block">{MISSION_STATEMENT}</blockquote>
        <h2 class="mt-32">Where Your Gift Goes</h2>
        <div class="impact-tier-grid mt-16">
          <div class="impact-tier"><div class="amount">$50</div><p>Covers a warm-handoff coordination call between two partner organizations.</p></div>
          <div class="impact-tier"><div class="amount">$250</div><p>Funds transportation support for one initiative for a month.</p></div>
          <div class="impact-tier"><div class="amount">$1,000</div><p>Supports partner verification and onboarding for a new organization.</p></div>
        </div>
        <div class="trust-badge-row">
          <span class="trust-badge">&#128274; Secure processing</span>
          <span class="trust-badge">&#128202; Transparent reporting</span>
          <span class="trust-badge">&#127970; Fiscally sponsored nonprofit</span>
        </div>
      </div>
      <div>
        <div class="donate-embed-slot">
          <h3>Online Giving</h3>
          <p class="mt-8">Our online donation processor is being connected. Once live, a
          one-time or recurring giving form will render directly on this page &mdash; no
          redirect required.</p>
          <p class="mt-8" style="font-size:0.85rem">Admin note: drop your Donorbox, Give
          Lively, or PayPal Giving embed snippet into
          <code>/donate.html</code> in place of this slot.</p>
        </div>
        <div class="sidebar-card mt-24">
          <h3>Give Another Way</h3>
          <p class="mt-8" style="color:var(--color-muted);font-size:0.92rem">
          Prefer to give by check, wire, or donor-advised fund? Reach our team directly and
          we'll take care of the rest.</p>
          <a class="btn btn-primary btn-block mt-16" href="mailto:give@cpinitiatives.org?subject=CPI%20Donation%20Inquiry">Contact Us to Give</a>
        </div>
      </div>
    </div>
  </div>
</section>
"""
    return page(
        "Donate — Community Partners Initiatives",
        "Support the connective infrastructure between community organizations working on housing, workforce, health, and reentry.",
        "/donate.html", depth, body,
    )


def build_contact():
    depth = 0
    body = f"""
<section class="page-header">
  <div class="container">
    <span class="hero-eyebrow">Contact</span>
    <h1>Get in Touch</h1>
    <p class="hero-sub">Questions about partnering, initiatives, or funding? Reach the CPI team directly.</p>
  </div>
</section>
<section class="light-page">
  <div class="container">
    <div class="two-col">
      <div class="contact-card">
        <h2>General Inquiries</h2>
        <p class="mt-8">For partnership, media, or general questions.</p>
        <a class="btn btn-primary mt-16" href="mailto:hello@cpinitiatives.org">hello@cpinitiatives.org</a>
      </div>
      <div class="contact-card">
        <h2>Giving &amp; Funding</h2>
        <p class="mt-8">For donors, foundations, and institutional partners.</p>
        <a class="btn btn-primary mt-16" href="mailto:give@cpinitiatives.org">give@cpinitiatives.org</a>
      </div>
    </div>
  </div>
</section>
"""
    return page(
        "Contact — CPI",
        "Reach the Community Partners Initiatives team for partnerships, media, or giving.",
        "/contact.html", depth, body,
    )


def build_portal_placeholder():
    depth = 0
    body = f"""
<section class="page-header">
  <div class="container">
    <span class="hero-eyebrow">Partner Portal</span>
    <h1>Partner Portal</h1>
    <p class="hero-sub">The partner portal &mdash; profile management, referral status, capacity
    updates, and initiative workspaces &mdash; is on our roadmap. Verified partners will be
    invited directly once it launches.</p>
    <div class="hero-ctas">
      <a class="btn btn-primary" href="join.html">Join CPI to Get Early Access</a>
    </div>
  </div>
</section>
"""
    return page(
        "Partner Portal — CPI",
        "The CPI partner portal is coming soon.",
        "/portal.html", depth, body,
    )


def build_404():
    depth = 0
    body = f"""
<section class="page-header text-center">
  <div class="container">
    <span class="hero-eyebrow">404</span>
    <h1>Page Not Found</h1>
    <p class="hero-sub" style="margin-left:auto;margin-right:auto">The page you're looking for
    may have moved. Try the homepage or search our partner directory.</p>
    <div class="hero-ctas" style="justify-content:center">
      <a class="btn btn-primary" href="/">Return Home</a>
      <a class="btn btn-secondary" href="/partners/">Browse Partners</a>
    </div>
  </div>
</section>
"""
    return page("Page Not Found — CPI", "Page not found.", "/404.html", depth, body)


# --------------------------------------------------------------------------
# JS assets (data + interactivity)
# --------------------------------------------------------------------------

MAIN_JS = """
document.addEventListener('DOMContentLoaded', function () {
  var toggle = document.querySelector('[data-nav-toggle]');
  var menu = document.querySelector('[data-mobile-menu]');
  if (toggle && menu) {
    toggle.addEventListener('click', function () {
      var isOpen = menu.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
      document.body.style.overflow = isOpen ? 'hidden' : '';
    });
    menu.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () {
        menu.classList.remove('is-open');
        toggle.setAttribute('aria-expanded', 'false');
        document.body.style.overflow = '';
      });
    });
  }
  document.querySelectorAll('[data-year]').forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });
});
""".strip()


def build_filter_js(kind):
    """Generic client-side search/filter script shared by listing pages."""
    if kind == "partners":
        return """
document.addEventListener('DOMContentLoaded', function () {
  var searchInput = document.getElementById('partner-search');
  var catSelect = document.getElementById('filter-category');
  var locSelect = document.getElementById('filter-location');
  var cards = Array.prototype.slice.call(document.querySelectorAll('#partner-results .partner-card'));
  var countEl = document.getElementById('results-count');
  var emptyEl = document.getElementById('empty-state');

  function apply() {
    var q = (searchInput && searchInput.value || '').toLowerCase().trim();
    var cat = catSelect ? catSelect.value : 'all';
    var loc = locSelect ? locSelect.value : 'all';
    var visible = 0;
    cards.forEach(function (card) {
      var name = card.getAttribute('data-name') || '';
      var cats = (card.getAttribute('data-categories') || '').split(',');
      var locs = (card.getAttribute('data-locations') || '').split(',');
      var matchesQ = !q || name.indexOf(q) !== -1;
      var matchesCat = cat === 'all' || cats.indexOf(cat) !== -1;
      var matchesLoc = loc === 'all' || locs.indexOf(loc) !== -1;
      var show = matchesQ && matchesCat && matchesLoc;
      card.hidden = !show;
      if (show) visible++;
    });
    if (countEl) countEl.textContent = visible + (visible === 1 ? ' organization found' : ' organizations found');
    if (emptyEl) emptyEl.hidden = visible !== 0;
  }

  [searchInput, catSelect, locSelect].forEach(function (el) {
    if (el) el.addEventListener('input', apply);
  });

  var params = new URLSearchParams(window.location.search);
  if (params.get('category') && catSelect) catSelect.value = params.get('category');
  apply();
});
""".strip()
    if kind == "find-support":
        return """
document.addEventListener('DOMContentLoaded', function () {
  var searchInput = document.getElementById('partner-search');
  var chips = Array.prototype.slice.call(document.querySelectorAll('#category-chips .chip'));
  var cards = Array.prototype.slice.call(document.querySelectorAll('#partner-results .partner-card'));
  var countEl = document.getElementById('results-count');
  var emptyEl = document.getElementById('empty-state');
  var activeCat = 'all';

  function apply() {
    var q = (searchInput && searchInput.value || '').toLowerCase().trim();
    var visible = 0;
    cards.forEach(function (card) {
      var name = card.getAttribute('data-name') || '';
      var cats = (card.getAttribute('data-categories') || '').split(',');
      var matchesQ = !q || name.indexOf(q) !== -1;
      var matchesCat = activeCat === 'all' || cats.indexOf(activeCat) !== -1;
      var show = matchesQ && matchesCat;
      card.hidden = !show;
      if (show) visible++;
    });
    if (countEl) countEl.textContent = visible + (visible === 1 ? ' organization found' : ' organizations found');
    if (emptyEl) emptyEl.hidden = visible !== 0;
  }

  chips.forEach(function (chip) {
    chip.addEventListener('click', function () {
      chips.forEach(function (c) { c.setAttribute('aria-pressed', 'false'); });
      chip.setAttribute('aria-pressed', 'true');
      activeCat = chip.getAttribute('data-cat');
      apply();
    });
  });
  if (searchInput) searchInput.addEventListener('input', apply);

  var params = new URLSearchParams(window.location.search);
  if (params.get('q') && searchInput) searchInput.value = params.get('q');
  var wantedCat = params.get('category');
  if (wantedCat) {
    var match = chips.filter(function (c) { return c.getAttribute('data-cat') === wantedCat; })[0];
    if (match) match.click();
  }
  apply();
});
""".strip()
    if kind == "initiatives":
        return """
document.addEventListener('DOMContentLoaded', function () {
  var catSelect = document.getElementById('filter-category');
  var statusSelect = document.getElementById('filter-status');
  var cards = Array.prototype.slice.call(document.querySelectorAll('#initiative-results .initiative-card'));
  var countEl = document.getElementById('results-count');
  var emptyEl = document.getElementById('empty-state');

  function apply() {
    var cat = catSelect ? catSelect.value : 'all';
    var status = statusSelect ? statusSelect.value : 'all';
    var visible = 0;
    cards.forEach(function (card) {
      var matchesCat = cat === 'all' || card.getAttribute('data-category') === cat;
      var matchesStatus = status === 'all' || card.getAttribute('data-status') === status;
      var show = matchesCat && matchesStatus;
      card.hidden = !show;
      if (show) visible++;
    });
    if (countEl) countEl.textContent = visible + (visible === 1 ? ' initiative found' : ' initiatives found');
    if (emptyEl) emptyEl.hidden = visible !== 0;
  }

  [catSelect, statusSelect].forEach(function (el) {
    if (el) el.addEventListener('change', apply);
  });
  apply();
});
""".strip()
    if kind == "needs":
        return """
document.addEventListener('DOMContentLoaded', function () {
  var supportSelect = document.getElementById('filter-support');
  var cards = Array.prototype.slice.call(document.querySelectorAll('#need-results .need-card'));
  var countEl = document.getElementById('results-count');
  var emptyEl = document.getElementById('empty-state');

  function apply() {
    var support = supportSelect ? supportSelect.value : 'all';
    var visible = 0;
    cards.forEach(function (card) {
      var show = support === 'all' || card.getAttribute('data-support') === support;
      card.hidden = !show;
      if (show) visible++;
    });
    if (countEl) countEl.textContent = visible + (visible === 1 ? ' open need' : ' open needs');
    if (emptyEl) emptyEl.hidden = visible !== 0;
  }

  if (supportSelect) supportSelect.addEventListener('change', apply);
  apply();
});
""".strip()
    if kind == "resources":
        return """
document.addEventListener('DOMContentLoaded', function () {
  var pills = Array.prototype.slice.call(document.querySelectorAll('#resource-categories .category-pill'));
  var cards = Array.prototype.slice.call(document.querySelectorAll('#resource-results .resource-card'));
  var emptyEl = document.getElementById('empty-state');

  function apply(cat) {
    var visible = 0;
    cards.forEach(function (card) {
      var show = cat === 'all' || card.getAttribute('data-category') === cat;
      card.hidden = !show;
      if (show) visible++;
    });
    if (emptyEl) emptyEl.hidden = visible !== 0;
  }

  pills.forEach(function (pill) {
    pill.addEventListener('click', function () {
      pills.forEach(function (p) { p.classList.remove('is-active'); });
      pill.classList.add('is-active');
      apply(pill.getAttribute('data-cat'));
    });
  });
  apply('all');
});
""".strip()
    raise ValueError(kind)


JOIN_JS = """
document.addEventListener('DOMContentLoaded', function () {
  var form = document.getElementById('join-form');
  if (!form) return;
  var panels = Array.prototype.slice.call(form.querySelectorAll('.wizard-panel[data-panel]'));
  var dots = Array.prototype.slice.call(document.querySelectorAll('[data-step-dot]'));
  var backBtn = document.querySelector('[data-wizard-back]');
  var nextBtn = document.querySelector('[data-wizard-next]');
  var submitBtn = document.querySelector('[data-wizard-submit]');
  var actions = document.querySelector('[data-wizard-actions]');
  var totalSteps = dots.length; // 0..totalSteps-1 are form steps
  var current = 0;

  function panelFor(index) {
    return panels.filter(function (p) { return p.getAttribute('data-panel') === String(index); })[0];
  }

  function showStep(index) {
    panels.forEach(function (p) { p.classList.remove('is-active'); });
    var panel = panelFor(index);
    if (panel) panel.classList.add('is-active');
    dots.forEach(function (dot, i) {
      dot.classList.toggle('is-active', i === index);
      dot.classList.toggle('is-done', i < index);
    });
    backBtn.disabled = index === 0;
    nextBtn.hidden = index === totalSteps - 1;
    submitBtn.hidden = index !== totalSteps - 1;
    if (index === totalSteps - 1) renderReview();
  }

  function fieldsInStep(index) {
    var panel = panelFor(index);
    return panel ? Array.prototype.slice.call(panel.querySelectorAll('input, textarea')) : [];
  }

  function validateStep(index) {
    var valid = true;
    if (index === 4) {
      var checked = form.querySelectorAll('input[name="participation"]:checked');
      var err = document.getElementById('participation-error');
      if (checked.length === 0) {
        valid = false;
        if (err) err.style.display = 'block';
      } else if (err) {
        err.style.display = 'none';
      }
      return valid;
    }
    fieldsInStep(index).forEach(function (field) {
      var wrapper = field.closest('.field');
      if (field.hasAttribute('required') && !field.value.trim()) {
        valid = false;
        if (wrapper) wrapper.classList.add('has-error');
      } else if (wrapper) {
        wrapper.classList.remove('has-error');
      }
    });
    return valid;
  }

  function renderReview() {
    var summary = document.getElementById('review-summary');
    if (!summary) return;
    var data = collectData();
    var rows = [
      ['Organization', data.org_name],
      ['Website', data.website || '—'],
      ['Contact', data.contact_name + ' (' + data.email + ')'],
      ['Services', data.services],
      ['Population Served', data.population],
      ['Geography', data.geography],
      ['Participation', data.participation.join(', ')],
    ];
    summary.innerHTML = rows.map(function (r) {
      return '<div class="kv-row"><span class="k">' + r[0] + '</span><span class="v">' + escapeHtml(r[1]) + '</span></div>';
    }).join('');
  }

  function escapeHtml(str) {
    var div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  function collectData() {
    var fd = new FormData(form);
    return {
      org_name: fd.get('org_name') || '',
      website: fd.get('website') || '',
      contact_name: fd.get('contact_name') || '',
      email: fd.get('email') || '',
      phone: fd.get('phone') || '',
      services: fd.get('services') || '',
      population: fd.get('population') || '',
      geography: fd.get('geography') || '',
      participation: fd.getAll('participation'),
    };
  }

  nextBtn.addEventListener('click', function () {
    if (!validateStep(current)) return;
    current = Math.min(current + 1, totalSteps - 1);
    showStep(current);
  });
  backBtn.addEventListener('click', function () {
    current = Math.max(current - 1, 0);
    showStep(current);
  });

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (!validateStep(current)) return;
    var data = collectData();
    var appId = 'CPI-APP-' + new Date().getFullYear() + '-' + Math.floor(1000 + Math.random() * 9000);
    var idEl = document.getElementById('application-id');
    if (idEl) idEl.textContent = appId;

    var bodyLines = [
      'New CPI Partner Application (' + appId + ')',
      '',
      'Organization: ' + data.org_name,
      'Website: ' + data.website,
      'Contact: ' + data.contact_name,
      'Email: ' + data.email,
      'Phone: ' + data.phone,
      'Services: ' + data.services,
      'Population Served: ' + data.population,
      'Geography: ' + data.geography,
      'Participation: ' + data.participation.join(', '),
    ];
    var mailto = 'mailto:partners@cpinitiatives.org?subject=' +
      encodeURIComponent('CPI Partner Application - ' + data.org_name) +
      '&body=' + encodeURIComponent(bodyLines.join('\\n'));
    var emailBtn = document.getElementById('email-application-btn');
    if (emailBtn) emailBtn.setAttribute('href', mailto);

    panels.forEach(function (p) { p.classList.remove('is-active'); });
    panelFor('confirmation').classList.add('is-active');
    if (actions) actions.hidden = true;
    window.scrollTo({ top: 0, behavior: 'smooth' });
    window.location.href = mailto;
  });

  showStep(0);
});
""".strip()


def write(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    write("index.html", build_home())
    write("find-support.html", build_find_support())
    write("about.html", build_about())
    write("get-involved.html", build_get_involved())
    write("join.html", build_join())
    write("donate.html", build_donate())
    write("contact.html", build_contact())
    write("portal.html", build_portal_placeholder())
    write("404.html", build_404())

    write("partners/index.html", build_partners_index())
    for p_ in PARTNERS:
        write(f"partners/{p_['slug']}/index.html", build_partner_detail(p_))

    write("initiatives/index.html", build_initiatives_index())
    for i in INITIATIVES:
        write(f"initiatives/{i['slug']}/index.html", build_initiative_detail(i))

    write("needs/index.html", build_needs_index())
    write("resources/index.html", build_resources_index())

    write("assets/js/main.js", MAIN_JS)
    write("assets/js/find-support.js", build_filter_js("find-support"))
    write("assets/js/partners.js", build_filter_js("partners"))
    write("assets/js/initiatives.js", build_filter_js("initiatives"))
    write("assets/js/needs.js", build_filter_js("needs"))
    write("assets/js/resources.js", build_filter_js("resources"))
    write("assets/js/join.js", JOIN_JS)

    write("CNAME", "cpinitiatives.org\n")
    write("robots.txt", "User-agent: *\nAllow: /\nSitemap: https://cpinitiatives.org/sitemap.xml\n")

    urls = ["/", "/find-support.html", "/about.html", "/partners/", "/initiatives/",
            "/needs/", "/resources/", "/get-involved.html", "/join.html", "/donate.html",
            "/contact.html"]
    urls += [f"/partners/{p_['slug']}/" for p_ in PARTNERS]
    urls += [f"/initiatives/{i['slug']}/" for i in INITIATIVES]
    sitemap_items = "".join(f"<url><loc>{SITE_URL}{u}</loc></url>" for u in urls)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sitemap_items}</urlset>\n')

    print("Build complete.")


if __name__ == "__main__":
    main()
