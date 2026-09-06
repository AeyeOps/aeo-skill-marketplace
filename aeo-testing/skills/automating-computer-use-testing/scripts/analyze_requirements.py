#!/usr/bin/env python3
"""Analyzes automation requirements from user input and suggests goal file structure.

Usage:
    python analyze_requirements.py

Interactive tool that prompts for:
- Application URL
- Application type (React, Vue, Angular, etc.)
- Key features to test
- Success criteria
- Testing priorities

Outputs suggested goal file structure based on inputs.
"""

def main():
    print("=== Gemini Computer-Use Automation Requirements Analyzer ===\n")

    # Gather requirements
    print("Please provide the following information:\n")

    app_name = input("Application name: ").strip()
    app_url = input("Application URL (default: http://localhost:5173): ").strip() or "http://localhost:5173"
    app_type = input("Application type (React/Vue/Angular/Other): ").strip() or "React"

    print("\nWhat are the key features to test? (separate with commas)")
    features_input = input("Features: ").strip()
    features = [f.strip() for f in features_input.split(',') if f.strip()] if features_input else []

    print("\nWhat constitutes success? (separate with commas)")
    success_input = input("Success criteria: ").strip()
    success_criteria = [s.strip() for s in success_input.split(',') if s.strip()] if success_input else []

    print("\nWhat should be verified visually?")
    visual_verification = input("Visual checks: ").strip()

    # Generate suggested goal structure
    print("\n" + "="*60)
    print("SUGGESTED GOAL FILE STRUCTURE")
    print("="*60 + "\n")

    print(f"You are a QA engineer validating the {app_type} application {app_name}.")
    focus_summary = ', '.join(features[:3]) if features else 'core functionality'
    print(f"\nYour goal is to validate the {focus_summary} with production-like realism.")
    print("\n## Test Session Overview\n")
    print(f"1. **Navigate to the application** at {app_url}\n")
    print("2. **Verify Initial Load**:")
    if visual_verification:
        print(f"   - {visual_verification}")
    print("   - Confirm all key UI elements render")
    print("   - Record baseline performance (first paint, API latency)")
    print("   - Capture accessibility or console warnings for triage")
    print("   - Verify no console errors\n")

    for i, feature in enumerate(features, start=3):
        print(f"{i}. **Test {feature}**:")
        print(f"   - [ACTION: Describe how to test {feature} using realistic data]")
        print("   - [NEGATIVE: Note the failure modes and expected safeguards]")
        print(f"   - [VERIFY: What should happen when {feature} works correctly]\n")

    print("\n## Success Criteria\n")
    for criterion in success_criteria:
        print(f"- {criterion}")
    if not success_criteria:
        print("- All features function correctly")
        print("- No console errors visible")
        print("- UI matches design specifications")

    print("\n## Reporting\n")
    print("Document:")
    print("- **What worked**: Features that behave as expected")
    print("- **What broke**: Bugs, errors, broken functionality")
    print("- **UX notes**: Friction points, suggestions")
    print("- **Evidence**: Screenshots, HAR files, and logs for each defect")
    print("\nConclude with QA summary: 'Ready to ship' or 'Needs fixes' with blockers.\n")

    print("="*60)
    print("Copy the above structure to your goal file and customize as needed.")
    print("="*60)


if __name__ == "__main__":
    main()
