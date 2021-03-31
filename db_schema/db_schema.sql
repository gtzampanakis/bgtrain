CREATE TABLE "analyses" (
  "id" integer primary key,
  "posmatchid" char(27) NOT NULL,
  "move" varchar(27) NOT NULL,
  "equity" float NOT NULL,
  "ply" tinyint(4) DEFAULT NULL,
  UNIQUE ("posmatchid","move"),
  CONSTRAINT "anposmatchid" FOREIGN KEY ("posmatchid") REFERENCES "posmatchids" ("posmatchid") ON DELETE CASCADE
);
create index "anposmatchid_idx" on "analyses"("posmatchid");

CREATE TABLE "comments" (
  "id" integer primary key,
  "username" varchar(50) NOT NULL,
  "posmatchid" char(27) DEFAULT NULL,
  "postedat" datetime NOT NULL,
  "parentid" int(10) DEFAULT NULL,
  "comment" mediumtext NOT NULL,
  CONSTRAINT "parentid_fk" FOREIGN KEY ("parentid") REFERENCES "comments" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT "posmatchid_fk" FOREIGN KEY ("posmatchid") REFERENCES "posmatchids" ("posmatchid") ON DELETE SET NULL ON UPDATE NO ACTION,
  CONSTRAINT "username_fk" FOREIGN KEY ("username") REFERENCES "users" ("username") ON DELETE NO ACTION ON UPDATE NO ACTION
);
create index "posmatchid_fk_idx" on "comments"("posmatchid");
create index "parentid_idx" on "comments"("parentid");
create index "username_fk_idx" on "comments"("username");

CREATE TABLE "posmatchids" (
  "id" integer primary key,
  "posmatchid" char(27) NOT NULL,
  "decisiontype" char(1) DEFAULT NULL,
  "rating" float DEFAULT '1500',
  "version" int(11) DEFAULT NULL,
  "exported" bit(1) DEFAULT NULL,
  "matchid" char(32) DEFAULT NULL,
  "createddate" datetime DEFAULT NULL,
  "cluster" int(11) DEFAULT NULL,
  "submissions" int(11) DEFAULT NULL,
  UNIQUE ("posmatchid")
);
create index "posmatchids_new_gnuid_idx" on "posmatchids"("decisiontype","version","rating");

CREATE TABLE "postags" (
  "id" integer primary key,
  "POSMATCHID" char(27) NOT NULL,
  "TAG" varchar(30) NOT NULL,
  "CREATEDAT" datetime NOT NULL,
  UNIQUE ("POSMATCHID","TAG"),
  CONSTRAINT "tagsfk" FOREIGN KEY ("TAG") REFERENCES "tags" ("TAG") ON DELETE CASCADE ON UPDATE CASCADE
);
create index "tagsfk_idx" on "postags"("TAG");

CREATE TABLE "preferences" (
  "id" integer primary key,
  "username" varchar(50) NOT NULL,
  "name" varchar(50) NOT NULL,
  "value" varchar(100) DEFAULT NULL,
  UNIQUE ("username","name"),
  CONSTRAINT "usern_fk" FOREIGN KEY ("username") REFERENCES "users" ("username") ON DELETE NO ACTION ON UPDATE NO ACTION
);

CREATE TABLE "reports" (
  "id" integer primary key,
  "username" varchar(50) NOT NULL,
  "posmatchid" char(27) DEFAULT NULL,
  "postedat" datetime NOT NULL,
  "comment" mediumtext NOT NULL,
  CONSTRAINT "rep_posmatchid_fk" FOREIGN KEY ("posmatchid") REFERENCES "posmatchids" ("posmatchid") ON DELETE SET NULL ON UPDATE NO ACTION,
  CONSTRAINT "rep_username_fk" FOREIGN KEY ("username") REFERENCES "users" ("username") ON DELETE NO ACTION ON UPDATE NO ACTION
);
create index "rep_posmatchid_fk_idx" on "reports"("posmatchid");
create index "rep_username_fk_idx" on "reports"("username");

CREATE TABLE "stats" (
  "id" integer primary key,
  "numofpositions" int(11) DEFAULT NULL,
  "numofsubmissionslast24h" int(10) DEFAULT NULL
);

CREATE TABLE "tags" (
  "id" integer primary key,
  "TAG" varchar(30) NOT NULL,
  "DONETAGGING" char(1) DEFAULT NULL,
  "CREATEDAT" datetime NOT NULL,
  UNIQUE ("TAG")
);

CREATE TABLE "users" (
  "id" integer primary key,
  "username" varchar(50) NOT NULL,
  "rating" float DEFAULT '1500',
  "submissions" int(11) DEFAULT NULL,
  "pwhash" varchar(120) DEFAULT NULL,
  "email" varchar(100) DEFAULT NULL,
  "lastsubmission" datetime DEFAULT NULL,
  UNIQUE ("username")
);
create index "usersrating_idx" on "users"("rating");

CREATE TABLE "usersposmatchids" (
  "id" integer primary key,
  "username" varchar(50) NOT NULL,
  "posmatchid" char(27) NOT NULL,
  "move" varchar(27) DEFAULT NULL,
  "submittedat" datetime DEFAULT NULL,
  "ratinguser" float DEFAULT NULL,
  "ratingpos" float DEFAULT NULL,
  "eqdiff" float DEFAULT NULL,
  "increment" float DEFAULT NULL,
  "plasubms" int(11) DEFAULT NULL,
  "possubms" int(11) DEFAULT NULL,
  UNIQUE ("posmatchid","username"),
  CONSTRAINT "usersposmatchids_ibfk_1" FOREIGN KEY ("username") REFERENCES "users" ("username"),
  CONSTRAINT "usersposmatchids_ibfk_2" FOREIGN KEY ("posmatchid") REFERENCES "posmatchids" ("posmatchid") ON DELETE CASCADE
);
create index "usersposmatchids_idx1" on "usersposmatchids"("eqdiff");
create index "username" on "usersposmatchids"("username");
