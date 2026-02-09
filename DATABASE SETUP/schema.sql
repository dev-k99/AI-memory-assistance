-- Schema for AI Assistant with Long-Term Memory
-- Compatible with both Local PostgreSQL and Supabase

-- Create extension for UUID generation (optional but recommended)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Chat Message History Table
-- This table stores all chat messages organized by session_id
CREATE TABLE IF NOT EXISTS message_store (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    message JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Index for faster session-based queries
    INDEX idx_session_id (session_id),
    INDEX idx_created_at (created_at)
);

-- Optional: Create a sessions metadata table to track session information
CREATE TABLE IF NOT EXISTS sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    message_count INTEGER DEFAULT 0,
    metadata JSONB
);

-- Function to update last_activity timestamp
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
    
    -- If session doesn't exist, create it
    IF NOT FOUND THEN
        INSERT INTO sessions (session_id, message_count)
        VALUES (NEW.session_id, 1);
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update session metadata
CREATE TRIGGER update_session_on_message
    AFTER INSERT ON message_store
    FOR EACH ROW
    EXECUTE FUNCTION update_session_activity();

-- Grant necessary permissions (adjust as needed for your setup)
-- For Supabase, you may need to adjust these based on your authentication setup
-- GRANT SELECT, INSERT, UPDATE, DELETE ON message_store TO authenticated;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON sessions TO authenticated;

-- View to see session summaries
CREATE OR REPLACE VIEW session_summaries AS
SELECT 
    s.session_id,
    s.created_at,
    s.last_activity,
    s.message_count,
    EXTRACT(EPOCH FROM (s.last_activity - s.created_at)) / 3600 AS duration_hours
FROM sessions s
ORDER BY s.last_activity DESC;

COMMENT ON TABLE message_store IS 'Stores chat message history for AI assistant sessions';
COMMENT ON TABLE sessions IS 'Tracks metadata for chat sessions';
COMMENT ON VIEW session_summaries IS 'Provides quick overview of all chat sessions';