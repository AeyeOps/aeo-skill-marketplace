# Code Skill Example

A skill that bundles executable scripts alongside documentation.

## Use Case
PDF form processing with Python scripts for analysis, filling, and validation.

## File Structure
```
pdf-processor/
├── SKILL.md (main instructions)
├── FORMS.md (form-filling guide)
├── reference.md (API reference)
├── examples.md (usage examples)
└── scripts/
    ├── analyze_form.py (extract fields)
    ├── fill_form.py (populate form)
    └── validate.py (validate filled form)
```

## SKILL.md

```markdown
---
name: PDF Form Processor
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF documents, form automation, or document processing tasks.
---

# PDF Form Processor

Automate PDF form processing using PyPDF2 and reportlab libraries.

## Quick Start

Analyze a PDF form:
```bash
python scripts/analyze_form.py input.pdf
```

## Core Workflows

**Form Analysis**: Extract field names and types from PDF forms
**Form Filling**: Populate PDF forms with data
**Validation**: Verify filled forms meet requirements

## Detailed Guides

**Form filling workflows**: See [FORMS.md](FORMS.md)
**API reference**: See [reference.md](reference.md)
**Usage examples**: See [examples.md](examples.md)

## Available Scripts

### analyze_form.py
Extract all form fields from a PDF.

**Usage:**
```bash
python scripts/analyze_form.py <pdf_file> [--output json|text]
```

**Output:** Field names, types, and current values

### fill_form.py
Populate PDF form fields with provided data.

**Usage:**
```bash
python scripts/fill_form.py <template.pdf> <data.json> <output.pdf>
```

**Data format:** JSON with field names as keys

### validate.py
Validate filled form against rules.

**Usage:**
```bash
python scripts/validate.py <filled_form.pdf> <rules.json>
```

**Returns:** List of validation errors or success message

## Requirements

```bash
pip install PyPDF2 reportlab
```
```

## scripts/analyze_form.py

```python
#!/usr/bin/env python3
"""
PDF Form Field Analyzer
Extracts all form fields from a PDF file.
"""
import sys
import json
from PyPDF2 import PdfReader

def analyze_pdf_form(pdf_path, output_format='text'):
    """Extract form fields from PDF."""
    try:
        reader = PdfReader(pdf_path)
        fields = reader.get_fields()

        if output_format == 'json':
            print(json.dumps(fields, indent=2))
        else:
            for field_name, field_info in fields.items():
                field_type = field_info.get('/FT', 'Unknown')
                field_value = field_info.get('/V', '')
                print(f"Field: {field_name}")
                print(f"  Type: {field_type}")
                print(f"  Value: {field_value}")
                print()

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python analyze_form.py <pdf_file> [--output json|text]")
        sys.exit(1)

    pdf_file = sys.argv[1]
    output_fmt = 'text'

    if len(sys.argv) > 2 and sys.argv[2] == '--output':
        output_fmt = sys.argv[3] if len(sys.argv) > 3 else 'text'

    analyze_pdf_form(pdf_file, output_fmt)
```

## scripts/fill_form.py

```python
#!/usr/bin/env python3
"""
PDF Form Filler
Populates PDF form fields with data from JSON.
"""
import sys
import json
from PyPDF2 import PdfReader, PdfWriter

def fill_pdf_form(template_path, data_path, output_path):
    """Fill PDF form with data from JSON file."""
    try:
        # Load data
        with open(data_path, 'r') as f:
            data = json.load(f)

        # Read template
        reader = PdfReader(template_path)
        writer = PdfWriter()

        # Update fields
        writer.append_pages_from_reader(reader)
        writer.update_page_form_field_values(
            writer.pages[0],
            data
        )

        # Write output
        with open(output_path, 'wb') as f:
            writer.write(f)

        print(f"Form filled successfully: {output_path}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python fill_form.py <template.pdf> <data.json> <output.pdf>")
        sys.exit(1)

    fill_pdf_form(sys.argv[1], sys.argv[2], sys.argv[3])
```

## FORMS.md

```markdown
# PDF Form Filling Guide

## Workflow Overview

1. **Analyze** the blank form to discover field names
2. **Prepare** data in JSON format matching field names
3. **Fill** the form using the script
4. **Validate** the filled form

## Step 1: Analyze Form

```bash
python scripts/analyze_form.py blank_form.pdf --output json > fields.json
```

This outputs all field names and their properties.

## Step 2: Prepare Data

Create a JSON file with your data:

```json
{
  "applicant_name": "John Doe",
  "application_date": "2024-01-15",
  "email": "john@example.com",
  "phone": "(555) 123-4567"
}
```

## Step 3: Fill Form

```bash
python scripts/fill_form.py blank_form.pdf data.json filled_form.pdf
```

## Step 4: Validate

```bash
python scripts/validate.py filled_form.pdf rules.json
```

[Guide continues with advanced scenarios...]
```

## Key Points

- **Scripts execute via bash**: No context token cost for code
- **Clear instructions**: SKILL.md explains when to run each script
- **Structured workflow**: Analysis → Preparation → Filling → Validation
- **Supporting docs**: FORMS.md provides detailed guide
- **Real code**: Complete, working scripts included
