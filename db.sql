DROP TABLE progress;
DROP TABLE result;
DROP TABLE term;
DROP TABLE test;
DROP TABLE translate;
DROP TABLE user;

CREATE TABLE progress (
    "id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE,
    "translate_id" INTEGER NOT NULL,
    "all" INTEGER DEFAULT (0),
    "error" INTEGER DEFAULT (0)
);
CREATE TABLE result (
    "id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE,
    "test_id" INTEGER NOT NULL,
    "number" INTEGER NOT NULL,
    "question" VARCHAR,
    "answer" VARCHAR,
    "enter" VARCHAR,
    "error" BOOL,
    "created" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE term (
    "token" VARCHAR(40) NOT NULL UNIQUE,
    "en" VARCHAR NOT NULL
);
CREATE TABLE test (
    "id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE,
    "user_id" INTEGER NOT NULL,
    "name" VARCHAR(64) NOT NULL,
    "created" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "finished" TIMESTAMP
);
CREATE TABLE translate (
    "id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE,
    "term" VARCHAR(40) NOT NULL,
    "user_id" INTEGER NOT NULL,
    "rus" VARCHAR NOT NULL,
    "created" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE user (
    "id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE,
    "name" VARCHAR NOT NULL,
    "password" VARCHAR NOT NULL,
    "full" TEXT
);
CREATE INDEX "progress_result" ON "progress" ("all" ASC, "error" ASC);
CREATE INDEX "progress_translate" ON "progress" ("translate_id" ASC);
CREATE INDEX "result_test" ON "result" ("test_id" ASC, "number" DESC, "error" ASC, "created" DESC);
CREATE INDEX "term_token" ON "term" ("en" ASC);
CREATE INDEX "test_user" ON "test" ("user_id" ASC, "created" DESC, "finished" DESC);
CREATE INDEX "translate_created" ON "translate" ("created" DESC);
CREATE INDEX "translate_rus" ON "translate" ("term" ASC, "user_id" ASC, "rus" ASC);
CREATE INDEX "translate_term" ON "translate" ("term" ASC, "user_id" ASC);
CREATE UNIQUE INDEX "user_name" ON "user" ("name" ASC);
CREATE INDEX "user_passwod" ON "user" ("password" ASC);
