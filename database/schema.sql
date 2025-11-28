DROP TABLE IF EXISTS user;
CREATE TABLE user(
    id TEXT PRIMARY KEY, 
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE, 
    profile_pic TEXT NOT NULL DEFAULT 'default.jpg'
);

DROP TABLE IF EXISTS files; 
CREATE TABLE files(
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    user_id TEXT,
    filename TEXT NOT NULL,
    old_name TEXT NOT NULL,
    filepath TEXT NOT NULL
);