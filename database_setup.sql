-- database_setup.sql

CREATE TABLE IF NOT EXISTS Category (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS Item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER,
    name TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES Category(id)
);

-- Indexes for optimization
CREATE INDEX IF NOT EXISTS idx_category_name ON Category(name);
CREATE INDEX IF NOT EXISTS idx_item_name ON Item(name);
CREATE INDEX IF NOT EXISTS idx_item_category ON Item(category_id);
