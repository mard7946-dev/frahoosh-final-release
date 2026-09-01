# Frahoosh v15.1 — Panel connection and delete actions

- Staff records whose position is teacher/معلم/دبیر are synchronized into the teachers table.
- teachers.source_staff_id links the teacher record to its originating staff record.
- Executive staff page now has a real delete action with confirmation.
- Deleting a staff member also removes the linked teacher record when present.
- Existing v15 functionality is preserved.

QA:
- Python compile: PASS
- Staff -> teacher sync test: PASS
- Linked delete test: PASS
