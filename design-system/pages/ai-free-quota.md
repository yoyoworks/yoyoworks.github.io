# AI Free Quota Page Override

This file records only behavior that differs from the global YOYOworks design
system. Shared visual values remain in `assets/theme.css`.

## Content priority

- The first screen should expose the title, freshness, compact totals, and the
  beginning of the actual directory.
- Supporting explanatory copy belongs after the directory.
- The raw JSON dataset is not presented as a user-facing action.

## Responsive model

- Desktop and tablet use a structured table.
- Mobile converts each row into a flat content card.
- Long mobile descriptions show a short preview and expand independently.
- Short descriptions remain fully visible without an extra control.
- Descriptions lead with quota, validity, and the main eligibility condition.
- Reference and registration actions remain visible while details are collapsed.
- Desktop actions are compact and fixed-width.
- Mobile actions align with their field labels without filling the entire card.
- Desktop reference and registration columns center their headers and controls.
- Mobile action rows keep field labels at the left and controls at the right.

## Page-specific visuals

- Hero geometry may be stronger on desktop and quieter on mobile.
- The top-right teal plane remains visible at all breakpoints.
- Decorative planes must not sit beneath text on mobile.
- Repeating table rows and mobile cards do not use decorative blur.

## Control usage

- Language switching lives in the global navigation.
- Official references use `.yw-text-link`.
- Registration destinations use `.yw-button.yw-button--secondary`.
- Repeated registration controls use the page action sizing hook rather than
  redefining the shared button system.
