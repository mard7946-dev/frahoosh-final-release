# Student Panel — Parent Flow Alignment

The student panel now follows the same data-flow principle as the parent panel:

- one resolved current student context
- every page reads the canonical school tables for that student
- grades read `grades.student_id`
- assignments read the canonical `assignments` table, including student, class and broadcast assignments
- messages use the same receiver-resolution strategy as the parent panel
- cultural registrations read `student_registrations.student_id`
- reports read `report_cards.student_id`
- attendance reads `attendance.student_id`
- profile reads the student's own `students` row

No shadow `student_assignments` table is created.
