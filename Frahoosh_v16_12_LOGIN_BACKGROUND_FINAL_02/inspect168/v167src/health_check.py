import sqlite3, importlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent; DB=ROOT/'school.db'
REQUIRED=['users','students','teachers','staff','weekly_schedule','exam_schedule','quiz_questions','parent_meetings','attendance','grades','assignments','messages','online_classes','online_quizzes','school_requests','school_settings','virtual_server_config']
IMPORTS=['pages.school.panel','pages.education.panel','pages.executive.panel','executive.dashboard','advisor.panel','teacher.panel','student.panel','finance.panel','smart_board.panel','ai.panel','pages.school.settings']
print('DB:',DB)
with sqlite3.connect(DB) as c:
    tables={r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")}
missing=[x for x in REQUIRED if x not in tables]
print('MISSING TABLES:',missing)
for m in IMPORTS:
    try: importlib.import_module(m); print('IMPORT OK:',m)
    except Exception as e: print('IMPORT FAIL:',m,repr(e))
raise SystemExit(1 if missing else 0)
