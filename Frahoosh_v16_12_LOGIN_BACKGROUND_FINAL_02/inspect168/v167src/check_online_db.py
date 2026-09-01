import sqlite3

conn = sqlite3.connect("school.db")
cursor = conn.cursor()

for table in [
    "online_classes",
    "online_attendance",
    "online_quizzes"
]:
    print("\nTABLE:", table)

    cursor.execute(
        f"PRAGMA table_info({table})"
    )

    for column in cursor.fetchall():
        print(column)

conn.close()