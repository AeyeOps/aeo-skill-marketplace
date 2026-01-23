# Multi-File Skill Example

A skill with progressive disclosure using multiple documentation files.

## Use Case
Excel spreadsheet analysis with reference docs for different analysis types.

## File Structure
```
excel-analyzer/
├── SKILL.md (overview and navigation)
├── reference.md (API reference)
├── examples.md (usage examples)
└── workflows/
    ├── pivot-tables.md
    ├── charts.md
    └── formulas.md
```

## SKILL.md (Main File)

```markdown
---
name: Excel Analyzer
description: Analyze Excel spreadsheets, create pivot tables, generate charts, and build complex formulas. Use when working with .xlsx/.xlsm files or data analysis tasks.
---

# Excel Analyzer

Comprehensive Excel file analysis and manipulation using the openpyxl library.

## Quick Start

Read an Excel file:
```python
from openpyxl import load_workbook
wb = load_workbook('data.xlsx')
ws = wb.active
```

## Core Workflows

**Pivot Tables**: See [workflows/pivot-tables.md](workflows/pivot-tables.md)
**Charts and Graphs**: See [workflows/charts.md](workflows/charts.md)
**Complex Formulas**: See [workflows/formulas.md](workflows/formulas.md)

## API Reference

For complete openpyxl API documentation, see [reference.md](reference.md)

## Examples

For common use case examples, see [examples.md](examples.md)

## Requirements

Ensure `openpyxl` is installed:
```bash
pip install openpyxl
```
```

## workflows/pivot-tables.md

```markdown
# Pivot Table Workflows

## Creating a Basic Pivot Table

```python
from openpyxl import load_workbook
from openpyxl.pivot.table import TableDefinition, PivotTable

wb = load_workbook('sales.xlsx')
ws = wb.active

# Define source data range
data_range = 'A1:D100'

# Create pivot table
pivot = PivotTable()
pivot.addColumnFields('Region')
pivot.addRowFields('Product')
pivot.addDataFields('Revenue', 'sum')

# Add to new sheet
pivot_ws = wb.create_sheet('Pivot')
pivot_ws.add_pivot_table(pivot, 'A1', data_range)
wb.save('sales_with_pivot.xlsx')
```

## Advanced: Multi-Level Grouping

[Content continues with advanced pivot table examples...]
```

## reference.md

```markdown
# openpyxl API Reference

## Contents
- Workbook operations
- Worksheet operations
- Cell operations
- Styling and formatting
- Charts
- Formulas

## Workbook operations

**load_workbook(filename)**: Load existing workbook
- Parameters: filename (str), read_only (bool), data_only (bool)
- Returns: Workbook object

**Workbook()**: Create new workbook
- Parameters: None
- Returns: Empty Workbook object

[Reference continues...]
```

## examples.md

```markdown
# Excel Analyzer Examples

## Example 1: Read and Display Data

```python
from openpyxl import load_workbook

wb = load_workbook('report.xlsx')
ws = wb['Sales']

# Print first 5 rows
for row in ws.iter_rows(min_row=1, max_row=5, values_only=True):
    print(row)
```

## Example 2: Calculate Column Totals

[Examples continue...]
```

## Key Points

- **Progressive disclosure**: SKILL.md navigates to detailed workflows
- **Organized by domain**: Pivot tables, charts, formulas separated
- **Table of contents**: Each long file starts with contents
- **One level deep**: All references are directly from SKILL.md
- **Clear triggers**: "working with .xlsx/.xlsm files" and "data analysis" in description
