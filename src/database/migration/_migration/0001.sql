CREATE TABLE "wolt_token"
(
    "id"            integer PRIMARY KEY,
    "account_id"    integer REFERENCES wolt_account (id) NOT NULL,
    "refresh_token" varchar                              NOT NULL,
    "access_token"  varchar                              NOT NULL,
    "expires_in"    integer                              NOT NULL,
    "created"       timestamp DEFAULT CURRENT_TIMESTAMP  NOT NULL
);

CREATE TABLE "wolt_account"
(
    "id"           integer PRIMARY KEY,
    "account_name" varchar unique                      NOT NULL,
    "created"      timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE "youtube_video"
(
    "video_id"        nvarchar PRIMARY KEY,
    "channel_id"      nvarchar                            NOT NULL,
    "description"     nvarchar                            NULL,
    "title"           nvarchar                            NOT NULL,
    "publish_time"    datetime                            NOT NULL,
    "video_length"    float                               NULL,
    "url"             nvarchar                            NOT NULL,
    "skipped_finding" boolean                             NOT NULL,
    "created"         timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE "code"
(
    "id"                           integer PRIMARY KEY,
    "video_id"                     nvarchar REFERENCES youtube_video (video_id) NOT NULL,
    "code"                         NVARCHAR                                    NOT NULL,
    "how_long_to_process_in_total" float                                       NOT NULL,
    "code_state_id"                REFERENCES code_state (id)                  NOT NULL,
    "timestamp"                    float                                       NULL,
    "path_to_frame"                NVARCHAR                                    NULL,
    "created"                      timestamp DEFAULT CURRENT_TIMESTAMP         NOT NULL

);

CREATE TABLE "code_state"
(
    "id"   integer PRIMARY KEY,
    "name" nvarchar NOT NULL
);

CREATE TABLE "database_version"
(
    "VERSION" nvarchar NOT NULL
);

INSERT INTO "code_state"
    (id, name)
VALUES (1, 'SUCCESSFULLY_REDEEM'),
       (2, 'ALREADY_TAKEN'),
       (3, 'BAD_CODE'),
       (4, 'EXPIRED'),
       (5, 'TOO_MANY_REQUESTS'),
       (6, 'UNKNOWN_ERROR');


INSERT INTO "database_version"(VERSION)
VALUES ('0001');