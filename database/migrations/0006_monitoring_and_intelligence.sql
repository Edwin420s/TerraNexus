-- 0006_monitoring_and_intelligence.sql
-- Monitoring, Rules, Alerts, Notifications, Agronomic Intelligence, Recommendations, and Model Governance
-- Aligned with TNX-DATA-001 Sections 12 & 14 and TNX-ARCH-001 Section 10

CREATE TABLE IF NOT EXISTS alert_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organisation_id UUID NOT NULL REFERENCES organisations(id) ON DELETE CASCADE,
    farm_id UUID NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    field_id UUID REFERENCES fields(id) ON DELETE CASCADE,
    name VARCHAR(150) NOT NULL,
    rule_type VARCHAR(50) NOT NULL, -- threshold_min, threshold_max, range, rate_of_change, device_offline, anomaly
    measurement_type VARCHAR(50) REFERENCES measurement_types(code),
    conditions JSONB NOT NULL, -- e.g. {"operator": "<", "threshold": 25.0, "duration_minutes": 30}
    severity VARCHAR(20) NOT NULL DEFAULT 'warning' CHECK (severity IN ('info', 'warning', 'critical', 'emergency')),
    cooldown_minutes INTEGER NOT NULL DEFAULT 60,
    channels JSONB NOT NULL DEFAULT '["in_app"]'::jsonb, -- in_app, email, sms, webhook
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organisation_id UUID NOT NULL REFERENCES organisations(id) ON DELETE CASCADE,
    farm_id UUID NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    field_id UUID REFERENCES fields(id) ON DELETE SET NULL,
    device_id UUID REFERENCES devices(id) ON DELETE SET NULL,
    alert_rule_id UUID REFERENCES alert_rules(id) ON DELETE SET NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('info', 'warning', 'critical', 'emergency')),
    status VARCHAR(30) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'acknowledged', 'resolved', 'silenced')),
    triggered_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    acknowledged_at TIMESTAMPTZ,
    acknowledged_by UUID REFERENCES users(id),
    resolved_at TIMESTAMPTZ,
    resolved_by UUID REFERENCES users(id),
    resolution_notes TEXT,
    context_data JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_alerts_farm_status ON alerts(farm_id, status);
CREATE INDEX IF NOT EXISTS idx_alerts_triggered ON alerts(triggered_at DESC);

CREATE TABLE IF NOT EXISTS alert_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    alert_id UUID NOT NULL REFERENCES alerts(id) ON DELETE CASCADE,
    action VARCHAR(50) NOT NULL, -- triggered, notified, acknowledged, escalated, resolved
    actor_id UUID REFERENCES users(id),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organisation_id UUID NOT NULL REFERENCES organisations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    alert_id UUID REFERENCES alerts(id) ON DELETE SET NULL,
    title VARCHAR(200) NOT NULL,
    body TEXT NOT NULL,
    category VARCHAR(50) NOT NULL DEFAULT 'alert', -- alert, recommendation, task, system, security
    link_url TEXT,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    read_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id, is_read, created_at DESC);

CREATE TABLE IF NOT EXISTS notification_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    channel VARCHAR(30) NOT NULL CHECK (channel IN ('in_app', 'email', 'sms', 'push')),
    category VARCHAR(50) NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (user_id, channel, category)
);

CREATE TABLE IF NOT EXISTS notification_deliveries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    notification_id UUID NOT NULL REFERENCES notifications(id) ON DELETE CASCADE,
    channel VARCHAR(30) NOT NULL,
    recipient_target VARCHAR(255) NOT NULL, -- email address or phone number
    status VARCHAR(30) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'delivered', 'failed', 'bounced')),
    external_id VARCHAR(100),
    error_message TEXT,
    sent_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Machine Learning & Agricultural Intelligence
CREATE TABLE IF NOT EXISTS intelligence_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(150) NOT NULL,
    model_type VARCHAR(50) NOT NULL, -- irrigation_scheduler, yield_predictor, pest_risk_detector, evapotranspiration_fao56, qvac_local_agronomist
    version VARCHAR(50) NOT NULL,
    framework VARCHAR(50) NOT NULL DEFAULT 'rule_based', -- rule_based, scikit_learn, qvac, pytorch, onnx
    description TEXT,
    parameters JSONB NOT NULL DEFAULT '{}'::jsonb,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_experimental BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (name, version)
);

CREATE TABLE IF NOT EXISTS intelligence_model_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_id UUID NOT NULL REFERENCES intelligence_models(id) ON DELETE CASCADE,
    organisation_id UUID NOT NULL REFERENCES organisations(id) ON DELETE CASCADE,
    farm_id UUID NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    field_id UUID REFERENCES fields(id) ON DELETE SET NULL,
    trigger_type VARCHAR(50) NOT NULL DEFAULT 'scheduled', -- scheduled, on_demand, event_driven
    input_features JSONB NOT NULL,
    output_predictions JSONB NOT NULL,
    execution_time_ms INTEGER,
    status VARCHAR(30) NOT NULL DEFAULT 'success' CHECK (status IN ('success', 'partial', 'failed')),
    error_message TEXT,
    ran_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS forecasts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organisation_id UUID NOT NULL REFERENCES organisations(id) ON DELETE CASCADE,
    farm_id UUID NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    field_id UUID REFERENCES fields(id) ON DELETE SET NULL,
    forecast_type VARCHAR(50) NOT NULL, -- weather, evapotranspiration, yield, soil_water_depletion
    forecast_source VARCHAR(100) NOT NULL DEFAULT 'open_meteo',
    valid_time TIMESTAMPTZ NOT NULL,
    horizon_hours INTEGER NOT NULL,
    metrics JSONB NOT NULL, -- e.g. {"temp_max": 28.5, "precipitation_prob": 70, "et0_mm": 4.2}
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_forecasts_farm_time ON forecasts(farm_id, valid_time);

CREATE TABLE IF NOT EXISTS recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organisation_id UUID NOT NULL REFERENCES organisations(id) ON DELETE CASCADE,
    farm_id UUID NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    field_id UUID REFERENCES fields(id) ON DELETE CASCADE,
    model_run_id UUID REFERENCES intelligence_model_runs(id) ON DELETE SET NULL,
    category VARCHAR(50) NOT NULL, -- irrigation, fertilizer, spraying, planting, harvesting, scouting
    title VARCHAR(200) NOT NULL,
    summary TEXT NOT NULL,
    rationale TEXT NOT NULL,
    confidence_score NUMERIC(3,2) CHECK (confidence_score BETWEEN 0.00 AND 1.00),
    urgency VARCHAR(20) NOT NULL DEFAULT 'medium' CHECK (urgency IN ('low', 'medium', 'high', 'immediate')),
    proposed_actions JSONB NOT NULL, -- e.g. [{"action": "irrigate", "zone_code": "Z-1", "duration_minutes": 45}]
    status VARCHAR(30) NOT NULL DEFAULT 'proposed' CHECK (status IN ('proposed', 'accepted', 'modified', 'rejected', 'executed', 'expired')),
    reviewed_by UUID REFERENCES users(id),
    reviewed_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_recommendations_field_status ON recommendations(field_id, status);

CREATE TABLE IF NOT EXISTS recommendation_evidence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recommendation_id UUID NOT NULL REFERENCES recommendations(id) ON DELETE CASCADE,
    evidence_type VARCHAR(50) NOT NULL, -- sensor_measurement, weather_forecast, crop_stage, soil_test, historical_yield
    metric_name VARCHAR(100) NOT NULL,
    observed_value VARCHAR(100) NOT NULL,
    threshold_value VARCHAR(100),
    source_reference TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS recommendation_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recommendation_id UUID NOT NULL REFERENCES recommendations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    feedback_rating INTEGER CHECK (feedback_rating BETWEEN 1 AND 5),
    feedback_notes TEXT,
    rejection_reason VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS recommendation_outcomes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recommendation_id UUID NOT NULL REFERENCES recommendations(id) ON DELETE CASCADE,
    outcome_metrics JSONB NOT NULL, -- e.g. {"water_saved_litres": 1200, "yield_effect_est": "+4%"}
    evaluator_user_id UUID REFERENCES users(id),
    notes TEXT,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
