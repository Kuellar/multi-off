SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


CREATE TABLE `server` (
  `id` bigint(36) NOT NULL PRIMARY KEY,
  `name` varchar(50) NOT NULL,
  `max_players` int(6) NOT NULL DEFAULT 1000,
  `premium` tinyint(1) NOT NULL DEFAULT 0,
  `channel_id` bigint(36) DEFAULT NULL,
  `message_id` bigint(36) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE `user` (
  `id` bigint(20) NOT NULL,
  `server_id` bigint(36) NOT NULL,
  `name` varchar(50) NOT NULL,
  `admin` tinyint(1) NOT NULL DEFAULT 0,
  `osu_id` bigint(36) NOT NULL,
  `osu_name` varchar(11) NOT NULL,
  `cache_play_id` bigint(36) DEFAULT NULL,
  `cache_score` bigint(36) DEFAULT NULL,
  `cache_combo` int(10) DEFAULT NULL,
  `cache_acc` double DEFAULT NULL,
  `cache_rank` varchar(4) DEFAULT NULL,
  `cache_time` datetime DEFAULT NULL,
  PRIMARY KEY(id, server_id, osu_id),
  FOREIGN KEY(server_id) REFERENCES server(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE `beatmap` (
  `id` bigint(36) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  `server_id` bigint(36) NOT NULL,
  `count` int(11) NOT NULL DEFAULT 0 COMMENT 'Nmro de veces jugado',
  `ban` int(11) NOT NULL DEFAULT 0,
  `active` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY(id, user_id, server_id),
  FOREIGN KEY(user_id) REFERENCES user(id),
  FOREIGN KEY(server_id) REFERENCES server(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE `play` (
  `id` bigint(20) NOT NULL,
  `server_id` bigint(20) NOT NULL,
  `beatmap_id` bigint(20) NOT NULL,
  `active` tinyint(1) NOT NULL DEFAULT 1,
  `start` datetime NOT NULL DEFAULT current_timestamp(),
  `end` datetime NOT NULL DEFAULT current_timestamp(),
  `first` bigint(20) DEFAULT NULL,
  `second` bigint(20) DEFAULT NULL,
  `third` bigint(20) DEFAULT NULL,
  PRIMARY KEY(id, server_id, beatmap_id),
  FOREIGN KEY(server_id) REFERENCES server(id),
  FOREIGN KEY(beatmap_id) REFERENCES beatmap(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


SET FOREIGN_KEY_CHECKS = 1;
