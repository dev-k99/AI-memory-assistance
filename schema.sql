-- Chat Message History Table
CREATE TABLE IF NOT EXISTS message_store (
    id BIGSERIAL PRIMARY KEY,
    session_id TEXT NOT NULL,
    message JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_session_id 
ON message_store(session_id);

CREATE INDEX IF NOT EXISTS idx_created_at 
ON message_store(created_at);

-- Sessions Table
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    message_count INTEGER DEFAULT 0,
    metadata JSONB
);

-- Update session metadata
CREATE OR REPLACE FUNCTION update_session_activity()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE sessions
    SET last_activity = CURRENT_TIMESTAMP,
        message_count = (
            SELECT COUNT(*) 
            FROM message_store 
            WHERE session_id = NEW.session_id
        )
    WHERE session_id = NEW.session_id;

    IF NOT FOUND THEN
        INSERT INTO sessions (session_id, message_count)
        VALUES (NEW.session_id, 1);
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_session_on_message
AFTER INSERT ON message_store
FOR EACH ROW
EXECUTE FUNCTION update_session_activity();
