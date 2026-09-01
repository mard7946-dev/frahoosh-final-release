# Frahoosh Final v9 – QA Notes

## Fixed
- Modern PySide6 alignment enum compatibility: `Qt.AlignmentFlag.AlignCenter` used for QLabel alignment calls.
- Parent panel: deferred child selector callback to prevent `PerformanceChart` / `container` initialization race.
- Advisor panel: restored missing `QHBoxLayout` import that caused runtime construction failure.
- Teacher virtual classes: manager/teacher identity matching expanded; active classes created by management are now discoverable by teacher display name, first/last name, email/phone aliases where available.
- Finance accounting form: replaced cramped horizontal rows with a responsive four-column grid and readable controls.
- Finance navigation: consistent vertical green action buttons.
- Smart board: fixed 2x2 card grid, spacing, minimum/maximum card sizes, margins and typography to prevent overlapping content.
- Student panel: fixed-width vertical menu with readable button sizes.

## Validation
- Python compileall: PASS
- SQLite integrity check: PASS (where sqlite3 CLI is available)
- ZIP integrity: checked after packaging

## Important
The environment used to prepare the archive does not include PySide6, so live GUI clicking cannot be performed here. The archive is prepared for the user's Windows/PySide6 runtime test.
