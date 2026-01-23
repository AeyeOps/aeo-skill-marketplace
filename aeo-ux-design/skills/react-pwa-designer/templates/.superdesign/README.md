# SuperDesign Directory Structure

This directory stores design iteration artifacts during the SuperDesign methodology workflow.

## Directory Purpose

`.superdesign/design_iterations/` - Stores HTML, CSS, and SVG design prototypes

## Usage

Copy this entire `.superdesign/` directory to your project root:

```bash
cp -r templates/.superdesign ./
```

## File Naming Convention

Design artifacts follow this pattern:
- HTML: `{component_name}_{iteration}.html` (e.g., `table_1.html`, `chat_ui_2.html`)
- CSS: `theme_{iteration}.css` (e.g., `theme_1.css`)
- SVG: `{component_name}_{iteration}.svg`

## Example Structure

```
.superdesign/
└── design_iterations/
    ├── theme_1.css
    ├── theme_2.css
    ├── table_1.html
    ├── table_2.html
    ├── chat_ui.html
    └── chat_ui.css
```

## Workflow Integration

1. Phase 1 (Research): Iterate on designs, save to `design_iterations/`
2. Phase 2 (Refine): Reference previous iterations from this directory
3. Phase 3 (Implement): Convert final designs to React components

See SuperDesign.md for complete methodology.
