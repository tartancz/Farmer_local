UPDATE database_version
SET VERSION='0002';

INSERT INTO "code_state"
    (id, name)
VALUES (7, 'SKIPPED');

alter table "code"
    add column "activated_by" varchar REFERENCES wolt_account (account_name) NULL;

alter table "code"
    add column "value" INT NULL;

alter table "wolt_account"
    add column "max_credits_per_month" INT NOT NULL DEFAULT 0;

alter table "wolt_account"
    add column "priority" INT NULL;

alter table "wolt_account"
    add column "working_credentials" boolean NULL;
