-- phpMyAdmin SQL Dump
-- version 4.9.7
-- https://www.phpmyadmin.net/
--
-- Servidor: localhost
-- Tiempo de generación: 19-04-2023 a las 20:33:48
-- Versión del servidor: 10.3.32-MariaDB
-- Versión de PHP: 7.4.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `server_snitch`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `ActionLog`
--

CREATE TABLE `ActionLog` (
  `UserId` int(11) NOT NULL,
  `DeviceId` varchar(32) NOT NULL,
  `TimeStamp` timestamp NOT NULL DEFAULT current_timestamp(),
  `Action` enum('start','reboot') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `DataValue`
--

CREATE TABLE `DataValue` (
  `Id` bigint(20) NOT NULL,
  `Name` varchar(100) NOT NULL,
  `Value` varchar(50) DEFAULT NULL,
  `Type` enum('bool','int','float','string') NOT NULL DEFAULT 'string',
  `TimeStamp` timestamp NOT NULL DEFAULT current_timestamp(),
  `DeviceId` varchar(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `Device`
--

CREATE TABLE `Device` (
  `EUI` varchar(32) NOT NULL,
  `MAC` varchar(32) NOT NULL,
  `Alias` varchar(50) NOT NULL,
  `Description` text NULL,
  `GroupId` int(11) NOT NULL,
  `UserId` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `DeviceGroup`
--

CREATE TABLE `DeviceGroup` (
  `Id` int(11) NOT NULL,
  `Alias` varchar(50) NOT NULL,
  `Description` text NULL,
  `Location` varchar(30) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `User`
--

CREATE TABLE `User` (
  `Id` int(11) NOT NULL,
  `User` varchar(50) NOT NULL,
  `PwdHash` varchar(255) NOT NULL,
  `Name` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `UserDeviceGroup`
--

CREATE TABLE `UserDeviceGroup` (
  `DeviceGropuId` int(11) NOT NULL,
  `UserId` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `ActionLog`
--
ALTER TABLE `ActionLog`
  ADD KEY `UserAction` (`UserId`),
  ADD KEY `DeviceAction` (`DeviceId`);

--
-- Indices de la tabla `DataValue`
--
ALTER TABLE `DataValue`
  ADD PRIMARY KEY (`Id`),
  ADD KEY `DeviceDataValue` (`DeviceId`);

--
-- Indices de la tabla `Device`
--
ALTER TABLE `Device`
  ADD PRIMARY KEY (`EUI`),
  ADD UNIQUE KEY `Alias` (`Alias`),
  ADD UNIQUE KEY `MAC` (`MAC`),
  ADD KEY `DeviceGroup` (`GroupId`),
  ADD KEY `DeviceCreator` (`UserId`);

--
-- Indices de la tabla `DeviceGroup`
--
ALTER TABLE `DeviceGroup`
  ADD PRIMARY KEY (`Id`),
  ADD UNIQUE KEY `Alias` (`Alias`);

--
-- Indices de la tabla `User`
--
ALTER TABLE `User`
  ADD PRIMARY KEY (`Id`),
  ADD UNIQUE KEY `User` (`User`);

--
-- Indices de la tabla `UserDeviceGroup`
--
ALTER TABLE `UserDeviceGroup`
  ADD PRIMARY KEY (`DeviceGropuId`,`UserId`),
  ADD KEY `UserGroup` (`UserId`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `User`
--
ALTER TABLE `User`
  MODIFY `Id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `DataValue`
--
ALTER TABLE `DataValue`
  MODIFY `Id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `DeviceGroup`
--
ALTER TABLE `DeviceGroup`
  MODIFY `Id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `ActionLog`
--
ALTER TABLE `ActionLog`
  ADD CONSTRAINT `DeviceAction` FOREIGN KEY (`DeviceId`) REFERENCES `Device` (`EUI`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `UserAction` FOREIGN KEY (`UserId`) REFERENCES `User` (`Id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `DataValue`
--
ALTER TABLE `DataValue`
  ADD CONSTRAINT `DeviceDataValue` FOREIGN KEY (`DeviceId`) REFERENCES `Device` (`EUI`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `Device`
--
ALTER TABLE `Device`
  ADD CONSTRAINT `DeviceCreator` FOREIGN KEY (`UserId`) REFERENCES `User` (`Id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `DeviceGroup` FOREIGN KEY (`GroupId`) REFERENCES `DeviceGroup` (`Id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `UserDeviceGroup`
--
ALTER TABLE `UserDeviceGroup`
  ADD CONSTRAINT `DeviceGroupUser` FOREIGN KEY (`DeviceGropuId`) REFERENCES `DeviceGroup` (`Id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `UserGroup` FOREIGN KEY (`UserId`) REFERENCES `User` (`Id`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
