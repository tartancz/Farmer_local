UPDATE database_version
SET VERSION='0002';

INSERT INTO "code_state"
    (id, name)
VALUES (7, 'SKIPPED');

alter table "code"
    add column "activated_by" varchar REFERENCES wolt_account (account_name) NULL;

alter table "code"
    add column "value" INT NULL;


