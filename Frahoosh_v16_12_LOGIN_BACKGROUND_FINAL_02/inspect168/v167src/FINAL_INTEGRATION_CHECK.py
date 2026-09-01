"""Frahoosh v15.8 final integration smoke checks that do not require Qt."""
from pathlib import Path
import ast, sqlite3
ROOT=Path(__file__).resolve().parent
DB=ROOT/'school.db'
MODULES=['pages.school.panel','pages.education.panel','pages.cultural.panel','executive.panel','advisor.panel','teacher.panel','student.panel','finance.panel','smart_board.panel','ai.panel','pages.parent.panel']
REQUIRED={
 'students':['id','first_name','last_name','student_code','grade','class_name'],
 'teachers':['id','first_name','last_name','phone','email','subject','grades','mobile','lessons','employment_status'],
 'teacher_classes':['id','teacher_id','teacher_name','subject','grade','class_name','active'],
 'lesson_plans':['id','teacher_id','teacher_name','subject','grade','class_name','title','content','session_date','lesson_title','description','plan_date'],
 'messages':['id','sender','receiver','text','created_at'],
 'parent_children':['parent_username','student_id'],
 'student_registrations':['id','student_id','activity_id','activity_title','fee','payment_status','registration_code','registered_at','payment_url'],
 'attendance':['id','student_id','date','status','description'],
}
errors=[]
for mod in MODULES:
 p=ROOT/(mod.replace('.','/')+'.py')
 try:
  tree=ast.parse(p.read_text(encoding='utf-8'))
  names={n.name for n in tree.body if isinstance(n,(ast.ClassDef,ast.FunctionDef))}
  assigns={n.targets[0].id for n in tree.body if isinstance(n,ast.Assign) and n.targets and isinstance(n.targets[0],ast.Name)}
  if 'Panel' not in names and 'Panel' not in assigns: errors.append(f'{mod}: missing Panel entry point')
 except Exception as e: errors.append(f'{mod}: {e}')
con=sqlite3.connect(DB); con.row_factory=sqlite3.Row
for table,cols in REQUIRED.items():
 try: have={r['name'] for r in con.execute(f'PRAGMA table_info({table})')}
 except Exception as e: errors.append(f'{table}: {e}'); continue
 for col in cols:
  if col not in have: errors.append(f'{table}: missing {col}')
# critical query smoke tests
queries=[
 ('teacher list','SELECT id,first_name,last_name,national_code,COALESCE(subject,lessons,"") AS subject,COALESCE(employment_status,"فعال") FROM teachers ORDER BY last_name'),
 ('teacher classes','SELECT id,teacher_id,teacher_name,subject,grade,class_name,active FROM teacher_classes'),
 ('lesson plans','SELECT id,subject,grade,class_name,COALESCE(NULLIF(title,""),lesson_title),COALESCE(NULLIF(session_date,""),plan_date) FROM lesson_plans'),
 ('student messages','SELECT sender,text,created_at,receiver FROM messages ORDER BY id DESC'),
 ('parent links','SELECT p.parent_username,s.id,s.first_name,s.last_name FROM parent_children p JOIN students s ON s.id=p.student_id'),
 ('student activities','SELECT student_id,activity_title,fee,payment_status,registration_code FROM student_registrations'),
]
for name,q in queries:
 try: con.execute(q).fetchall()
 except Exception as e: errors.append(f'{name}: {e}')
con.close()
if errors:
 print('FAIL')
 for e in errors: print('-',e)
 raise SystemExit(1)
print('PASS: routes, required schemas, and critical SQL paths')
