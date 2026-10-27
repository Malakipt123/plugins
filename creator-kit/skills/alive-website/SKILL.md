---
name: alive-website
description: >-
  Use when the user runs /alive-website or wants a website or landing page that
  looks designed by a real designer, not generic "AI slop": an art direction
  from real reference sites, a design vocabulary (grid, type, colour,
  spacing), a bank of polished components, purposeful motion with Framer
  Motion (motion.dev), and a Playwright screenshot loop to check the result.
---

# Alive Website

Generic AI sites look alike: centred hero, purple gradient, three feature cards, emoji icons, everything fading in. This skill avoids that with three layers (direction, components, motion) and checks the result in a real browser.

## 1. Art direction first

Before writing code, ask for or propose:

- **The one feeling** the site should give (calm, premium, playful, technical) and the audience.
- **2-3 real reference sites** the user likes. Open them with Playwright, take full-page screenshots, and note what makes them work: type scale, grid, how much white space, colour count, photo style.
- **Real content.** Real product name, real copy, real photos or screenshots from the user. No lorem ipsum, no stock "team smiling at laptop".

Write the direction to `DESIGN.md`: palette (one accent, the rest neutrals, with hex values and contrast ratios), two fonts at most with a modular type scale (e.g. 1.25), an 8 px spacing scale, a 12-column grid with max content width, corner radius, and shadow style. Every later decision follows this file.

## 2. Design vocabulary

Use precise words in your own plan and in code review, they produce better layouts than "make it nice":

- **Layout:** asymmetric split, bento grid, editorial column, full-bleed band, sticky aside.
- **Type:** display vs text sizes, tight tracking on large headings, line length 60-75 characters, real hierarchy (no more than 3 sizes per screen).
- **Colour:** one accent used for actions only; tinted neutrals instead of pure grey.
- **Polish:** optical alignment, consistent radii, hover and focus states on everything clickable, no orphaned single words in headings.

## 3. Component bank

Build the page from a small set of components in `components/`, each with its states: nav (with mobile menu), hero, logo strip, feature section, pricing table, testimonials, FAQ, footer, button (primary, secondary, ghost; hover, focus, disabled), input. Reuse them; do not restyle the same thing twice. If the project already has a component library (shadcn/ui, Radix, the user's own), use it instead of writing new ones.

## 4. Motion with purpose

Use Framer Motion (`motion` package, `import { motion } from "motion/react"`) in React, or the vanilla `motion` package otherwise.

- Animate to explain: reveal a section's content in reading order, show a state change, guide the eye to the call to action.
- Durations 150-400 ms for UI, up to 800 ms for hero entrances; ease-out for entering, ease-in for leaving; spring for things the user drags or toggles.
- Scroll reveals once (`whileInView` with `viewport={{ once: true }}`), small distances (16-24 px), never on every element.
- Respect `prefers-reduced-motion`: use `useReducedMotion()` and fall back to opacity only.
- Animate only `transform` and `opacity` to stay at 60 fps.

## 5. Check it in a browser (Playwright)

After each significant change, start the dev server and with Playwright:

1. Screenshot at 390, 768 and 1440 px wide, full page. Look at every screenshot.
2. Check for: horizontal scroll on mobile, text overflowing its box, contrast below 4.5:1 for body text, missing hover/focus styles, layout shift when fonts load.
3. Record the hero entrance as a short video (`recordVideo`) when motion changed, and watch it.
4. Fix what you find and screenshot again. Report what you checked and what you fixed.

## Done means

The page matches `DESIGN.md`, uses only components from the bank, works on mobile and desktop screenshots, passes the contrast check, and every animation has a reason you can name.
