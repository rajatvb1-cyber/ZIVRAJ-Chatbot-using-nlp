---
name: ZIVRAJ
colors:
  surface: '#0d1321'
  surface-dim: '#0d1321'
  surface-bright: '#333948'
  surface-container-lowest: '#070e1b'
  surface-container-low: '#151c29'
  surface-container: '#19202d'
  surface-container-high: '#232a38'
  surface-container-highest: '#2e3543'
  on-surface: '#dce2f5'
  on-surface-variant: '#bbc9cf'
  inverse-surface: '#dce2f5'
  inverse-on-surface: '#2a303f'
  outline: '#859399'
  outline-variant: '#3c494e'
  surface-tint: '#47d6ff'
  primary: '#a5e7ff'
  on-primary: '#003543'
  primary-container: '#00d2ff'
  on-primary-container: '#00566a'
  inverse-primary: '#00677f'
  secondary: '#e6feff'
  on-secondary: '#003739'
  secondary-container: '#00f4fe'
  on-secondary-container: '#006c71'
  tertiary: '#e5d7ff'
  on-tertiary: '#3c0090'
  tertiary-container: '#ccb6ff'
  on-tertiary-container: '#6100de'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#b6ebff'
  primary-fixed-dim: '#47d6ff'
  on-primary-fixed: '#001f28'
  on-primary-fixed-variant: '#004e60'
  secondary-fixed: '#63f7ff'
  secondary-fixed-dim: '#00dce5'
  on-secondary-fixed: '#002021'
  on-secondary-fixed-variant: '#004f53'
  tertiary-fixed: '#e9ddff'
  tertiary-fixed-dim: '#d1bcff'
  on-tertiary-fixed: '#23005b'
  on-tertiary-fixed-variant: '#5700c9'
  background: '#0d1321'
  on-background: '#dce2f5'
  surface-variant: '#2e3543'
typography:
  display-lg:
    fontFamily: Sora
    fontSize: 48px
    fontWeight: '700'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Sora
    fontSize: 32px
    fontWeight: '600'
    lineHeight: '1.2'
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Sora
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.2'
  body-md:
    fontFamily: Geist
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.6'
  label-sm:
    fontFamily: Geist
    fontSize: 12px
    fontWeight: '600'
    lineHeight: '1'
    letterSpacing: 0.05em
rounded:
  sm: 0.5rem
  DEFAULT: 1rem
  md: 1.5rem
  lg: 2rem
  xl: 3rem
  full: 9999px
spacing:
  base: 8px
  container-padding: 24px
  gutter: 16px
  stack-sm: 12px
  stack-md: 24px
  stack-lg: 48px
---

## Brand & Style
The design system embodies a "Hyper-Intelligence" aesthetic, positioning the product as an advanced, ethereal AI companion. The visual language is rooted in **Glassmorphism** and **Futuristic Minimalism**, utilizing high-contrast neon accents against deep, infinite voids. 

The emotional response should be one of awe, sophistication, and seamless technological integration. Every element is designed to feel as though it is floating in a pressurized, high-tech environment—utilizing transparency and light refraction to create a sense of depth and intelligence.

## Colors
The palette is strictly nocturnal, designed to reduce eye strain while emphasizing high-energy focal points. 
- **The Void (Neutral):** A deep navy-blue gradient serves as the canvas, creating an expansive sense of space.
- **Neon Highlights (Primary/Secondary):** Electric blues and cyans are used exclusively for interactive elements, status indicators, and the AI's "pulse."
- **Deep Accents (Tertiary):** A soft purple is used for secondary actions and to add chromatic depth to gradients, preventing the UI from feeling monochromatic.

## Typography
The typography system uses **Sora** for its geometric, futuristic proportions in headlines, while **Geist** provides a highly legible, technical feel for data and chat interfaces. 

Hierarchies are reinforced through weight and "luminance" rather than just size; primary text is pure white (#FFFFFF), while secondary text uses a muted blue-grey (#94a3b8) to recede into the background.

## Layout & Spacing
This design system utilizes a **Fluid Grid** model with generous safe areas. Elements are grouped into "Glass Modules" that float within the viewport. 

The spacing rhythm is built on an 8px scale. On desktop, the layout favors wide, centered chat-flows with significant horizontal margins to enhance the premium feel. Mobile layouts collapse into a single-column view where the glass containers span the full width minus a 16px margin.

## Elevation & Depth
Depth is the primary communicator of hierarchy. 
- **Surface 0 (Background):** The deep navy gradient with a subtle "noise" texture or glowing particle field.
- **Surface 1 (Glass Containers):** Semi-transparent white fill (opacity: 4% - 8%) with a `backdrop-filter: blur(16px)`.
- **Borders:** Every glass container must have a 1px solid border. Use a linear gradient for the border: `rgba(255,255,255,0.2)` at the top-left to `rgba(255,255,255,0.05)` at the bottom-right.
- **Glows:** Instead of traditional black shadows, use "Neon Underglows"—soft, diffused outer glows using the primary neon blue color at very low opacity (15%) for active or elevated states.

## Shapes
The shape language is ultra-smooth. All primary containers use a 24px corner radius to soften the technical edge of the AI. Interactive elements like buttons and input fields utilize pill-shapes (fully rounded) to evoke a friendly, approachable, yet modern aesthetic.

## Components
- **Chat Bubbles:** AI responses should use the primary glass style with a subtle cyan glow. User messages should be more translucent with no glow to maintain secondary hierarchy.
- **Glass Inputs:** Floating bars with a 1px cyan border when focused. The cursor should be a pulsing neon block.
- **Action Buttons:** High-saturation neon gradients. On hover, the button should scale by 1.05x and increase its "glow radius."
- **Status Chips:** Small pill-shaped glass elements with a "live" breathing animation for the AI's "thinking" state.
- **Scrollbars:** Ultra-thin, 4px wide, neon blue tracks that only appear on interaction.
- **Cards:** Use "Frosted Glass" with internal padding of 24px and Sora headlines.