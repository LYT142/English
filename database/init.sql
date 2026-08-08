CREATE TABLE IF NOT EXISTS learning_events (
    id SERIAL PRIMARY KEY,
    exercise_id INTEGER NOT NULL,
    answer TEXT NOT NULL,
    score INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
