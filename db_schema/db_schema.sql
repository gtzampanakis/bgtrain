-- MySQL dump 10.13  Distrib 5.5.41, for debian-linux-gnu (x86_64)
--
-- Host: giorgostzampanakis.mysql.pythonanywhere-services.com    Database: giorgostzampanak$bgtrain
-- ------------------------------------------------------
-- Server version	5.1.73-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `analyses`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
) ENGINE=InnoDB AUTO_INCREMENT=5010690 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `comments`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
) ENGINE=InnoDB AUTO_INCREMENT=447 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `posmatchids`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `posmatchids` (
  `posmatchid` char(27) NOT NULL,
  `decisiontype` char(1) DEFAULT NULL,
  `rating` float DEFAULT '1500',
  `version` int(11) DEFAULT NULL,
  `exported` bit(1) DEFAULT NULL,
  `matchid` char(32) DEFAULT NULL,
  `createddate` datetime DEFAULT NULL,
  `cluster` int(11) DEFAULT NULL,
  PRIMARY KEY (`posmatchid`),
  KEY `dectype_version` (`decisiontype`,`version`),
  KEY `posmatchids_new_gnuid_idx` (`decisiontype`,`version`,`rating`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `preferences`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `preferences` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `name` varchar(50) NOT NULL,
  `value` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `usern_name_uq_idx` (`username`,`name`),
  KEY `usern_fk_idx` (`username`),
  CONSTRAINT `usern_fk` FOREIGN KEY (`username`) REFERENCES `users` (`username`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=87 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `reports`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
) ENGINE=InnoDB AUTO_INCREMENT=77 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `stats`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `stats` (
  `id` int(11) NOT NULL DEFAULT '0',
  `numofpositions` int(11) DEFAULT NULL,
  `numofsubmissionslast24h` int(10) unsigned DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `users`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `username` varchar(50) NOT NULL,
  `rating` float DEFAULT '1500',
  `submissions` int(11) DEFAULT NULL,
  `pwhash` varchar(120) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`username`),
  KEY `usersrating_idx` (`rating`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `usersposmatchids`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `usersposmatchids` (
  `username` varchar(50) NOT NULL,
  `posmatchid` char(27) NOT NULL,
  `move` varchar(27) DEFAULT NULL,
  `submittedat` datetime DEFAULT NULL,
  `ratinguser` float DEFAULT NULL,
  `ratingpos` float DEFAULT NULL,
  UNIQUE KEY `upm_posmatchid_username` (`posmatchid`,`username`),
  KEY `username` (`username`),
  CONSTRAINT `usersposmatchids_ibfk_1` FOREIGN KEY (`username`) REFERENCES `users` (`username`),
  CONSTRAINT `usersposmatchids_ibfk_2` FOREIGN KEY (`posmatchid`) REFERENCES `posmatchids` (`posmatchid`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2015-03-11 21:16:35

alter table usersposmatchids add (eqdiff float);

create index usersposmatchids_idx1 on usersposmatchids(eqdiff);

