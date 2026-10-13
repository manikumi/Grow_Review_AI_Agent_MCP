---
name: Obsidian Pulse & Intelligence
colors:
  surface: '#0f131d'
  surface-dim: '#0f131d'
  surface-bright: '#353944'
  surface-container-lowest: '#0a0e18'
  surface-container-low: '#171b26'
  surface-container: '#1c1f2a'
  surface-container-high: '#262a35'
  surface-container-highest: '#313540'
  on-surface: '#dfe2f1'
  on-surface-variant: '#bbcabf'
  inverse-surface: '#dfe2f1'
  inverse-on-surface: '#2c303b'
  outline: '#86948a'
  outline-variant: '#3c4a42'
  surface-tint: '#4edea3'
  primary: '#4edea3'
  on-primary: '#003824'
  primary-container: '#10b981'
  on-primary-container: '#00422b'
  inverse-primary: '#006c49'
  secondary: '#4cd7f6'
  on-secondary: '#003640'
  secondary-container: '#03b5d3'
  on-secondary-container: '#00424e'
  tertiary: '#d0bcff'
  on-tertiary: '#3c0091'
  tertiary-container: '#b090ff'
  on-tertiary-container: '#4600a7'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#6ffbbe'
  primary-fixed-dim: '#4edea3'
  on-primary-fixed: '#002113'
  on-primary-fixed-variant: '#005236'
  secondary-fixed: '#acedff'
  secondary-fixed-dim: '#4cd7f6'
  on-secondary-fixed: '#001f26'
  on-secondary-fixed-variant: '#004e5c'
  tertiary-fixed: '#e9ddff'
  tertiary-fixed-dim: '#d0bcff'
  on-tertiary-fixed: '#23005c'
  on-tertiary-fixed-variant: '#5516be'
  background: '#0f131d'
  on-background: '#dfe2f1'
  surface-variant: '#313540'
typography:
  headline-xl:
    fontFamily: Geist
    fontSize: 40px
    fontWeight: '600'
    lineHeight: 48px
    letterSpacing: -0.03em
  headline-xl-mobile:
    fontFamily: Geist
    fontSize: 30px
    fontWeight: '600'
    lineHeight: 36px
    letterSpacing: -0.025em
  headline-lg:
    fontFamily: Geist
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.025em
  headline-lg-mobile:
    fontFamily: Geist
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Geist
    fontSize: 24px
    fontWeight: '500'
    lineHeight: 32px
    letterSpacing: -0.02em
  headline-sm:
    fontFamily: Geist
    fontSize: 20px
    fontWeight: '500'
    lineHeight: 28px
    letterSpacing: -0.015em
  body-lg:
    fontFamily: Geist
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
    letterSpacing: -0.01em
  body-md:
    fontFamily: Geist
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
    letterSpacing: -0.005em
  body-sm:
    fontFamily: Geist
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
    letterSpacing: 0em
  metric-display:
    fontFamily: Geist
    fontSize: 36px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.03em
  label-lg:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 18px
    letterSpacing: 0.02em
  label-md:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.03em
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 10px
    fontWeight: '500'
    lineHeight: 14px
    letterSpacing: 0.04em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1.25rem
  gutter-sm: 0.75rem
  gutter-lg: 1.5rem
  margin: 2rem
  margin-mobile: 1rem
  margin-desktop: 2.5rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2rem
---

## Brand & Style

This design system expresses high-conviction fintech intelligence through an analytical, institutional dark aesthetic. The experience combines the precision of high-frequency trading terminals with the clarity of executive review briefs. 

### Visual Archetype & Mood
- **Style Direction:** Modern Technical Glassmorphism layered over structured Obsidian surfaces.
- **Tone:** Authoritative, razor-sharp, analytical, and luminous under data focus.
- **Emotional Resonance:** Quiet confidence, rapid cognitive synthesis, and cryptographic clarity. Visual noise is aggressively eliminated in favor of metric salience, deliberate data hierarchies, and controlled chromatic energy.

## Colors

The chromatic structure relies on deep light-absorbing surfaces punctuated by surgical, highly saturated signals.

### Surface Architecture
- **Base Canvas (`#0B0F19`):** Pure obsidian baseline that anchors the entire interface.
- **Surface Elevation 1 (`#111827`):** Structural panels, side rails, and high-level section backing.
- **Surface Elevation 2 (`#1F2937`):** Metric cards, analytical modules, and executive card containers.
- **Surface Highlight (`#374151`):** Hover states, interactive row highlights, and tertiary chip backgrounds.

### Accents & Intelligence Roles
- **Primary Emerald (`#10B981` / `#059669`):** Growth indicators, verified metrics, primary system actions, positive yield, and foundational health signals.
- **Electric Cyan (`#06B6D4`):** Trend projections, algorithmic confidence indexes, streaming telemetry, and secondary metric comparisons.
- **Intelligence Violet (`#8B5CF6`):** Machine learning sentiment synthesis, qualitative intelligence summaries, and systemic review signals.
- **Muted Typography & Boundaries (`#9CA3AF`):** Secondary metrics, unit labels, timestamps, and descriptive synthesis copy. Crisp white (`#F9FAFB`) remains reserved for primary KPI values and critical headings.

## Typography

The typographic system utilizes a dual-engine architecture:
- **Geist** governs core semantic hierarchy, narrative digests, and executive analysis. Its mechanical neutrality provides uncolored data consumption.
- **JetBrains Mono** is reserved exclusively for tabular numeric streamings, metadata tags, metric differentials (deltas), and timestamps.

### Formatting Rules
- All numeric changes (`+12.4%`, `-$420.00M`) mandate `JetBrains Mono` with explicit tabular lining figures (`font-variant-numeric: tabular-nums`).
- Large metric figures deploy tight negative tracking (`letterSpacing: -0.03em`) to anchor numerical mass within cards.

## Layout & Spacing

A strictly disciplined 12-column fluid grid system engineered for intensive multidimensional data density.

### Breakpoints & Geometry
- **Desktop (≥ 1280px):** 12 columns, 24px gutters, 40px outer canvas margins. Multi-column metric matrix with persistent intelligence side-drawers.
- **Tablet (768px – 1279px):** 8 columns, 16px gutters, 24px outer margins. KPI cards collapse into 2x2 grids; secondary charts fold beneath main executive narratives.
- **Mobile (< 768px):** 4 columns, 12px gutters, 16px margins. Stacked single-column layouts with horizontal kinetic-scroll ribbons for pill chips and secondary KPI clusters.

### Density Protocol
Spacers strictly define whitespace, not boundary thickness. Critical executive summaries prioritize compact internal card padding (`space-lg`) paired with strict micro-gaps (`space-xs`, `space-sm`) between tags and labels to keep visual context immediately scannable above the fold.

## Elevation & Depth

Depth is constructed through optical transparency, dark tonal stratification, and targeted luminescent edging rather than traditional drop shadows.

### Elevation Hierarchy
1. **Canvas (Ground Layer):** Deep obsidian (`#0B0F19`) baseline. Zero elevation.
2. **Structural Panels (Tier 1):** `#111827` at 90% opacity with `backdrop-filter: blur(12px)`. Outlined by a microscopic hairline border: `1px solid rgba(255, 255, 255, 0.05)`.
3. **Elevated Intelligence Cards (Tier 2):** `#1F2937` at 75% opacity with `backdrop-filter: blur(16px)`. Bordered by high-precision micro-strokes: `1px solid rgba(255, 255, 255, 0.08)`. Elevated cards use ambient underglows keyed to their metric status (e.g., a subtle 24px blur shadow of `rgba(16, 185, 129, 0.06)` for top-tier positive growth cards).
4. **Modals & Flyouts (Tier 3):** `#1F2937` at 95% opacity with `backdrop-filter: blur(24px)`, framed with `1px solid #374151` and an ambient perimeter shadow: `0 20px 40px -15px rgba(0, 0, 0, 0.7)`.

## Shapes

The system relies on crisp, controlled radiuses balancing modern tech ergonomics with financial institutional solidity.

### Radius Application Matrix
- **Containers & Glass Cards:** 12px (`rounded-lg`) standard curvature, preserving boundary structure across high-density grid placements.
- **Interactive Buttons & Form Fields:** 8px (`rounded`) radius for precise, deliberate action zones.
- **Intelligence Chips, Status Tags, & Badges:** Full-pill geometry (`rounded-full` / `9999px`) to create strong shape contrast against rigid rectangular card environments.

## Components

### Buttons
- **Primary Metric Action:** Solid emerald background (`#10B981`) with rich dark contrast text (`#0B0F19`), font weight 600. Hover transitions to `#059669` with an emerald glow (`box-shadow: 0 0 16px rgba(16, 185, 129, 0.35)`).
- **Secondary Ghost:** Surface-backed (`rgba(255, 255, 255, 0.04)`), `1px solid rgba(255, 255, 255, 0.08)`, text `#F9FAFB`. Hover shifts border to `#374151` and background to `rgba(255, 255, 255, 0.08)`.

### Chips & Badges
- **Status Pills:** Pill-shaped, micro-padding (`4px 10px`), set in `label-sm` font.
  - *Growth/Bullish:* `rgba(16, 185, 129, 0.12)` background, `#10B981` text, `1px solid rgba(16, 185, 129, 0.25)`.
  - *Algorithmic Flow:* `rgba(6, 182, 212, 0.12)` background, `#06B6D4` text, `1px solid rgba(6, 182, 212, 0.25)`.
  - *Synthesis/Intelligence:* `rgba(139, 92, 246, 0.12)` background, `#8B5CF6` text, `1px solid rgba(139, 92, 246, 0.25)`.

### Cards (Glass Intelligence Cards)
- Background `#1F2937` at 70% opacity, `backdrop-filter: blur(16px)`, border `1px solid rgba(255, 255, 255, 0.08)`.
- Internal structure separates metadata header, primary quantitative metric (`metric-display`), and contextual micro-trendline.

### Lists & Data Rows
- Borderless rows resting over `#111827` or transparent backgrounds, separated by hairline dividers (`rgba(255, 255, 255, 0.04)`).
- Interactive rows transition background to `rgba(255, 255, 255, 0.03)` on hover, with a subtle left-edge accent indicator.

### Input Fields
- Fill `#0B0F19` with inset boundary `1px solid #374151`. Text `#F9FAFB`, placeholder `#9CA3AF`.
- Active focus state: border shifts to `#10B981` with an outer ring glow (`0 0 0 1px #10B981`).

### Selection Controls (Checkboxes & Radios)
- Unchecked: `#111827` surface with `1px solid #374151`.
- Checked: `#10B981` fill with `#0B0F19` checkmark icon.

### Domain-Specific: Executive Review Synthesis Module
- Specialized card container featuring an intelligent dual-gradient edge (`linear-gradient(135deg, rgba(6, 182, 212, 0.3), rgba(139, 92, 246, 0.3))`). Contains bulleted machine-synthesized executive takeaways with dynamic sentiment highlights.