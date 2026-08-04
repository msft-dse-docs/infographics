# Creating HTML Infographics with CoWork

This guide walks you through using CoWork to generate a self-contained HTML infographic for the SME&C Infographic Hub.

## Prerequisites

- Access to CoWork
- A clear topic or presentation you want to turn into an infographic

## Steps

### 1. Upload Your Source Content

The best infographics come from **grounded sources** — an existing PowerPoint, PDF, or other content you already have. Starting from real content gives CoWork accurate details to work with and avoids hallucinated information.

1. Open CoWork and start a new session
2. Click the **+** button in the CoWork client
3. Select **Upload images and files**
4. Upload your PowerPoint, PDF, or other source material

### 2. Prompt for an Infographic

Reference the uploaded documents in your prompt so CoWork uses them as the basis for the infographic.

> **Example prompt:**
> *"Can you take this presentation and instead turn it into an interactive learning html page broken down into well animated infographics that I could send to users?"*

You can also add specifics to steer the output:

- **Style** — request Microsoft Fluent / Segoe UI styling to stay consistent with the site
- **Sections** — call out specific sections or key points to emphasize
- **Audience** — mention who will be reading it (e.g., customers, internal team)

### 3. Review and Refine

CoWork will produce an HTML file with inline CSS and SVG graphics. Review it by:

1. Saving the output as an `.html` file
2. Opening it in your browser to verify layout and content
3. Iterating with CoWork if anything needs adjustment (e.g., "make the comparison table wider" or "add a section on pricing")

### 4. Finalise the File

Before committing, make sure the file:

- Is **fully self-contained** — all styles, scripts, and images are inline (no external dependencies)
- Has a descriptive file name using kebab-case (e.g., `sql-2016-eol-customer-guide.html`)
- Renders correctly at common screen widths (desktop and tablet)

## Tips

- Keep infographics focused — one topic per file works best.
- Use CoWork's iteration loop to polish layout and copy before committing.
- If you need icons or diagrams, ask CoWork to embed them as inline SVGs.

## Next Steps

Once your HTML file is ready, follow [Adding an Infographic to the Website](adding-an-infographic-to-the-website.md) to publish it.
