CREATE TABLE "progress" ("id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE , "translate_id" INTEGER NOT NULL , "all" INTEGER DEFAULT 0, "error" INTEGER DEFAULT 0);
CREATE TABLE "term" ("token" VARCHAR(40) PRIMARY KEY  NOT NULL  UNIQUE , "en" VARCHAR NOT NULL );
CREATE TABLE "translate" ("id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE , "term" VARCHAR(40) NOT NULL , "user_id" INTEGER NOT NULL , "rus" VARCHAR NOT NULL );
CREATE TABLE "user" ("id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL , "name" VARCHAR NOT NULL  UNIQUE , "password" VARCHAR NOT NULL , "full" TEXT);
CREATE INDEX "progress_result" ON "progress" ("all" ASC, "error" ASC);
CREATE INDEX "progress_translate" ON "progress" ("translate_id" ASC);
CREATE INDEX "translate_user_id" ON "translate" ("user_id" ASC);
CREATE UNIQUE INDEX "user_name" ON "user" ("name" ASC);
CREATE INDEX "user_passwod" ON "user" ("password" ASC);
