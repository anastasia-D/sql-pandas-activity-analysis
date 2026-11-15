import sqlite3
from datetime import UTC, datetime, timedelta

TASKS = ('task_04', 'task_04b', 'task_05', 'task_06', 'task_06b', 'project')


def connect_demo() -> sqlite3.Connection:
    """Create an in-memory SQLite database with fictional activity events."""
    connection = sqlite3.connect(':memory:')
    connection.executescript("""
        CREATE TABLE pageviews (uid TEXT NOT NULL, datetime TEXT NOT NULL);
        CREATE TABLE checker (
            uid TEXT NOT NULL,
            labname TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            status TEXT NOT NULL,
            numTrials INTEGER NOT NULL
        );
        CREATE TABLE deadlines (labs TEXT PRIMARY KEY, deadlines INTEGER NOT NULL);
    """)

    first_deadline = datetime(2025, 1, 10, 18)
    deadlines = {
        name: first_deadline + timedelta(days=offset)
        for offset, name in enumerate(TASKS)
    }
    with connection:
        connection.executemany(
            'INSERT INTO deadlines VALUES (?, ?)',
            [(name, int(date.replace(tzinfo=UTC).timestamp()))
             for name, date in deadlines.items()],
        )
        for number in range(1, 17):
            uid = f'user_{number:02d}'
            events = [
                (uid, name, (deadline - timedelta(hours=3 + (number * offset) % 23)),
                 'ready', 1)
                for offset, (name, deadline) in enumerate(deadlines.items(), 1)
            ]
            connection.executemany('INSERT INTO checker VALUES (?, ?, ?, ?, ?)', events)
            connection.execute(
                'INSERT INTO checker VALUES (?, ?, ?, ?, ?)',
                (uid, TASKS[0], first_deadline, 'ready', 2),
            )
            if number <= 10:
                first_view = first_deadline + timedelta(days=2, hours=number % 3)
                views = [
                    (uid, first_view + timedelta(hours=offset))
                    for offset in range(1 + (number * 3) % 8)
                ]
                connection.executemany('INSERT INTO pageviews VALUES (?, ?)', views)
        connection.execute('INSERT INTO pageviews VALUES (?, ?)', ('staff', first_deadline))
    return connection
