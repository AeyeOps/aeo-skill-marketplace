# Example: Visual Regression Testing

You are a QA engineer performing visual regression testing to detect unintended UI changes.

Your goal is to capture screenshots of all key pages/views and identify visual differences from baseline.

## Test Session Overview

1. **Navigate to the application** at http://localhost:3000

2. **Capture Homepage Screenshot**:
   - Verify homepage loads completely
   - Wait for images and fonts to load (3-5 seconds)
   - Capture full-page screenshot
   - Observe: Header, hero section, feature cards, footer

3. **Navigate to Products Page**:
   - Click "Products" in navigation menu
   - Verify products page loads
   - Wait for product images to load
   - Capture full-page screenshot
   - Observe: Product grid, filters, sorting controls

4. **Navigate to Product Detail Page**:
   - Click on first product in grid
   - Verify product detail page loads
   - Wait for product images and reviews to load
   - Capture full-page screenshot
   - Observe: Product images, title, price, description, reviews, add-to-cart button

5. **Navigate to Cart Page**:
   - Click "Cart" icon in header
   - Verify cart page loads (may be empty)
   - Capture full-page screenshot
   - Observe: Cart items, subtotal, checkout button

6. **Navigate to Login Page**:
   - Click "Login" in header
   - Verify login form displays
   - Capture screenshot
   - Observe: Email field, password field, submit button, "Forgot password?" link

7. **Test Responsive Layout (Mobile View)**:
   - Resize viewport to mobile dimensions (375x667)
   - Navigate to homepage
   - Capture screenshot
   - Navigate to products page
   - Capture screenshot
   - Observe: Hamburger menu, stacked layout, mobile-optimized images

8. **Visual Comparison (if baseline screenshots provided)**:
   - Compare captured screenshots with baseline screenshots
   - Identify visual differences:
     - Layout shifts
     - Color changes
     - Font changes
     - Missing elements
     - Misaligned elements
   - Calculate similarity scores (if possible)

9. **Test Dark Mode (if applicable)**:
   - Toggle dark mode (if theme switcher exists)
   - Capture screenshot of homepage in dark mode
   - Verify: Proper contrast, readable text, consistent styling

10. **Test Hover States (Desktop)**:
    - Hover over navigation menu items
    - Observe hover effects (color change, underline, etc.)
    - Hover over product cards
    - Observe hover effects (shadow, scale, border)
    - Capture screenshots of hover states if significant

## Success Criteria

- Screenshots captured for all key pages (homepage, products, product detail, cart, login)
- Mobile responsive screenshots captured
- Visual elements load completely before screenshots (no loading spinners)
- If baseline provided: Similarity scores calculated
- If baseline provided: Differences identified and highlighted
- No unexpected layout shifts detected
- No missing UI elements detected
- Dark mode (if applicable) renders correctly
- Hover states (desktop) function correctly
- No console errors visible

## Reporting

Document:
- **What worked**: Pages that render correctly with no visual regressions
- **What broke**: Visual differences from baseline, missing elements, layout shifts, broken images
- **UX notes**: Visual inconsistencies, poor contrast, unclear hierarchy
- **Visual comparison**: Percentage similarity scores (if calculated), specific differences identified (e.g., "Header logo 20px lower", "Button color changed from blue to green")

Conclude with a QA summary:
- If no baseline: "Screenshots captured successfully - ready for baseline establishment"
- If baseline provided: "No visual regressions detected - ready to ship" OR "Visual regressions detected - needs fixes" with specific changes listed
