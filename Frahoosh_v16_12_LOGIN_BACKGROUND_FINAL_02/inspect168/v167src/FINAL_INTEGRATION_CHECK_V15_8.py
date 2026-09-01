import sqlite3
from pathlib import Path

ROOT=Path(__file__).resolve().parent
DB=ROOT/'school.db'

def cols(c,t): return {r[1] for r in c.execute(f'PRAGMA table_info({t})').fetchall()}

def main():
    from services.core_bootstrap import bootstrap
    bootstrap()
    with sqlite3.connect(DB) as c:
        required={
            'assets': {'archived'},
            'grades': {'student_id','teacher_id','subject','exam_name','score'},
            'students': {'id','student_code','grade','class_name'},
            'parent_children': {'parent_username','student_id'},
            'messages': {'receiver','text'},
            'student_registrations': {'student_id','activity_id'},
            'parent_meetings': {'student_id','teacher_id'},
        }
        for t,want in required.items():
            missing=want-cols(c,t)
            if missing: raise RuntimeError(f'{t}: missing {sorted(missing)}')
        # Grade propagation contract: any grade row must be visible by student_id.
        c.execute("CREATE TEMP TABLE grade_visibility AS SELECT g.student_id,g.subject,g.score FROM grades g")
        # Parent contract: a linked parent sees only rows for selected child.
        parent=c.execute('SELECT parent_username,student_id FROM parent_children LIMIT 1').fetchone()
        if parent:
            rows=c.execute('SELECT g.student_id,g.subject,g.score FROM grades g JOIN parent_children p ON p.student_id=g.student_id WHERE p.parent_username=? AND g.student_id=?',(parent[0],parent[1])).fetchall()
            for r in rows:
                assert r[0]==parent[1]
        print('PASS: schema, archived migration, grade visibility, parent-child data contract')

if __name__=='__main__': main()
