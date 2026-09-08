# Family Chore Tracker Backlog

## 1. Set Up Empty Django Project
Goal: Create an empty Django project with a passing test.
Description: Initialize the Django project structure, configure SQLite for local development, and add a minimal app suitable for the chore tracker domain. Add one smoke test that passes through the project test runner so future tasks have a verified baseline.

## 2. Add Base Layout And Static Asset Pipeline
Goal: Create the shared page shell used by all screens.
Description: Add a base Django template, static CSS entry point, and basic responsive layout structure for a shared household screen. Include HTMX in the base template so later tasks can add partial updates without changing the global layout.

## 3. Model Kids
Goal: Store household kids in the database.
Description: Add a Kid model with the fields needed for V1, such as name and creation order. Include migrations, admin registration if useful, and tests for basic creation and display ordering.

## 4. Build Kid Setup Flow
Goal: Let parents add kid names before chores are created.
Description: Create a parent-facing setup screen for adding kids and listing existing kids. The flow should validate that names are present and should make it clear when no kids have been added yet.

## 5. Add Parent PIN State
Goal: Support PIN-protected setup and edit mode.
Description: Add storage for a household parent PIN and implement session state for whether the current browser is in parent mode. This task should cover setting the initial PIN, entering parent mode, leaving parent mode, and tests for protected view access.

## 6. Model Chores And Weekly Due Days
Goal: Store chores assigned to one kid on selected days of the week.
Description: Add a Chore model associated with a single Kid and a representation of Sunday-through-Saturday due days. Include validation that each chore has a name, a kid, and at least one due day.

## 7. Build Quick-Add Chore Flow
Goal: Let parents create chores with a name, kid, and selected due days.
Description: Create a PIN-protected form for adding chores using the quick-add fields from the product scope. The form should list available kids, present day-of-week selection, save valid chores, and show useful validation errors.

## 8. Render Weekly Calendar Grid
Goal: Show the main weekly calendar with days as columns and kids as rows.
Description: Build the main screen around a Sunday-starting weekly grid. Every kid/day cell should remain visible even when there are no chores, and chores should appear in the matching kid/day cell by name.

## 9. Add Date Navigation For Weeks
Goal: Let the household view the current week and move between weeks.
Description: Add server-side week calculation using concrete dates, with Sunday as the start of each week. Provide previous week, current week, and next week navigation while keeping the calendar layout stable.

## 10. Track Daily Chore Completion
Goal: Let kids mark a chore done for a specific calendar date.
Description: Add a completion model keyed by chore and concrete date so history is separate from reusable weekly assignments. Implement checkbox behavior for marking chores complete from the main calendar without requiring parent PIN entry.

## 11. Support Same-Day Undo
Goal: Let kids undo a completed chore only on the same day.
Description: Add rules that allow completion to be removed when the completion date is today. Past dates should remain read-only from the kid-facing calendar, with tests covering allowed and blocked undo behavior.

## 12. Add HTMX Calendar Updates
Goal: Update chore checkboxes without a full page reload.
Description: Convert completion and undo actions to HTMX requests that replace the affected chore, day cell, or calendar summary. Preserve non-HTMX fallbacks so the behavior still works with a normal form post.

## 13. Show All-Done-Today Celebration
Goal: Celebrate when every chore due today is complete.
Description: Add logic to detect when all chores scheduled for the current date are completed. Display a simple kid-friendly but not childish celebration on the main screen, and make sure it appears or disappears after HTMX updates.

## 14. Add Current-Month History View
Goal: Show simple completion history for the current month.
Description: Create a parent-accessible history view summarizing completed and missed chores for dates in the current month. Use concrete completion dates and scheduled due days so missed chores do not roll over into future dates.

## 15. Add Parent Edit And Delete Controls
Goal: Let parents maintain kids and chores after initial setup.
Description: Add PIN-protected edit and delete actions for kids and chores. Keep the controls out of the kid-facing default mode, and protect the server endpoints so editing cannot happen without parent mode.

## 16. Polish Responsive Shared-Screen UI
Goal: Make the app usable and visually appropriate on a household screen.
Description: Refine the calendar, setup forms, buttons, empty states, and celebration styling. The visual style should be friendly for kids without looking childish, and the calendar should remain readable on tablet and desktop widths.

## 17. Add End-To-End Workflow Tests
Goal: Verify the core V1 household workflow.
Description: Add integration tests for creating kids, setting or entering the parent PIN, adding chores, viewing the weekly calendar, completing chores, undoing same-day completions, and seeing monthly history. These tests should cover the highest-risk user paths rather than every visual detail.

## 18. Document Local Run And Test Commands
Goal: Give future contributors a concise way to run the app.
Description: Add project documentation with setup, database migration, development server, and test commands. Include any assumptions about local-only SQLite usage and the difference between parent mode and kid-facing chore completion.
