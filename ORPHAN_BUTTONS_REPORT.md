# Report on Orphan Buttons

The following buttons were identified as potentially missing a form assignment or having HTML structure issues.

## High Priority Issues

1.  **`prototype/templates/pages/residents_add.html`**
    *   **Button:** `<button type="submit" class="btn btn-primary px-8">Save Resident Profile</button>`
    *   **Issue:** The button is visually inside a `<form>`, but extra closing `</div>` tags in the `Sectoral Info` section cause the form to be implicitly closed before the button. This likely prevents form submission.

2.  **`templates/pages/audit/logs.html`**
    *   **Button:** `<button class="btn btn-outline btn-sm">Export Logs</button>`
    *   **Issue:** No `type` attribute (defaults to `submit`) and not inside a `<form>`. Likely intended to trigger an export action.

3.  **`templates/pages/finance/dashboard.html`**
    *   **Button:** `<button class="btn btn-primary">Fee Calculator</button>`
    *   **Issue:** Orphan button with no apparent function.

## Potential Issues (Implicit Submit Buttons)

These buttons rely on JavaScript but lack `type="button"`, defaulting to `submit`.

*   **`templates/pages/certificates/partials/cert_card.html`**: "Issue Now" button (uses Alpine `@click`).
*   **`templates/components/data_table.html`**: Pagination buttons (`«`, `Page ...`, `»`) are `<button>` tags without a form.
*   **`templates/pages/residents/detail.html`**: "Print Profile" button (uses `onclick`).
*   **`templates/pages/business/list.html`**: "Expiring Soon" and "New Business" buttons (use `onclick`).
