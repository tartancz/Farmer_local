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



CREATE TABLE "database_version"
(
    "VERSION" nvarchar NOT NULL
);
INSERT INTO "database_version"(VERSION) VALUES ('0001')