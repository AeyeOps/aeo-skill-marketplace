# Example: Form Automation with Validation Testing

You are a QA engineer testing a multi-step registration form.

Your goal is to validate form field validation, error messaging, and successful submission workflow.

## Test Session Overview

1. **Navigate to the registration form** at http://localhost:3000/register

2. **Verify Initial Load**:
   - Confirm registration form displays with Step 1 visible
   - Check "Create Account" header renders
   - Verify form fields are empty and ready for input
   - Confirm "Next Step" button is visible

3. **Test Required Field Validation**:
   - Click "Next Step" button without filling any fields
   - Verify error messages display for required fields:
     - "Name is required"
     - "Email is required"
     - "Password is required"
   - Confirm form does NOT progress to Step 2

4. **Test Email Format Validation**:
   - Enter "john" in email field (invalid format)
   - Enter valid values in name and password fields
   - Click "Next Step" button
   - Verify "Please enter a valid email address" error displays
   - Confirm form does NOT progress to Step 2

5. **Test Password Strength Validation**:
   - Enter valid name and email
   - Enter "123" in password field (too short)
   - Click "Next Step" button
   - Verify "Password must be at least 8 characters" error displays
   - Confirm form does NOT progress to Step 2

6. **Test Successful Step 1 Completion**:
   - Enter "John Doe" in name field
   - Enter "john.doe@example.com" in email field
   - Enter "SecurePass123!" in password field
   - Click "Next Step" button
   - Verify form progresses to Step 2
   - Confirm Step 1 data is preserved (not lost)

7. **Test Step 2 Fields**:
   - Verify Step 2 displays with additional fields:
     - Address
     - City
     - State (dropdown)
     - ZIP Code
   - Fill out all Step 2 fields with valid data
   - Click "Submit" button

8. **Test Successful Submission**:
   - Verify success message displays: "Account created successfully!"
   - Confirm user is redirected to /dashboard or confirmation page
   - Check that submitted data appears correctly (if dashboard shows it)

9. **Test Back Navigation**:
   - Return to registration form
   - Fill out Step 1 with valid data and progress to Step 2
   - Click "Back" button (if present)
   - Verify form returns to Step 1
   - Confirm Step 1 data is still populated (not lost)

## Success Criteria

- Required field validation works correctly
- Email format validation displays appropriate error
- Password strength validation displays appropriate error
- Valid Step 1 data progresses to Step 2
- Step 1 data persists when progressing to Step 2
- All Step 2 fields accept valid input
- Form submission succeeds with valid data
- Success message displays after submission
- User is redirected to appropriate page
- Back navigation preserves form data
- No console errors visible

## Reporting

Document:
- **What worked**: Form validation rules that function correctly
- **What broke**: Validation errors not appearing, data loss, submission failures
- **UX notes**: Confusing error messages, unclear field labels, friction in multi-step flow
- **Edge cases tested**: Empty fields, invalid formats, boundary conditions (e.g., password length)

Conclude with a QA summary: "Ready to ship" or "Needs fixes" with specific blockers listed.
