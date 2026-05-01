import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'buitesuite.db')

_SCHEMA = '''
CREATE TABLE IF NOT EXISTS targets (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    hostname   TEXT,
    ip         TEXT,
    os_guess   TEXT,
    notes      TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    last_seen  TEXT
);

CREATE TABLE IF NOT EXISTS commands (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    target      TEXT,
    category    TEXT,
    tool        TEXT,
    command     TEXT,
    output      TEXT DEFAULT '',
    success     INTEGER DEFAULT 0,
    executed_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS notes (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    title      TEXT NOT NULL,
    content    TEXT,
    tags       TEXT DEFAULT '',
    category   TEXT DEFAULT 'General',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tool_stats (
    tool      TEXT PRIMARY KEY,
    category  TEXT,
    use_count INTEGER DEFAULT 0,
    last_used TEXT
);
'''


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(_SCHEMA)
    conn.commit()
    conn.close()


def _conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


# ── Commands ──────────────────────────────────────────────────────────────────

def log_command(target: str, category: str, tool: str, command: str,
                success: bool = False, output: str = ''):
    now = datetime.now().isoformat(timespec='seconds')
    with _conn() as c:
        c.execute(
            'INSERT INTO commands (target, category, tool, command, output, success, executed_at)'
            ' VALUES (?,?,?,?,?,?,?)',
            (target, category, tool, command, output, int(success), now),
        )
        c.execute(
            'INSERT INTO tool_stats (tool, category, use_count, last_used) VALUES (?,?,1,?)'
            ' ON CONFLICT(tool) DO UPDATE SET use_count=use_count+1, last_used=excluded.last_used',
            (tool, category, now),
        )


def get_history(limit: int = 8):
    with _conn() as c:
        return c.execute(
            'SELECT target, category, tool, command, success, executed_at'
            ' FROM commands ORDER BY id DESC LIMIT ?', (limit,)
        ).fetchall()


def get_history_for_tool(tool: str, limit: int = 5):
    with _conn() as c:
        return c.execute(
            'SELECT target, command, success, executed_at'
            ' FROM commands WHERE tool=? ORDER BY id DESC LIMIT ?',
            (tool, limit),
        ).fetchall()


# ── Notes ─────────────────────────────────────────────────────────────────────

def save_note(title: str, content: str, tags: str = '', category: str = 'General'):
    now = datetime.now().isoformat(timespec='seconds')
    with _conn() as c:
        c.execute(
            'INSERT INTO notes (title, content, tags, category, created_at, updated_at)'
            ' VALUES (?,?,?,?,?,?)',
            (title, content, tags, category, now, now),
        )


def update_note(note_id: int, title: str, content: str, tags: str = ''):
    now = datetime.now().isoformat(timespec='seconds')
    with _conn() as c:
        c.execute(
            'UPDATE notes SET title=?, content=?, tags=?, updated_at=? WHERE id=?',
            (title, content, tags, now, note_id),
        )


def delete_note(note_id: int):
    with _conn() as c:
        c.execute('DELETE FROM notes WHERE id=?', (note_id,))


def get_notes(category: str = None, limit: int = 20):
    with _conn() as c:
        if category:
            return c.execute(
                'SELECT id, title, content, tags, created_at FROM notes'
                ' WHERE category=? ORDER BY id DESC LIMIT ?',
                (category, limit),
            ).fetchall()
        return c.execute(
            'SELECT id, title, content, tags, created_at FROM notes'
            ' ORDER BY id DESC LIMIT ?', (limit,)
        ).fetchall()


# ── Stats ─────────────────────────────────────────────────────────────────────

def get_top_tools(limit: int = 5):
    with _conn() as c:
        return c.execute(
            'SELECT tool, category, use_count FROM tool_stats'
            ' ORDER BY use_count DESC LIMIT ?', (limit,)
        ).fetchall()


def get_stats():
    with _conn() as c:
        n_cmds    = c.execute('SELECT COUNT(*) FROM commands').fetchone()[0]
        n_targets = c.execute('SELECT COUNT(DISTINCT target) FROM commands WHERE target != ""').fetchone()[0]
        n_notes   = c.execute('SELECT COUNT(*) FROM notes').fetchone()[0]
        n_tools   = c.execute('SELECT COUNT(*) FROM tool_stats').fetchone()[0]
    return {'commands': n_cmds, 'targets': n_targets, 'notes': n_notes, 'tools_used': n_tools}


# ── Targets ───────────────────────────────────────────────────────────────────

def add_target(hostname: str = '', ip: str = '', os_guess: str = '', notes: str = ''):
    now = datetime.now().isoformat(timespec='seconds')
    with _conn() as c:
        c.execute(
            'INSERT INTO targets (hostname, ip, os_guess, notes, last_seen) VALUES (?,?,?,?,?)',
            (hostname, ip, os_guess, notes, now),
        )


def get_targets(limit: int = 10):
    with _conn() as c:
        return c.execute(
            'SELECT hostname, ip, os_guess, last_seen FROM targets ORDER BY id DESC LIMIT ?',
            (limit,),
        ).fetchall()
