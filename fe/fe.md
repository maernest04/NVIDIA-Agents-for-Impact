# Frontend Generation Prompt for Gemini

Use my attached wireframe as the base layout reference, but improve it significantly so it feels calmer, more modern, more trustworthy, and more comfortable for SJSU students.

Build the **frontend only** for this hackathon project:

## Project
**SJSU Safeline**  
NVIDIA Agents for Impact Hackathon — SJSU, March 16 2026

This app helps a person describe their situation in plain language, then shows the most relevant crisis support resources and a short call script for what to say.

The experience must feel:
- calm
- compassionate
- non-judgmental
- student-friendly
- modern and clean
- trustworthy, not overly clinical
- demo-ready for hackathon judges

## Important design intent
My current wireframe has:
- a left panel for user input
- a large right panel for results
- a bottom loading/status area

Keep that overall **two-column structure**, but redesign it so it feels much softer and more human.

Do **not** make it look like an admin dashboard.
Do **not** make it feel cold, robotic, or overly enterprise.
Do **not** use harsh borders everywhere.

## Target users
Primary audience:
- SJSU students
- young adults under stress
- users who may be overwhelmed, anxious, or unsure how to ask for help

So the UI should reduce friction and answer this emotional question:
**“Do I feel safe enough to type here?”**

## What the app should do in the UI
The screen should support 3 main states:

1. **Empty state**
   - Warm welcome message
   - Short explanation that users can type in their own words
   - Quick prompt chips to help them start

2. **Loading / routing state**
   - Show supportive progress copy instead of a generic spinner
   - Example steps:
     - Understanding your situation
     - Finding support options
     - Preparing what you can say when you call

3. **Results state**
   - Show 1–3 support resource cards
   - Each card includes:
     - hotline/resource name
     - phone number
     - availability/hours
     - short “why this may help” text
     - short call script
     - actions like Call / Copy

## Required UX elements
### Header
Include:
- app title: **SJSU Safeline**
- subtitle: **Find the right support without knowing what to search for.**
- a visible but calm emergency note: **In immediate danger? Call 911 now.**

### Left panel
Use the left column for:
- title / introduction
- supportive one-line guidance
- quick prompt chips
- main multiline text input
- primary CTA button
- privacy/trust microcopy

Suggested helpful microcopy:
- **Tell us what’s going on. You do not need perfect words.**
- **Private, judgment-free, and in plain language.**

Suggested quick prompt chips:
- I’m feeling overwhelmed
- I don’t feel safe at home
- I need mental health support
- I’m worried about a friend
- I need help tonight
- I don’t know where to start

### Main input area
Make it feel like a comfortable chat prompt box, not a tiny form.
Use placeholder text like:
- **What’s going on?**
- **Describe your situation in your own words...**

CTA button text should be clear and supportive, not just an icon.
Use one of these:
- **Find support**
- **Get help options**

### Right panel
The right side is the main response area.
It should feel organized and reassuring.

For empty state, show:
- a soft illustration area or visual placeholder
- a sentence explaining that support options will appear here
- maybe 2–3 example scenarios

For results state, show stacked cards with strong hierarchy.
Each card should feel easy to scan.

### Agent transparency panel
Because this is a hackathon demo, include a small **collapsible** or **secondary** panel that shows the AI/tool-routing concept without overwhelming the user.
Examples:
- detected categories
- hotline lookup called
- number of matched resources

This is for judges, so it should exist, but it should not dominate the experience.

## Visual style
Create a visual system that feels like:
- student wellness app
- campus support tool
- modern startup polish
- accessible and emotionally safe

### Color direction
Use a calm palette:
- soft off-white / light neutral background
- deep blue or muted navy for trust
- muted green or teal accent for support
- optional subtle gold accent to hint at SJSU energy

Avoid:
- bright aggressive red dominating the UI
- heavy black borders
- neon gradients
- overly playful cartoon styling

### Shape and spacing
- soft rounded corners
- comfortable whitespace
- light borders or subtle shadows
- generous internal padding
- strong readability

### Typography
Use a clean sans-serif style.
Emphasize clarity and warmth.
Make headings clear but not loud.
Make body text easy to scan.

## Accessibility
Please make the UI accessible.
Include:
- semantic HTML
- clear focus states
- keyboard-friendly interactions
- sufficient color contrast
- responsive layout
- readable sizing

## Technical requirements
Generate a production-quality frontend using:
- **React**
- **Tailwind CSS**
- component-based structure

If possible, use a single-page app layout.
Use clean, maintainable code.
Use realistic mock data for the results.

Please create:
- reusable components
- a polished layout
- empty/loading/results states
- good spacing and hover/focus states

## Suggested component structure
You can organize components like:
- `AppShell`
- `Header`
- `PromptPanel`
- `PromptChips`
- `PromptInput`
- `ResultsPanel`
- `ResourceCard`
- `LoadingState`
- `EmptyState`
- `AgentTrace`

## Data to mock
Use sample categories like:
- mental_health
- suicide
- domestic_violence
- substance_use
- homelessness
- human_trafficking
- general_crisis
- emergency

Use 2–3 sample resources in mock data, for example:
- 988 Suicide & Crisis Lifeline
- Crisis Text Line
- National Domestic Violence Hotline

Each should include a short script such as:
- “Hi, I’m going through a hard time and need support right now.”
- “I’m not sure how to explain everything, but I need help.”

## Layout guidance
Desktop-first layout:
- left column around 35%
- right column around 65%

Inside the right column:
- keep the large response area
- integrate the loading/status experience into the main panel instead of a disconnected footer bar

For mobile:
- stack vertically
- keep the CTA visible
- preserve calm spacing

## Tone requirements in UI copy
All on-screen copy should feel:
- compassionate
- direct
- simple
- non-clinical
- non-judgmental

Avoid robotic copy like:
- “Processing request”
- “Classification complete”
- “System response generated”

Prefer copy like:
- “We’re finding support options for you.”
- “You can use these words when you call.”
- “You’re not expected to know exactly what to say.”

## Safety note
The product should not present itself as medical diagnosis or therapy.
It is a support-routing interface.
Always keep a visible note that says:
**For immediate emergencies, call 911.**

## Output request
Please generate:
1. the full frontend implementation
2. clean React + Tailwind code
3. polished mock data
4. responsive design
5. a visually refined version of my wireframe

Make it look like a hackathon-winning demo that is emotionally thoughtful, technically clear, and comfortable for SJSU students.
