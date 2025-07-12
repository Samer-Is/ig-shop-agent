-- Enterprise-Level Row-Level Security (RLS) Implementation
-- This ensures database-level multi-tenant isolation even if application code fails

-- Enable RLS on all tenant-specific tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE catalog_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE kb_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE business_rules ENABLE ROW LEVEL SECURITY;

-- Create application role for normal operations
CREATE ROLE app_user;
GRANT CONNECT ON DATABASE igshop_db TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;

-- Create admin role that can bypass RLS
CREATE ROLE admin_user;
GRANT CONNECT ON DATABASE igshop_db TO admin_user;
GRANT USAGE ON SCHEMA public TO admin_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin_user;

-- Function to get current user ID from application context
CREATE OR REPLACE FUNCTION get_current_user_id() RETURNS text AS $$
BEGIN
    -- Get user_id from application context set by middleware
    RETURN current_setting('app.current_user_id', true);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- RLS Policies for users table (users can only see their own record)
CREATE POLICY users_isolation_policy ON users
    FOR ALL TO app_user
    USING (id = get_current_user_id());

-- RLS Policies for catalog_items table
CREATE POLICY catalog_items_isolation_policy ON catalog_items
    FOR ALL TO app_user
    USING (user_id = get_current_user_id());

-- RLS Policies for orders table
CREATE POLICY orders_isolation_policy ON orders
    FOR ALL TO app_user
    USING (user_id = get_current_user_id());

-- RLS Policies for conversations table
CREATE POLICY conversations_isolation_policy ON conversations
    FOR ALL TO app_user
    USING (user_id = get_current_user_id());

-- RLS Policies for kb_documents table
CREATE POLICY kb_documents_isolation_policy ON kb_documents
    FOR ALL TO app_user
    USING (user_id = get_current_user_id());

-- RLS Policies for business_rules table
CREATE POLICY business_rules_isolation_policy ON business_rules
    FOR ALL TO app_user
    USING (user_id = get_current_user_id());

-- Admin bypass policies (admins can see all data)
CREATE POLICY admin_bypass_policy ON users
    FOR ALL TO admin_user
    USING (true);

CREATE POLICY admin_bypass_policy ON catalog_items
    FOR ALL TO admin_user
    USING (true);

CREATE POLICY admin_bypass_policy ON orders
    FOR ALL TO admin_user
    USING (true);

CREATE POLICY admin_bypass_policy ON conversations
    FOR ALL TO admin_user
    USING (true);

CREATE POLICY admin_bypass_policy ON kb_documents
    FOR ALL TO admin_user
    USING (true);

CREATE POLICY admin_bypass_policy ON business_rules
    FOR ALL TO admin_user
    USING (true);

-- Create audit log table for compliance
CREATE TABLE IF NOT EXISTS audit_log (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    action TEXT NOT NULL,
    table_name TEXT NOT NULL,
    record_id TEXT,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS on audit log (users can only see their own audit entries)
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY audit_log_isolation_policy ON audit_log
    FOR SELECT TO app_user
    USING (user_id = get_current_user_id());

-- Admin can see all audit logs
CREATE POLICY audit_log_admin_policy ON audit_log
    FOR ALL TO admin_user
    USING (true);

-- Create function to log data changes
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    -- Insert audit record
    INSERT INTO audit_log (user_id, action, table_name, record_id, old_values, new_values)
    VALUES (
        get_current_user_id(),
        TG_OP,
        TG_TABLE_NAME,
        CASE 
            WHEN TG_OP = 'DELETE' THEN OLD.id
            ELSE NEW.id
        END,
        CASE 
            WHEN TG_OP = 'DELETE' THEN row_to_json(OLD)
            WHEN TG_OP = 'UPDATE' THEN row_to_json(OLD)
            ELSE NULL
        END,
        CASE 
            WHEN TG_OP = 'INSERT' THEN row_to_json(NEW)
            WHEN TG_OP = 'UPDATE' THEN row_to_json(NEW)
            ELSE NULL
        END
    );
    
    RETURN CASE 
        WHEN TG_OP = 'DELETE' THEN OLD
        ELSE NEW
    END;
END;
$$ LANGUAGE plpgsql;

-- Create audit triggers for all tenant tables
CREATE TRIGGER catalog_items_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON catalog_items
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER orders_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON orders
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER conversations_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON conversations
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER kb_documents_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON kb_documents
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER business_rules_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON business_rules
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_created_at ON audit_log(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_log_table_name ON audit_log(table_name);

-- Create data retention policy (GDPR compliance)
CREATE OR REPLACE FUNCTION cleanup_old_data()
RETURNS void AS $$
BEGIN
    -- Delete conversations older than 30 days (GDPR requirement)
    DELETE FROM conversations 
    WHERE created_at < NOW() - INTERVAL '30 days';
    
    -- Delete audit logs older than 7 years (compliance requirement)
    DELETE FROM audit_log 
    WHERE created_at < NOW() - INTERVAL '7 years';
    
    -- Log cleanup action
    INSERT INTO audit_log (user_id, action, table_name, record_id, new_values)
    VALUES ('SYSTEM', 'CLEANUP', 'conversations', NULL, 
            json_build_object('retention_days', 30, 'cleaned_at', NOW()));
END;
$$ LANGUAGE plpgsql;

-- Create usage tracking table for billing
CREATE TABLE IF NOT EXISTS usage_metrics (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    metric_type TEXT NOT NULL, -- 'api_calls', 'storage_mb', 'ai_tokens', etc.
    metric_value BIGINT NOT NULL,
    period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS on usage metrics
ALTER TABLE usage_metrics ENABLE ROW LEVEL SECURITY;

CREATE POLICY usage_metrics_isolation_policy ON usage_metrics
    FOR ALL TO app_user
    USING (user_id = get_current_user_id());

CREATE POLICY usage_metrics_admin_policy ON usage_metrics
    FOR ALL TO admin_user
    USING (true);

-- Create rate limiting table
CREATE TABLE IF NOT EXISTS rate_limits (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    endpoint TEXT NOT NULL,
    requests_count INTEGER NOT NULL DEFAULT 0,
    window_start TIMESTAMP WITH TIME ZONE NOT NULL,
    window_end TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, endpoint, window_start)
);

-- Enable RLS on rate limits
ALTER TABLE rate_limits ENABLE ROW LEVEL SECURITY;

CREATE POLICY rate_limits_isolation_policy ON rate_limits
    FOR ALL TO app_user
    USING (user_id = get_current_user_id());

-- Create data encryption functions
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Function to encrypt sensitive data
CREATE OR REPLACE FUNCTION encrypt_sensitive_data(data TEXT, key TEXT DEFAULT 'default_key')
RETURNS TEXT AS $$
BEGIN
    RETURN encode(encrypt(data::bytea, key::bytea, 'aes'), 'base64');
END;
$$ LANGUAGE plpgsql;

-- Function to decrypt sensitive data
CREATE OR REPLACE FUNCTION decrypt_sensitive_data(encrypted_data TEXT, key TEXT DEFAULT 'default_key')
RETURNS TEXT AS $$
BEGIN
    RETURN convert_from(decrypt(decode(encrypted_data, 'base64'), key::bytea, 'aes'), 'UTF8');
END;
$$ LANGUAGE plpgsql;

-- Grant necessary permissions
GRANT EXECUTE ON FUNCTION get_current_user_id() TO app_user;
GRANT EXECUTE ON FUNCTION encrypt_sensitive_data(TEXT, TEXT) TO app_user;
GRANT EXECUTE ON FUNCTION decrypt_sensitive_data(TEXT, TEXT) TO app_user;
GRANT EXECUTE ON FUNCTION cleanup_old_data() TO admin_user;

-- Create scheduled cleanup job (requires pg_cron extension)
-- SELECT cron.schedule('cleanup-old-data', '0 2 * * *', 'SELECT cleanup_old_data();');

COMMENT ON TABLE audit_log IS 'Enterprise audit trail for compliance and security monitoring';
COMMENT ON TABLE usage_metrics IS 'Usage tracking for billing and quota management';
COMMENT ON TABLE rate_limits IS 'Rate limiting data for API throttling';
COMMENT ON FUNCTION get_current_user_id() IS 'Gets current user ID from application context for RLS';
COMMENT ON FUNCTION cleanup_old_data() IS 'GDPR-compliant data retention cleanup'; 