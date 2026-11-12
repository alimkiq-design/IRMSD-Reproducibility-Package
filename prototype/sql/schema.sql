-- IRMSD Prototype Relational Schema (PostgreSQL)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS project (
    project_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_name VARCHAR(150) NOT NULL UNIQUE,
    domain_type  VARCHAR(50)  NOT NULL,
    alpha_cal    DECIMAL(3,2) NOT NULL DEFAULT 0.30 CHECK (alpha_cal > 0.00 AND alpha_cal <= 0.50),
    created_at   TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS "user" (
    user_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name      VARCHAR(100) NOT NULL,
    role           VARCHAR(30)  NOT NULL CHECK (role IN ('Developer', 'Tech_Lead', 'QA', 'PM')),
    experience_yrs INT          NOT NULL CHECK (experience_yrs >= 0)
);

CREATE TABLE IF NOT EXISTS requirement (
    req_id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id          UUID        NOT NULL REFERENCES project(project_id) ON DELETE CASCADE,
    user_story_text     TEXT        NOT NULL,
    acceptance_criteria TEXT        NOT NULL,
    priority_level      VARCHAR(20) NOT NULL DEFAULT 'Medium'
                        CHECK (priority_level IN ('Low', 'Medium', 'High', 'Critical'))
);

CREATE TABLE IF NOT EXISTS development_task (
    task_id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    req_id               UUID         NOT NULL REFERENCES requirement(req_id) ON DELETE CASCADE,
    assignee_id          UUID         REFERENCES "user"(user_id) ON DELETE SET NULL,
    e_init               DECIMAL(6,2) NOT NULL CHECK (e_init > 0),
    e_adj                DECIMAL(6,2) NOT NULL,
    governing_risk_level VARCHAR(10)  NOT NULL DEFAULT 'Low'
                         CHECK (governing_risk_level IN ('Low', 'Medium', 'High')),
    workflow_status      VARCHAR(20)  NOT NULL DEFAULT 'Backlog'
                         CHECK (workflow_status IN ('Backlog', 'Blocked_Spike', 'In_Progress', 'Review', 'Done')),
    CONSTRAINT chk_adjusted_effort CHECK (e_adj >= e_init)
);

CREATE TABLE IF NOT EXISTS nlp_prediction (
    pred_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id             UUID         NOT NULL REFERENCES development_task(task_id) ON DELETE CASCADE,
    req_id              UUID         NOT NULL REFERENCES requirement(req_id) ON DELETE CASCADE,
    model_version       VARCHAR(50)  NOT NULL DEFAULT 'bert-base-uncased-v1',
    candidate_category  VARCHAR(5)   NOT NULL
                        CHECK (candidate_category IN ('R1','R2','R3','R4','R5','R6','R7','R8','R9','R10','R11','R12')),
    confidence_score    DECIMAL(4,3) NOT NULL CHECK (confidence_score >= 0.000 AND confidence_score <= 1.000),
    extracted_text_span TEXT,
    human_decision      VARCHAR(15)  NOT NULL DEFAULT 'Pending'
                        CHECK (human_decision IN ('Pending', 'Accepted', 'Rejected', 'Modified')),
    reviewed_at         TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS risk_record (
    risk_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id       UUID        NOT NULL REFERENCES development_task(task_id) ON DELETE CASCADE,
    pred_id       UUID        UNIQUE REFERENCES nlp_prediction(pred_id) ON DELETE SET NULL,
    owner_id      UUID        NOT NULL REFERENCES "user"(user_id) ON DELETE RESTRICT,
    category_code VARCHAR(5)  NOT NULL
                  CHECK (category_code IN ('R1','R2','R3','R4','R5','R6','R7','R8','R9','R10','R11','R12')),
    p_init        INT         NOT NULL CHECK (p_init BETWEEN 1 AND 5),
    i_init        INT         NOT NULL CHECK (i_init BETWEEN 1 AND 5),
    r_init        INT         GENERATED ALWAYS AS (p_init * i_init) STORED,
    p_curr        INT         NOT NULL CHECK (p_curr BETWEEN 1 AND 5),
    i_curr        INT         NOT NULL CHECK (i_curr BETWEEN 1 AND 5),
    r_curr        INT         GENERATED ALWAYS AS (p_curr * i_curr) STORED,
    severity_tier VARCHAR(10) GENERATED ALWAYS AS (
        CASE
            WHEN (p_curr * i_curr) <= 6  THEN 'Low'
            WHEN (p_curr * i_curr) <= 14 THEN 'Medium'
            ELSE 'High'
        END
    ) STORED,
    risk_status   VARCHAR(15) NOT NULL DEFAULT 'Open'
                  CHECK (risk_status IN ('Open', 'Mitigating', 'Verified', 'Closed')),
    identified_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- At most one active risk per task/category; closed and verified records remain historical.
CREATE UNIQUE INDEX IF NOT EXISTS uq_active_risk_task_category
    ON risk_record (task_id, category_code)
    WHERE risk_status IN ('Open', 'Mitigating');

CREATE TABLE IF NOT EXISTS mitigation_action (
    mitigation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    risk_id       UUID         NOT NULL REFERENCES risk_record(risk_id) ON DELETE CASCADE,
    owner_id      UUID         NOT NULL REFERENCES "user"(user_id) ON DELETE RESTRICT,
    action_type   VARCHAR(25)  NOT NULL
                  CHECK (action_type IN ('Spike', 'Peer_Review', 'Security_Scan', 'Buffer')),
    buffer_hours  DECIMAL(5,2) NOT NULL DEFAULT 0.00 CHECK (buffer_hours >= 0.00),
    due_date      DATE         NOT NULL,
    action_status VARCHAR(15)  NOT NULL DEFAULT 'Planned'
                  CHECK (action_status IN ('Planned', 'In_Progress', 'Completed')),
    started_at    TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS verification (
    verif_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mitigation_id UUID         NOT NULL REFERENCES mitigation_action(mitigation_id) ON DELETE CASCADE,
    evidence_type VARCHAR(30)  NOT NULL
                  CHECK (evidence_type IN ('Spike_Doc', 'Review_Log', 'Test_Report')),
    artifact_link VARCHAR(255) NOT NULL,
    verified_at   TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
