# TABLE: analyses
CREATE TABLE `analyses` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `posmatchid` char(27) NOT NULL,
  `move` varchar(27) NOT NULL,
  `equity` float NOT NULL,
  `ply` tinyint(4) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `posmatchid` (`posmatchid`,`move`),
  KEY `anposmatchid_idx` (`posmatchid`),
  CONSTRAINT `anposmatchid` FOREIGN KEY (`posmatchid`) REFERENCES `posmatchids` (`posmatchid`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4394120 DEFAULT CHARSET=utf8;
# TABLE: comments
CREATE TABLE `comments` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `posmatchid` char(27) DEFAULT NULL,
  `postedat` datetime NOT NULL,
  `parentid` int(10) unsigned DEFAULT NULL,
  `comment` mediumtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `username_fk_idx` (`username`),
  KEY `parentid_idx` (`parentid`),
  KEY `posmatchid_fk_idx` (`posmatchid`),
  CONSTRAINT `parentid_fk` FOREIGN KEY (`parentid`) REFERENCES `comments` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `posmatchid_fk` FOREIGN KEY (`posmatchid`) REFERENCES `posmatchids` (`posmatchid`) ON DELETE SET NULL ON UPDATE NO ACTION,
  CONSTRAINT `username_fk` FOREIGN KEY (`username`) REFERENCES `users` (`username`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=64 DEFAULT CHARSET=utf8 COMMENT='	';
# TABLE: posmatchids
CREATE TABLE `posmatchids` (
  `posmatchid` char(27) NOT NULL,
  `decisiontype` char(1) DEFAULT NULL,
  `rating` float DEFAULT '1500',
  `version` int(11) DEFAULT NULL,
  `exported` bit(1) DEFAULT NULL,
  `matchid` char(32) DEFAULT NULL,
  `createddate` datetime DEFAULT NULL,
  `positionbin` binary(50) DEFAULT NULL,
  `cluster` int(11) DEFAULT NULL,
  PRIMARY KEY (`posmatchid`),
  KEY `dectype_version` (`decisiontype`,`version`),
  KEY `posmatchids_new_gnuid_idx` (`decisiontype`,`version`,`rating`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
# TABLE: preferences
CREATE TABLE `preferences` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `name` varchar(50) NOT NULL,
  `value` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `usern_name_uq_idx` (`username`,`name`),
  KEY `usern_fk_idx` (`username`),
  CONSTRAINT `usern_fk` FOREIGN KEY (`username`) REFERENCES `users` (`username`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
# TABLE: reports
CREATE TABLE `reports` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `posmatchid` char(27) DEFAULT NULL,
  `postedat` datetime NOT NULL,
  `comment` mediumtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `rep_username_fk_idx` (`username`),
  KEY `rep_posmatchid_fk_idx` (`posmatchid`),
  CONSTRAINT `rep_posmatchid_fk` FOREIGN KEY (`posmatchid`) REFERENCES `posmatchids` (`posmatchid`) ON DELETE SET NULL ON UPDATE NO ACTION,
  CONSTRAINT `rep_username_fk` FOREIGN KEY (`username`) REFERENCES `users` (`username`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8 COMMENT='	';
# TABLE: stats
CREATE TABLE `stats` (
  `id` int(11) NOT NULL DEFAULT '0',
  `numofpositions` int(11) DEFAULT NULL,
  `numofsubmissionslast24h` int(10) unsigned DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
# TABLE: users
CREATE TABLE `users` (
  `username` varchar(50) NOT NULL,
  `rating` float DEFAULT '1500',
  `submissions` int(11) DEFAULT NULL,
  `pwhash` varchar(120) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `openverifsince` datetime DEFAULT NULL,
  PRIMARY KEY (`username`),
  KEY `usersrating_idx` (`rating`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
# TABLE: usersposmatchids
CREATE TABLE `usersposmatchids` (
  `username` varchar(50) NOT NULL,
  `posmatchid` char(27) NOT NULL,
  `move` varchar(27) DEFAULT NULL,
  `submittedat` datetime DEFAULT NULL,
  `ratinguser` float DEFAULT NULL,
  `ratingpos` float DEFAULT NULL,
  UNIQUE KEY `upm_posmatchid_username` (`posmatchid`,`username`),
  KEY `username` (`username`),
  KEY `usersposmatchids_ibfk_2` (`posmatchid`),
  CONSTRAINT `usersposmatchids_ibfk_1` FOREIGN KEY (`username`) REFERENCES `users` (`username`),
  CONSTRAINT `usersposmatchids_ibfk_2` FOREIGN KEY (`posmatchid`) REFERENCES `posmatchids` (`posmatchid`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
#...done.
SET FOREIGN_KEY_CHECKS=1;
