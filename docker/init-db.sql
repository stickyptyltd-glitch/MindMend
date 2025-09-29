-- MindMend Database Initialization Script
-- ========================================

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create additional database user for backups
CREATE USER mindmend_backup WITH PASSWORD 'backup_password_change_me';
GRANT CONNECT ON DATABASE mindmend_production TO mindmend_backup;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO mindmend_backup;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO mindmend_backup;

-- Create audit logging function
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_log (table_name, operation, row_data, changed_by, changed_at)
        VALUES (TG_TABLE_NAME, TG_OP, row_to_json(NEW), current_user, current_timestamp);
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_log (table_name, operation, row_data, old_data, changed_by, changed_at)
        VALUES (TG_TABLE_NAME, TG_OP, row_to_json(NEW), row_to_json(OLD), current_user, current_timestamp);
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_log (table_name, operation, old_data, changed_by, changed_at)
        VALUES (TG_TABLE_NAME, TG_OP, row_to_json(OLD), current_user, current_timestamp);
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Create audit log table
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    operation TEXT NOT NULL,
    row_data JSONB,
    old_data JSONB,
    changed_by TEXT NOT NULL,
    changed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_audit_log_table_name ON audit_log(table_name);
CREATE INDEX IF NOT EXISTS idx_audit_log_changed_at ON audit_log(changed_at);
CREATE INDEX IF NOT EXISTS idx_audit_log_operation ON audit_log(operation);

-- HIPAA Compliance: Create session tracking table
CREATE TABLE IF NOT EXISTS hipaa_session_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    session_id VARCHAR(255) NOT NULL,
    ip_address INET NOT NULL,
    user_agent TEXT,
    login_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    logout_time TIMESTAMP WITH TIME ZONE,
    session_duration INTERVAL,
    actions_performed INTEGER DEFAULT 0,
    data_accessed TEXT[],
    compliance_flags JSONB DEFAULT '{}'::jsonb
);

-- Create indexes for session tracking
CREATE INDEX IF NOT EXISTS idx_hipaa_session_user_id ON hipaa_session_log(user_id);
CREATE INDEX IF NOT EXISTS idx_hipaa_session_login_time ON hipaa_session_log(login_time);
CREATE INDEX IF NOT EXISTS idx_hipaa_session_ip ON hipaa_session_log(ip_address);

-- Data retention policy function
CREATE OR REPLACE FUNCTION cleanup_old_audit_logs()
RETURNS void AS $$
BEGIN
    -- Delete audit logs older than 7 years (HIPAA requirement)
    DELETE FROM audit_log WHERE changed_at < NOW() - INTERVAL '7 years';
    
    -- Delete session logs older than 7 years
    DELETE FROM hipaa_session_log WHERE login_time < NOW() - INTERVAL '7 years';
END;
$$ LANGUAGE plpgsql;

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO mindmend_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO mindmend_user;
GRANT EXECUTE ON FUNCTION audit_trigger_function() TO mindmend_user;
GRANT EXECUTE ON FUNCTION cleanup_old_audit_logs() TO mindmend_user;