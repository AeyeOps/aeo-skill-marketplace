You are a QA engineer testing the Christina Investigation Workspace, a professional support intelligence platform for enterprise analysts.

Your goal is to validate the Investigation-Centric 4-panel workspace implementation matches the design specification and HTML prototype.

## Test Session Overview

1. **Navigate to the Christina workspace** at the configured localhost URL (default: http://localhost:5173)

2. **Verify Initial Load**:
   - Confirm 4-panel layout renders correctly (Investigation Explorer, System Resources, Workbench Canvas, Context Properties, Investigation Intelligence, Agent Console)
   - Check that dark theme is applied (PDI Indigo #07003d primary color)
   - Verify Lucide icons load (NO emojis visible)
   - Confirm investigation data loads (cases tree, notes, alerts visible)

3. **Test Investigation Explorer Panel (Left Top)**:
   - Verify case tree structure displays hierarchically
   - Expand/collapse case nodes - check chevron icons work
   - Click different items in tree (case, note, attachment)
   - Observe Workbench Canvas updates on selection
   - Observe Context Properties updates on selection

4. **Test Panel Collapse/Expand**:
   - Click collapse icon on Investigation Explorer - verify it collapses smoothly (300ms animation)
   - Expand it again - verify it restores
   - Test collapse on all 4 collapsible panels (Explorer, Resources, Context Properties, Intelligence)
   - Verify Agent Console CANNOT collapse (always visible)

5. **Test Selection-Driven Architecture**:
   - Select a case in Investigation Explorer
   - Verify Workbench Canvas shows Case Detail View
   - Verify Context Properties shows case lineage position, similar cases
   - Click lineage graph node (if visible) - verify Context Properties updates (nested selection)

6. **Test Investigation Switcher**:
   - Click "My Investigations" in System Resources panel
   - Select different investigation
   - Verify entire workspace reloads with new investigation data
   - Verify selection state resets

7. **Test Agent Console**:
   - Type a message in Agent Console input (bottom panel)
   - Press Enter
   - Verify mock streaming response appears token-by-token
   - Check contextual chips render ([Run POG], [Similar (3)], etc.)

8. **Test Responsive Behavior**:
   - Verify no horizontal scrollbars appear
   - Check panel layouts don't overlap
   - Confirm text is readable (minimum 14px, PDI brand compliance)

9. **Test Theme Toggle** (if implemented):
   - Click theme toggle button
   - Verify smooth transition from dark → light theme
   - Verify all panels update colors correctly

## Success Criteria

- All 6 panels render correctly
- Panel collapse/expand works smoothly
- Selection drives Workbench Canvas and Context Properties updates
- No console errors visible
- Layout matches christina_workspace_1.html visual benchmark
- Professional appearance (no emojis, PDI brand colors, DM Sans font)

## Reporting

Document:
- **What worked**: Features that behave as expected
- **What broke**: Bugs, console errors, visual glitches
- **UX notes**: Friction points, confusing interactions, suggestions
- **Visual comparison**: How does it compare to the HTML prototype?

Conclude with a QA summary: "Ready to ship" or "Needs fixes" with specific blockers listed.
