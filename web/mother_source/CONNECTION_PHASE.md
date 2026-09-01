Frahoosh - Connection Phase 1

Base: v14.5

Implemented:
- Central identity/data linkage service: services/data_link_service.py
- users table now supports linked_student_id, linked_teacher_id, linked_staff_id and display_name
- AuthService resolves linked domain records at login
- Dashboard passes linked student identity to the student panel
- Dashboard resolves the real teacher name for the teacher panel
- Student panel now builds its stacked pages when opened from the main dashboard
- Core student/teacher/online-class modules use the canonical school.db path
- Parent-child linkage remains in the central school.db and supports multi-child records

Verification:
- Python compileall: PASS
- Database schema migration: PASS
- Student user -> student record resolution: PASS
- Parent -> child linkage smoke test: PASS

Next phase:
- Full cross-panel business-flow testing
- Server/API synchronization
- Final Web/EXE/APK packaging
