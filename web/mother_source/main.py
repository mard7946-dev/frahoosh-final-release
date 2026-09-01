# ============================================================
# Frahoosh - Main
# فایل اصلی اجرای برنامه
# ============================================================

import sys

from PySide6.QtWidgets import QApplication
from qt_material import apply_stylesheet

from database.db import create_tables, get_connection
from services.core_bootstrap import bootstrap
from ui.login import Login

from utils.theme import FARAHOOSH_THEME
from ui.theme import apply_theme

from finance.finance_db import create_finance_tables
from smart_board.smart_board_db import create_smart_board_tables
from database.ai_db import create_ai_tables
from database.settings_db import create_settings_tables
from database.complete_schema import create_complete_schema


# FRAHOOSH_V16_12_OPERATIONAL_FINAL_ROUTING
def ensure_operational_final_schema():
    import sqlite3
    from pathlib import Path
    db_path=Path(__file__).resolve().parent/'school.db'
    c=sqlite3.connect(db_path)
    c.executescript("""
    CREATE TABLE IF NOT EXISTS executive_operations(id INTEGER PRIMARY KEY AUTOINCREMENT,operation_type TEXT,title TEXT,student_id INTEGER,class_name TEXT,status TEXT,operation_date TEXT,description TEXT);
    CREATE TABLE IF NOT EXISTS executive_reports(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT,report_type TEXT,student_id INTEGER,class_name TEXT,report_date TEXT,created_by TEXT);
    CREATE TABLE IF NOT EXISTS teacher_exams(id INTEGER PRIMARY KEY AUTOINCREMENT,teacher_id INTEGER,title TEXT,subject TEXT,grade TEXT,class_name TEXT,exam_type TEXT,exam_date TEXT,duration TEXT);
    CREATE TABLE IF NOT EXISTS smart_board_whiteboards(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT,content TEXT,class_id INTEGER,teacher_id INTEGER,board_date TEXT);
    CREATE TABLE IF NOT EXISTS smart_board_interactive_tools(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT,tool_type TEXT,description TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
    """)
    c.commit(); c.close()



# ============================================================
# ساخت برنامه
# ============================================================

app = QApplication(sys.argv)
ensure_operational_final_schema()

print("APP START")


# ============================================================
# اعمال تم اولیه
# ============================================================

apply_theme(app)

print(app.styleSheet())


# ============================================================
# ساخت جدول‌های دیتابیس
# ============================================================

create_tables()
bootstrap()

create_finance_tables()

create_smart_board_tables()
create_ai_tables()
create_settings_tables()
create_complete_schema()


# ============================================================
# اتصال دیتابیس فرهنگی
# ============================================================

try:

    from database.cultural_db import create_cultural_tables

    create_cultural_tables()

    print("CULTURAL DATABASE OK")

except ImportError:

    print(
        "WARNING: cultural_db.py not found"
    )

except Exception as e:

    print(
        "CULTURAL DATABASE ERROR:",
        e
    )


# ============================================================
# بررسی جداول دیتابیس
# ============================================================

conn = get_connection()

cursor = conn.cursor()

cursor.execute("""
    SELECT
        name
    FROM sqlite_master
    WHERE type='table'
    ORDER BY name
""")

tables = cursor.fetchall()

print("DATABASE TABLES:")

for table in tables:

    print(
        "TABLE:",
        table[0]
    )

conn.close()

print("DATABASE OK")


# ============================================================
# اعمال قالب Material
# ============================================================

apply_stylesheet(
    app,
    theme="light_blue.xml"
)

print("THEME OK")


# ============================================================
# استایل اختصاصی فراهوش
# ============================================================

app.setStyleSheet(

    FARAHOOSH_THEME

    +

    """
    /* ---------- ورودی ها ---------- */

    QLineEdit,
    QTextEdit,
    QPlainTextEdit,
    QComboBox {

        background-color: #ffffff;
        color: #111827;
        border: 1px solid #94a3b8;
        border-radius: 7px;
        padding: 4px 7px;
        min-height: 24px;
    }


    /* ---------- کارت ها ---------- */

    QGroupBox {

        background-color: #FFE0B2;

        color: #111827;

        border: 2px solid #F57C00;

        border-radius: 10px;

        font-weight: bold;
    }


    /* ---------- دکمه ها ---------- */

    QPushButton {

        background-color: #2563eb;
        color: #ffffff;
        border: 1px solid #1d4ed8;
        border-radius: 7px;
        padding: 3px 8px;
        min-height: 26px;
        max-height: 32px;
        min-width: 70px;
        font-size: 12px;
        font-weight: bold;
    }


    QPushButton:hover {

        background-color: #1d4ed8;

        color: #111827;
    }


    QPushButton:pressed {

        background-color: #1e40af;

        color: #111827;
    }


    QPushButton:disabled {

        background-color: #D7CCC8;

        color: #666666;
    }


    /* ---------- متن ها ---------- */

    QLabel {

        color: #111827;
    }

    """
)


# ============================================================
# شروع برنامه
# ============================================================

print("OPEN LOGIN")

window = Login()

window.show()


# ============================================================
# اجرای برنامه
# ============================================================

sys.exit(
    app.exec()
)
