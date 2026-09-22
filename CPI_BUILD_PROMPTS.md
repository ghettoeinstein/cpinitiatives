# CPI Website Build Prompts

> **Hosting constraint:** cpinitiatives.org must remain deployable on free GitHub Pages. The production implementation must be static HTML/CSS/vanilla JS (or a static-exported Astro build), with no required server, database, API, authentication, server actions, or paid hosting. Forms must use a hosted/free form endpoint or mailto fallback. Supabase/Next.js ideas below are future architecture only and must not block the free static launch.

These prompts are sequenced to build the launch slice first, then the rest of the MVP. The current repository is a static HTML site. If migrating later, use Astro static output rather than a server-rendered Next.js deployment.

## Prompt 1 — Foundation & design system

Scaffold a Next.js 14 App Router + TypeScript + Tailwind CSS project for cpinitiatives.org, a community-partner network platform. Add a Supabase client and Postgres schema.

Use design tokens: white #FFFFFF, CPI Blue #0969DA, black #090B0D, neutrals #F5F7FA, #E7ECF2, #68707A. Use Inter or Geist. Voice is plain-language, community-first, confident, collaborative, and never bureaucratic or clinical. Use subtle hover elevation, clean blue focus rings, soft card movement, fast navigation, and no parallax, gradients, glassmorphism, or floating particles.

Create tables for organizations, organization_services, organization_locations, partner_applications, initiatives, initiative_partners, initiative_needs, resources, categories, and service_categories. Include organization verification states Applicant, Under Review, Verified, Temporarily Unavailable, Inactive, Suspended; initiative states OPEN, FORMING, ACTIVE, FUNDED, DELIVERING, COMPLETED. Do not store referrals, case notes, participant personal data, or health data in v1.

Build shared Navbar, Footer, Button, and stub components: SectionHeading, PartnerCard, InitiativeCard, NeedCard, ResourceCard, ServiceChip, StatusBadge, VerificationBadge, Metric, CTASection, SearchBar, FilterDrawer, ApplicationWizard.

## Prompt 2 — Homepage

Build the homepage in this order:

1. Hero: “Connecting People. Uniting Partners. Creating Opportunity.” with CPI description, primary CTA “Join as a Community Partner” → /join, secondary “Explore Current Initiatives” → /initiatives, tertiary “Find Support →”.
2. Four clickable service pillars: Housing Stability; Workforce & Economic Mobility; Health & Wellness; Whole-Person Support.
3. Find Support module with need and location/ZIP inputs, category chips, and “Find Partners”. No account required.
4. Partner Network preview with PartnerCards and CTAs to /partners and /join.
5. Active Initiatives preview with 3 InitiativeCards.
6. Current Community Needs preview linking to /needs.
7. How CPI Works: Organizations → Verified Partners → Visible Services → Shared Initiatives → Warm Connections → Measurable Outcomes.
8. Early-stage activity statement: “Building the founding CPI network.” Do not fabricate metrics.
9. Join CTA: “Your organization should not have to solve everything alone.”
10. Footer.

Use clearly marked placeholder data and comment that it must be replaced before launch.

## Prompt 3 — Partners

Build /partners and /partners/[slug]. The directory needs search and filters for Service, Location, Population served, Referral status, Languages, and Accessibility. PartnerCards show logo, name, services, areas served, Accepting Referrals, Verified CPI Partner, and View Organization.

Partner detail pages include identity, mission, description, services, locations, populations, eligibility, referral information, languages, hours, contact, website, active initiatives, verification badge, and last verified date. Include Visit Organization, Request Connection, and View Services actions.

Seed six clearly labeled placeholder organizations across Compton, South LA, Gardena, and Long Beach.

## Prompt 4 — Initiatives

Build /initiatives and /initiatives/[slug]. Directory copy: “The community has needs right now. See what organizations are building, what resources are missing, and where you can help.” Add filters for Category, Location, Status, and support type: Partner, Volunteers, Funding, Employer, Housing, Facility, Transportation, Professional Services, Supplies Needed. Status must always include an icon and text, never color alone.

Detail layout: Initiative → Problem → Goal → Current Partners → What We Need → Timeline → Progress → Join Initiative. “I Can Help” opens identity picker: Organization, Funder, Volunteer, Employer, Service Provider, Other.

Seed: Transitional Housing Expansion; Fair-Chance Employer Network; Mobile Behavioral Health Access.

## Prompt 5 — Join CPI

Build /join with headline “Join the CPI Network.” and copy: “CPI brings community organizations together around shared needs, shared infrastructure, and real collaboration.”

Create a five-step ApplicationWizard:
1. Organization, Website, Primary contact, Email, Phone
2. Services provided
3. Populations served
4. Areas of operation
5. Participation choices: Receive referrals, Send referrals, Join initiatives, Offer services, Hire participants, Provide funding, Provide facilities, Volunteer, Other

Submit to partner_applications with status Applicant. Show confirmation, application ID such as CPI-APP-2026-0048, and stub a Partner Application Received email trigger.

## Prompt 6 — Needs board

Build /needs, viewable without an account. NeedCards show title, category, quantity, location, linked initiative, and status. Add category/status filters. Seed five needs:

- 10 laptops needed for workforce cohort
- Housing partner needed for 4 transitional placements
- Employer seeking partnership with fair-chance training provider
- Volunteer transportation requested for weekly appointments
- Clinical organization needed for behavioral health initiative

## Prompt 7 — Public pages

Build /about, /resources, /get-involved, and /contact.

About: Why CPI Exists (“Fragmentation creates barriers.”), Discover → Connect → Coordinate → Measure → Improve, founding thesis that the community already contains extraordinary organizations, and the principle “A referral is not an outcome. A connection is complete only when another organization accepts the handoff.”

Resources: categories Reentry, Housing, Employment, Benefits, Health, Behavioral Health, Education, Transportation, Legal, Financial Literacy, Family Support. Support guides, directories, PDFs, partner materials, and public agency links.

Get Involved: route Organization, Employer, Funder, Volunteer, Community Member, Professional, and Government/Institution to the right action.

Contact: simple accessible form.

## Prompt 8 — Admin

Build restricted /admin, auth-gated to CPI administrators only. Dashboard sections: Applications, Partners, Initiatives, Needs, Resources, Messages. Support Review, Approve, Publish, Update, and Archive.

Support partner review and promotion through Applicant → Under Review → Verified or Temporarily Unavailable/Inactive/Suspended; manage partners, initiatives, initiative partners, initiative needs, resources, and moderation. Stub Partner Approved, Partner Needs More Information, and Quarterly Partner Verification Request emails.

Use RBAC, Supabase Auth admin role claims, rate-limited and validated forms, secure headers, CSRF protection where applicable, verification audit trails, and minimal PII.

## Prompt 9 — Search, SEO, accessibility, performance

Add global search over organizations, services, initiatives, needs, and resources. A query like “housing Compton” returns grouped counts. Support city, ZIP, county, and service-area search without hardcoding Los Angeles into the schema.

Add metadata, canonical URLs, Open Graph, JSON-LD for Organization/NonprofitOrganization/LocalBusiness/Service, and indexable partner/initiative pages.

Target WCAG 2.2 AA: keyboard navigation, semantic HTML, visible focus, strong contrast, screen-reader labels, 44px touch targets, accessible errors, and reduced-motion support.

Target LCP < 2.5s, CLS < 0.1, INP < 200ms. Track partner profile views, application starts/completions, initiative views, interest submissions, resource clicks, service searches, and need responses without retaining sensitive, person-identifiable search histories.

## Product doctrine

Optimize for connection over traffic, completion over referral, trust over volume, clarity over bureaucracy, coordination over ownership, and community capacity over platform dependency.

The first vertical slice is Homepage → Partner Directory → Initiative → Join CPI. The public promise is: Find help. Find partners. Build together.
