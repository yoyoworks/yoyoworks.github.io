# YOYOworks Design System

## Purpose

This document defines the visual intent and component usage rules for every
YOYOworks page. Concrete colors, dimensions, spacing, radii, typography values,
shadows, transitions, and responsive values live exclusively in
`assets/theme.css`.

When documentation and CSS appear to disagree, `assets/theme.css` is the source
of truth for values. This document remains the source of truth for intent.

## Visual Direction

- Use a warm paper canvas with dark navy typography.
- Build depth with directional, overlapping geometric planes rather than
  gradients, bubbles, neon light, or technology grids.
- Let navy, blue, and teal carry most chromatic weight.
- Concentrate coral and gold into a small number of focal accents.
- Keep content-heavy areas flatter and quieter than Hero areas.
- Use transparency and blur only where they clarify layering, primarily the
  navigation, Hero, and modal surfaces.
- Preserve a content-first editorial character. Decoration must never compete
  with reading or controls.

## Typography

- Use the system-first font stack defined in `assets/theme.css`.
- Use weight and spacing for hierarchy; do not introduce a second display font.
- Use the shared type tokens and component classes instead of page-specific
  font sizes.
- Buttons and navigation use restrained medium or semibold weight.
- Long-form body copy uses a relaxed line height.
- Dates and compact statistics use tabular figures where alignment matters.

## Spacing and Shape

- Use only the shared spacing tokens.
- Use the control radius for ordinary buttons.
- Reserve pill geometry for language switching, tags, and truly compact
  selectors.
- Use the card radius for content groups and the panel radius for major Hero
  surfaces.
- Avoid introducing a new radius or shadow inside page-specific CSS.

## Controls

### Buttons

- Start from `.yw-button`.
- Use `.yw-button--primary` for the single dominant action on a screen.
- Use `.yw-button--secondary` for repeated content actions.
- Use `.yw-button--ghost` for quiet auxiliary controls.
- Repeated list or table actions must remain compact and visually subordinate
  to the content.
- Button labels should be short, stable, and written in sentence case.
- Do not make repeated desktop table actions fill the entire cell.

### Language switch

- Use `.yw-language-switch`.
- Place it in the global navigation, never inside page content or Hero copy.
- It is the only navigation control that uses pill geometry.

### Text links

- Use `.yw-text-link` for references and supporting destinations.
- Reference links remain visually distinct from action buttons.
- External destinations may use the shared external-link marker.

## Navigation

- Keep the YOYOworks brand at the left and page navigation at the right.
- Preserve the same navigation placement across every page.
- Highlight the active top-level destination without adding another filled
  primary button.
- The Projects dropdown owns project discovery; page-level actions do not
  belong in it.

## Cards and Tables

- Dense information surfaces use solid or nearly solid backgrounds.
- Use borders and subtle tonal changes before shadows.
- Avoid blur on repeating rows and mobile cards.
- Table headers, card headers, body content, references, and actions must have
  visibly different hierarchy.
- Repeated controls should not dominate the scanning rhythm.

## Motion

- Use only the shared transition timing.
- Hover and pressed states may change color, border, or surface tone.
- Avoid decorative entrance animation and scroll choreography.
- Respect the reduced-motion rules already defined in the shared theme.

## Page Overrides

Before changing a page, check `design-system/pages/` for a matching override.
Page overrides may define layout behavior but must not duplicate token values
from `assets/theme.css`.

## Anti-patterns

- AI-purple or neon palettes unrelated to the YOYOworks brand.
- Random gradients, circular bubbles, or generic technology grids.
- Full-width outlined buttons repeated down a desktop table.
- Multiple competing button radii or font weights.
- Heavy shadows or blur on content-dense surfaces.
- Page-specific raw colors, radii, spacing, or control heights when a shared
  token already exists.

