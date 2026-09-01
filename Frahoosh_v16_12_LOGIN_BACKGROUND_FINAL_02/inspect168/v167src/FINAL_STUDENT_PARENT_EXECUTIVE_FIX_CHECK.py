import sqlite3
from pathlib import Path
DB=Path(__file__).resolve().parent/"school.db"
def cols(c,t): return {r[1] for r in c.execute(f"PRAGMA table_info({t})").fetchall()}
def main():
 c=sqlite3.connect(DB)
 required={"users":{"role"},"staff":{"role"},"assets":{"archived"},"executive_requests":{"role"},"grades":{"student_id","teacher_id","subject","exam_name","score","created_at"},"assignments":{"student_id","teacher_id","title","class_name","subject","created_at"},"messages":{"receiver","text","created_at"},"parent_children":{"parent_username","student_id"}}
 for t,need in required.items():
  missing=need-cols(c,t); assert not missing,(t,missing)
 c.execute("SELECT id,title,requester,role,description,status,created_at FROM executive_requests ORDER BY id DESC LIMIT 1").fetchall()
 sid=c.execute("SELECT id FROM students ORDER BY id LIMIT 1").fetchone()
 if sid:
  sid=sid[0]; c.execute("SELECT * FROM grades WHERE student_id=?",(sid,)).fetchall(); c.execute("SELECT * FROM assignments WHERE student_id=? OR student_id IS NULL OR student_id=0",(sid,)).fetchall()
 c.close(); print("FINAL STUDENT/PARENT/EXECUTIVE FLOW CHECK: PASS")
if __name__=="__main__": main()
