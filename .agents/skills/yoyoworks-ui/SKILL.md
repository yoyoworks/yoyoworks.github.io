---
name: yoyoworks-ui
description: Apply the YOYOworks design system to new and existing site pages.
---

# YOYOworks UI

Use this skill for every visual, layout, navigation, responsive, or component
change in this repository.

## Required context

1. Read `design-system/MASTER.md` completely.
2. Check `design-system/pages/` for an override matching the page.
3. Inspect `assets/theme.css` for existing tokens and component classes before
   adding CSS.

## Implementation rules

- Treat `assets/theme.css` as the only source of concrete visual values.
- Put shared tokens and reusable controls in `assets/theme.css`.
- Keep page CSS limited to composition, geometry, data layout, and documented
  page overrides.
- Reuse `.yw-button`, its variants, `.yw-language-switch`, and `.yw-text-link`.
- Do not add raw colors, spacing, radii, shadows, font sizes, or control heights
  to page CSS when a shared token can express the change.
- Update the design documentation only when visual intent or component usage
  changes. Do not copy CSS values into documentation.

## Validation

- Build all generated pages and run the repository tests.
- Review Chinese and English output.
- Capture screenshots at narrow phone, standard phone, and desktop widths.
- Check control hierarchy, text wrapping, horizontal overflow, visual rhythm,
  and whether decoration competes with content.
- Keep the workspace free of generated build output unless the repository
  intentionally tracks it.

