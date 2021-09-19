-- phpMyAdmin SQL Dump
-- version 5.1.0
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 19-09-2021 a las 23:03:40
-- Versión del servidor: 10.4.19-MariaDB
-- Versión de PHP: 8.0.6

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `multioff`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `beatmap`
--

CREATE TABLE `beatmap` (
  `id` bigint(36) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  `server_id` bigint(36) NOT NULL,
  `count` int(11) NOT NULL DEFAULT 0 COMMENT 'Nmro de veces jugado',
  `ban` int(11) NOT NULL DEFAULT 0,
  `active` tinyint(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `play`
--

CREATE TABLE `play` (
  `id` bigint(20) NOT NULL,
  `server_id` bigint(20) NOT NULL,
  `beatmap_id` bigint(20) NOT NULL,
  `active` tinyint(1) NOT NULL DEFAULT 1,
  `start` datetime NOT NULL DEFAULT current_timestamp(),
  `end` datetime NOT NULL DEFAULT current_timestamp(),
  `first` bigint(20) DEFAULT NULL,
  `second` bigint(20) DEFAULT NULL,
  `third` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `server`
--

CREATE TABLE `server` (
  `id` bigint(36) NOT NULL,
  `name` varchar(50) NOT NULL,
  `max_players` int(6) NOT NULL DEFAULT 1000,
  `premium` tinyint(1) NOT NULL DEFAULT 0,
  `channel_id` bigint(36) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `user`
--

CREATE TABLE `user` (
  `server_id` bigint(36) NOT NULL,
  `id` bigint(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `admin` tinyint(1) NOT NULL DEFAULT 0,
  `osu_id` bigint(36) NOT NULL,
  `osu_name` varchar(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `beatmap`
--
ALTER TABLE `beatmap`
  ADD PRIMARY KEY (`id`,`server_id`);

--
-- Indices de la tabla `play`
--
ALTER TABLE `play`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `server`
--
ALTER TABLE `server`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`server_id`,`id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `play`
--
ALTER TABLE `play`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
