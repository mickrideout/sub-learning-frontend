# Database Schema

```sql
-- Existing Schema (provided by user)
CREATE TABLE IF NOT EXISTS languages (
    id SMALLINT PRIMARY KEY,
    name TEXT,
    display_name TEXT,
    code TEXT
);

CREATE TABLE IF NOT EXISTS sub_titles (
    id INTEGER PRIMARY KEY,
    title TEXT
);

CREATE TABLE IF NOT EXISTS sub_lines (
    id INTEGER PRIMARY KEY,
    lineid SMALLINT,
    content TEXT
);

CREATE TABLE IF NOT EXISTS sub_links (
    id INTEGER PRIMARY KEY,
    fromid INTEGER,
    fromlang SMALLINT,
    toid INTEGER,
    tolang SMALLINT,
    FOREIGN KEY (fromid) REFERENCES sub_titles(id),
    FOREIGN KEY (toid) REFERENCES sub_titles(id),
    FOREIGN KEY (fromlang) REFERENCES languages(id),
    FOREIGN KEY (tolang) REFERENCES languages(id)
);

CREATE TABLE IF NOT EXISTS sub_link_lines (
    sub_link_id INTEGER,
    link_data JSONB,
    FOREIGN KEY (sub_link_id) REFERENCES sub_links(id),
    PRIMARY KEY (sub_link_id)
);

-- New User Management Schema
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT,
    oauth_provider TEXT,
    oauth_id TEXT,
    native_language_id SMALLINT,
    target_language_id SMALLINT,
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (native_language_id) REFERENCES languages(id),
    FOREIGN KEY (target_language_id) REFERENCES languages(id),
    UNIQUE(oauth_provider, oauth_id)
);

CREATE TABLE IF NOT EXISTS user_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    sub_link_id INTEGER NOT NULL,
    current_alignment_index INTEGER DEFAULT 0,
    total_alignments_completed INTEGER DEFAULT 0,
    session_duration_minutes INTEGER DEFAULT 0,
    last_accessed DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (sub_link_id) REFERENCES sub_links(id) ON DELETE CASCADE,
    UNIQUE(user_id, sub_link_id)
);

CREATE TABLE IF NOT EXISTS bookmarks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    sub_link_id INTEGER NOT NULL,
    alignment_index INTEGER NOT NULL,
    note TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (sub_link_id) REFERENCES sub_links(id) ON DELETE CASCADE,
    UNIQUE(user_id, sub_link_id, alignment_index)
);

-- Performance Optimization Indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_oauth ON users(oauth_provider, oauth_id);
CREATE INDEX IF NOT EXISTS idx_users_languages ON users(native_language_id, target_language_id);

CREATE INDEX IF NOT EXISTS idx_sub_titles_title ON sub_titles(title);
CREATE INDEX IF NOT EXISTS idx_sub_links_languages ON sub_links(fromlang, tolang);
CREATE INDEX IF NOT EXISTS idx_sub_links_from ON sub_links(fromid, fromlang);
CREATE INDEX IF NOT EXISTS idx_sub_links_to ON sub_links(toid, tolang);

CREATE INDEX IF NOT EXISTS idx_user_progress_user ON user_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_user_progress_link ON user_progress(sub_link_id);
CREATE INDEX IF NOT EXISTS idx_user_progress_accessed ON user_progress(last_accessed);

CREATE INDEX IF NOT EXISTS idx_bookmarks_user ON bookmarks(user_id);
CREATE INDEX IF NOT EXISTS idx_bookmarks_link ON bookmarks(sub_link_id);
CREATE INDEX IF NOT EXISTS idx_bookmarks_active ON bookmarks(user_id, is_active);

-- SQLite-specific optimizations
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = 10000;
PRAGMA temp_store = memory;
PRAGMA mmap_size = 268435456; -- 256MB
```
