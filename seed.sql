-- Seed the mock user + credit profile used by the frontend
INSERT INTO users (id, email, name)
VALUES ('323ba38f-ae2c-4a01-9cf7-5642c87686be', 'demo@amortly.app', 'Demo User')
ON CONFLICT (id) DO NOTHING;

INSERT INTO credit_profile (user_id, on_time_payments, late_payments, missed_payments, total_paid, mock_credit_score)
VALUES ('323ba38f-ae2c-4a01-9cf7-5642c87686be', 0, 0, 0, 0, 650)
ON CONFLICT (user_id) DO NOTHING;
