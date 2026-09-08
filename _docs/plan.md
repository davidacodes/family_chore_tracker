# Family Chore Tracker Scope

## Product Direction

Build a shared-screen family chore tracker and scheduler for parents and kids. The first version is a local, one-device tool that helps a household set up kids, assign chores to specific days, and track daily completion on a weekly calendar.

## V1 Scope

- Users are parents and kids.
- Everyone uses one shared household screen.
- The tool supports both weekly assignments and daily checkoffs.
- Data is stored locally in the browser on one device.
- Parents enter kid names before chores can be added.
- Parents use a PIN-protected setup/edit mode.
- The PIN protects setup and editing only.
- Kids can mark chores done without entering the PIN.
- Kids can undo a completed chore within the same day.
- Parent approval is not required after a kid marks a chore done.
- The main screen is a full weekly calendar.
- The calendar week starts on Sunday.
- Calendar layout uses days as columns and kids as rows.
- Empty kid/day cells stay visible to keep the grid consistent.
- Chores appear as separate daily checkboxes.
- Chores have due days only, with no due times.
- Missed chores stay missed and do not roll over.
- Chores are assigned manually by parents.
- Parents place chores on specific days manually.
- Each chore belongs to one kid only.
- Setup uses a quick-add flow: chore name, kid, and selected days.
- Chores show chore names only.
- The style should be kid-friendly but not childish.
- Show a simple all-done-today celebration when every chore for the day is complete.
- Completion does not reset automatically each week.
- Keep simple history for the current month.

## Out Of Scope For V1

- Rewards, points, allowance, badges, or streaks.
- Sharing across family devices.
- Printing the weekly schedule.
- Chore categories.
- Chore notes or instructions.
- Automatic chore rotation.
- Repeat presets.
- Multiple kids assigned to the same chore.
- Reordering kids or chores.
- Archiving or hiding old chores.

## Open Product Detail

Clarify during build how weekly completion state should behave with current-month history, since the selected scope says completion does not reset automatically each week while also keeping simple history for the current month.
