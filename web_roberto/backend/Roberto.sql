-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: May 12, 2026 at 12:35 AM
-- Server version: 10.4.28-MariaDB
-- PHP Version: 8.2.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

-- Desactivamos la comprobación de claves foráneas temporalmente para evitar errores al borrar
SET FOREIGN_KEY_CHECKS = 0;

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `Roberto`
--

-- --------------------------------------------------------

--
-- Table structure for table `Aeropuerto`
--

DROP TABLE IF EXISTS `Aeropuerto`;
CREATE TABLE `Aeropuerto` (
  `CodigoIATA` varchar(10) NOT NULL,
  `Nombre` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

--
-- Dumping data for table `Aeropuerto`
--

INSERT INTO `Aeropuerto` (`CodigoIATA`, `Nombre`) VALUES
('JFK', 'John F. Kennedy'),
('MAD', 'Adolfo Suárez Madrid-Barajas');

-- --------------------------------------------------------

--
-- Table structure for table `Evento`
--

DROP TABLE IF EXISTS `Evento`;
CREATE TABLE `Evento` (
  `EventoID` int(11) NOT NULL,
  `RobotID` int(11) NOT NULL,
  `PosicionID` int(11) DEFAULT NULL,
  `FechaHora` datetime NOT NULL,
  `TipoEvento` varchar(50) NOT NULL,
  `Severidad` varchar(20) NOT NULL,
  `Mensaje` text DEFAULT NULL,
  `Estado` varchar(20) DEFAULT NULL,
  `CerradaEn` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

--
-- Dumping data for table `Evento`
--

INSERT INTO `Evento` (`EventoID`, `RobotID`, `PosicionID`, `FechaHora`, `TipoEvento`, `Severidad`, `Mensaje`, `Estado`, `CerradaEn`) VALUES
(1, 1, 1, '2026-04-12 21:06:20', 'Inicio Sistema', 'Info', 'Sistema de navegación iniciado correctamente', 'Abierto', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `Interaccion`
--

DROP TABLE IF EXISTS `Interaccion`;
CREATE TABLE `Interaccion` (
  `InteraccionID` int(11) NOT NULL,
  `RobotID` int(11) NOT NULL,
  `ZonaActualID` int(11) NOT NULL,
  `ZonaDestinoID` int(11) NOT NULL,
  `FechaHora` datetime NOT NULL,
  `Duracion` int(11) NOT NULL,
  `Valoracion` int(11) DEFAULT NULL,
  `Comentario` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

--
-- Dumping data for table `Interaccion`
--

INSERT INTO `Interaccion` (`InteraccionID`, `RobotID`, `ZonaActualID`, `ZonaDestinoID`, `FechaHora`, `Duracion`, `Valoracion`, `Comentario`) VALUES
(7, 1, 3, 6, '2026-05-03 21:16:12', 195, 5, 'genial'),
(8, 1, 3, 6, '2026-05-03 21:16:31', 195, 1, 'boo'),
(9, 1, 3, 7, '2026-05-01 10:20:00', 120, 5, 'Llegada rápida al Restaurante VIP'),
(10, 2, 8, 3, '2026-05-01 11:45:30', 310, 4, 'Desde Burger King a Puerta 12 ok'),
(11, 1, 9, 6, '2026-05-02 09:15:00', 45, 2, 'Se detuvo cerca de Starbucks'),
(12, 2, 11, 15, '2026-05-02 14:30:12', 200, 5, 'Guía perfecta al Duty Free'),
(13, 1, 16, 17, '2026-05-03 08:00:00', 150, 3, 'Recogida de equipajes a Taxis'),
(14, 2, 10, 12, '2026-05-04 12:00:00', 180, 5, 'Tapas Bar a Electrónica sin fallos'),
(15, 1, 14, 3, '2026-05-05 16:20:45', 240, 1, 'Problemas saliendo de Farmacia'),
(16, 2, 13, 4, '2026-05-06 18:10:00', 130, 4, 'Librería a Puerta 4'),
(17, 1, 18, 11, '2026-05-07 20:05:30', 95, 5, 'Alquiler de coches a Duty Free'),
(18, 2, 5, 8, '2026-05-08 10:40:00', 210, 3, 'Puerta 8 a Burger King'),
(19, 1, 12, 15, '2026-05-09 13:15:00', 175, 4, 'Buen trabajo en zona de Ocio'),
(20, 2, 17, 18, '2026-05-10 15:50:22', 140, 5, 'Parada Taxis a Alquiler Coches'),
(21, 1, 4, 10, '2026-05-11 11:30:00', 300, 2, 'Perdido buscando el Tapas Bar'),
(22, 2, 15, 16, '2026-05-12 09:00:00', 160, 4, 'Salida Principal a Equipajes'),
(23, 1, 7, 9, '2026-05-12 14:10:00', 115, 5, 'Ruta de comida completada');

-- --------------------------------------------------------

--
-- Table structure for table `Mantenimiento`
--

DROP TABLE IF EXISTS `Mantenimiento`;
CREATE TABLE `Mantenimiento` (
  `MantenimientoID` int(11) NOT NULL,
  `RobotID` int(11) NOT NULL,
  `TecnicoID` int(11) DEFAULT NULL,
  `Tipo` varchar(50) NOT NULL,
  `FechaProgramada` date NOT NULL,
  `FechaEjecutada` datetime DEFAULT NULL,
  `Estado` varchar(20) DEFAULT NULL,
  `Notas` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `PosicionRobot`
--

DROP TABLE IF EXISTS `PosicionRobot`;
CREATE TABLE `PosicionRobot` (
  `PosicionID` int(11) NOT NULL,
  `RobotID` int(11) NOT NULL,
  `PosX` float NOT NULL,
  `PosY` float NOT NULL,
  `FechaHora` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

--
-- Dumping data for table `PosicionRobot`
--

INSERT INTO `PosicionRobot` (`PosicionID`, `RobotID`, `PosX`, `PosY`, `FechaHora`) VALUES
(1, 1, 125, 455, '2026-04-12 16:13:33'),
(2, 1, 10, 20, '2026-04-12 21:06:20'),
(3, 1, 0, 0, '2026-04-17 13:48:37'),
(4, 1, 0.114717, -0.000121889, '2026-04-17 13:53:15'),
(5, 1, 0.23045, -0.000176555, '2026-04-17 13:53:43'),
(6, 1, 0.349174, -0.000824697, '2026-04-17 13:53:46'),
(7, 1, 0.453049, -0.00130066, '2026-04-17 13:53:48'),
(8, 1, 0.588124, -0.000472007, '2026-04-17 13:53:50'),
(9, 1, 0.693563, 0.000536521, '2026-04-17 13:53:52'),
(10, 1, 0, 0, '2026-04-17 14:14:14'),
(11, 1, 0, 0, '2026-04-17 14:43:05'),
(12, 1, 0, 0, '2026-04-17 14:53:40'),
(13, 1, 0, 0, '2026-04-17 15:03:18'),
(14, 1, 0, 0, '2026-04-17 16:48:44'),
(15, 1, 0.00312907, -0.0294583, '2026-04-17 17:02:25'),
(16, 1, 0.00312907, -0.0294583, '2026-04-17 17:04:33'),
(17, 1, 0.0164993, -0.0161786, '2026-04-17 17:26:39'),
(18, 1, -0.0106496, -0.0193185, '2026-04-17 17:27:41'),
(19, 1, 0, 0, '2026-04-17 17:28:08'),
(20, 1, 0, 0, '2026-04-17 18:42:16'),
(21, 1, 0, 0, '2026-04-17 18:54:34'),
(22, 1, 0, 0, '2026-04-17 19:14:32'),
(23, 1, 0, 0, '2026-04-17 19:28:04'),
(24, 1, 0, 0, '2026-04-17 19:40:37'),
(25, 1, 0, 0, '2026-04-17 20:02:05'),
(26, 1, 0, 0, '2026-04-17 20:04:04'),
(27, 1, 0, 0, '2026-04-17 20:14:53'),
(28, 1, 0, 0, '2026-04-17 20:29:41'),
(29, 1, 0, 0, '2026-04-17 21:23:26'),
(30, 1, 0.0472678, 0.0212028, '2026-04-17 23:15:54'),
(31, 1, 0.283367, 0.253334, '2026-04-17 23:15:55'),
(32, 1, 0.430166, 0.423054, '2026-04-17 23:15:56'),
(33, 1, 0.567496, 0.578353, '2026-04-17 23:15:57'),
(34, 1, 0.718357, 0.7221, '2026-04-17 23:15:58'),
(35, 1, 0.840953, 0.84095, '2026-04-17 23:15:59'),
(36, 1, 0.956363, 0.944688, '2026-04-17 23:16:01'),
(37, 1, 0.946542, 0.833692, '2026-04-17 23:16:27'),
(38, 1, 0.891061, 0.626031, '2026-04-17 23:16:28'),
(39, 1, 0.832743, 0.412499, '2026-04-17 23:16:29'),
(40, 1, 0.786294, 0.180544, '2026-04-17 23:16:30'),
(41, 1, 0.726777, -0.0241327, '2026-04-17 23:16:31'),
(42, 1, 0.658494, -0.244297, '2026-04-17 23:16:32'),
(43, 1, 0.597569, -0.457125, '2026-04-17 23:16:33'),
(44, 1, 0.526204, -0.743147, '2026-04-17 23:16:34'),
(45, 1, 0.490313, -0.855993, '2026-04-17 23:16:35'),
(46, 1, 0.476726, -0.722442, '2026-04-17 23:17:42'),
(47, 1, 0.591732, -0.426987, '2026-04-17 23:17:43'),
(48, 1, 0.677808, -0.125392, '2026-04-17 23:17:45'),
(49, 1, 0.737099, 0.0775573, '2026-04-17 23:17:46'),
(50, 1, 0.82592, 0.411213, '2026-04-17 23:17:47'),
(51, 1, 0.923967, 0.710575, '2026-04-17 23:17:49'),
(52, 1, 0.99005, 0.941308, '2026-04-17 23:17:52'),
(53, 1, 0.99005, 0.941308, '2026-04-18 00:04:44'),
(54, 1, 0.998547, 1.05926, '2026-04-18 00:05:25'),
(55, 1, 1.00759, 1.17572, '2026-04-18 00:05:28'),
(56, 1, 1.01746, 1.29108, '2026-04-18 00:05:32'),
(57, 1, 1.02364, 1.41104, '2026-04-18 00:05:35'),
(58, 1, 1.03708, 1.52541, '2026-04-18 00:05:38'),
(59, 1, 1.0505, 1.64345, '2026-04-18 00:05:41'),
(60, 1, 1.06858, 1.76352, '2026-04-18 00:05:44'),
(61, 1, 1.08018, 1.87442, '2026-04-18 00:05:47'),
(62, 1, 1.09787, 1.99023, '2026-04-18 00:05:50'),
(63, 1, 1.09787, 1.99023, '2026-04-18 00:12:03'),
(64, 1, 1.11096, 2.04331, '2026-04-18 00:12:45'),
(65, 1, 1.12648, 1.96372, '2026-04-18 00:12:57'),
(66, 1, 1.10298, 1.80455, '2026-04-18 00:12:58'),
(67, 1, 1.09279, 1.69928, '2026-04-18 00:13:02'),
(68, 1, 1.07288, 1.59922, '2026-04-18 00:13:05'),
(69, 1, 1.05572, 1.48597, '2026-04-18 00:13:06'),
(70, 1, 1.03931, 1.3757, '2026-04-18 00:13:11'),
(71, 1, 1.02149, 1.24754, '2026-04-18 00:13:13'),
(72, 1, 1.02099, 1.19031, '2026-04-18 00:13:18'),
(73, 1, 1.00975, 1.12158, '2026-04-18 00:13:20'),
(74, 1, 1.00975, 1.12158, '2026-04-18 00:23:24'),
(75, 1, 0.975578, 1.02424, '2026-04-18 00:27:03'),
(76, 1, 0.934828, 0.895445, '2026-04-18 00:27:05'),
(77, 1, 0.908924, 0.783036, '2026-04-18 00:27:11'),
(78, 1, 0.889221, 0.709872, '2026-04-18 00:27:16'),
(79, 1, 0.0895751, 0.0349985, '2026-04-18 00:27:31'),
(80, 1, 0.0193322, 0.00941862, '2026-04-18 00:27:34'),
(81, 1, 0.0431084, -0.0608233, '2026-04-18 00:27:36'),
(82, 1, 0.094674, -0.220081, '2026-04-18 00:27:38'),
(83, 1, 0.126655, -0.324421, '2026-04-18 00:27:44'),
(84, 1, 0.181594, -0.442946, '2026-04-18 00:27:46'),
(85, 1, 0.237326, -0.557166, '2026-04-18 00:27:55'),
(86, 1, 0.28831, -0.56997, '2026-04-18 00:28:07'),
(87, 1, 0.354239, -0.403477, '2026-04-18 00:28:13'),
(88, 1, 0.397678, -0.290198, '2026-04-18 00:28:14'),
(89, 1, 0.434343, -0.198882, '2026-04-18 00:28:19'),
(90, 1, 0.492381, -0.0775273, '2026-04-18 00:28:25'),
(91, 1, 0.539594, 0.0265514, '2026-04-18 00:28:31'),
(92, 1, 0.590448, 0.130916, '2026-04-18 00:28:35'),
(93, 1, 0.640153, 0.247488, '2026-04-18 00:28:37'),
(94, 1, 0.697015, 0.355455, '2026-04-18 00:28:43'),
(95, 1, 0.761103, 0.478985, '2026-04-18 00:28:47'),
(96, 1, 0.80842, 0.602626, '2026-04-18 00:28:55'),
(97, 1, 0.86126, 0.717474, '2026-04-18 00:28:56'),
(98, 1, 0.918101, 0.835689, '2026-04-18 00:29:04'),
(99, 1, 0.977385, 0.942752, '2026-04-18 00:29:10'),
(100, 1, 0.933128, 0.900196, '2026-04-18 00:30:37'),
(101, 1, 0.838091, 0.801133, '2026-04-18 00:30:40'),
(102, 1, 0.754528, 0.717211, '2026-04-18 00:30:45'),
(103, 1, 0.658482, 0.632181, '2026-04-18 00:30:50'),
(104, 1, 0.526981, 0.508577, '2026-04-18 00:30:53'),
(105, 1, 0.432032, 0.415322, '2026-04-18 00:30:58'),
(106, 1, 0.332003, 0.314283, '2026-04-18 00:31:01'),
(107, 1, 0.24824, 0.236531, '2026-04-18 00:31:03'),
(108, 1, 0.167248, 0.162271, '2026-04-18 00:31:10'),
(109, 1, 0.108787, 0.105532, '2026-04-18 00:31:13'),
(110, 1, 0.0412452, 0.0413623, '2026-04-18 00:31:15'),
(111, 1, 0.0412452, 0.0413623, '2026-04-18 00:36:47'),
(112, 1, 0.0189882, 0.0377048, '2026-04-18 00:36:54'),
(113, 1, 0.037848, 0.0468838, '2026-04-18 00:36:57'),
(114, 1, 0.0542305, 0.0857848, '2026-04-18 00:37:06'),
(115, 1, 0.0845831, 0.131743, '2026-04-18 00:37:07'),
(116, 1, 0.214109, 0.246479, '2026-04-18 00:37:11'),
(117, 1, 0.310364, 0.348533, '2026-04-18 00:37:16'),
(118, 1, 0.46986, 0.494557, '2026-04-18 00:37:19'),
(119, 1, 0.509543, 0.523262, '2026-04-18 00:37:27'),
(120, 1, 0.639368, 0.648685, '2026-04-18 00:37:31'),
(121, 1, 0.715582, 0.729463, '2026-04-18 00:37:36'),
(122, 1, 0.766252, 0.781834, '2026-04-18 00:37:37'),
(123, 1, 0.867444, 0.88516, '2026-04-18 00:37:44'),
(124, 1, 0.94424, 0.952962, '2026-04-18 00:37:47'),
(125, 1, 0.961383, 0.968658, '2026-04-18 00:38:40'),
(126, 1, 0.954168, 0.942599, '2026-04-18 00:38:47'),
(127, 1, 0.925397, 0.906639, '2026-04-18 00:38:50'),
(128, 1, 0.825393, 0.818925, '2026-04-18 00:38:54'),
(129, 1, 0.758679, 0.754188, '2026-04-18 00:38:56'),
(130, 1, 0.641713, 0.645176, '2026-04-18 00:39:04'),
(131, 1, 0.566004, 0.568609, '2026-04-18 00:39:08'),
(132, 1, 0.510657, 0.501805, '2026-04-18 00:39:13'),
(133, 1, 0.441816, 0.427293, '2026-04-18 00:39:15'),
(134, 1, 0.354117, 0.323939, '2026-04-18 00:39:19'),
(135, 1, 0.252632, 0.22229, '2026-04-18 00:39:25'),
(136, 1, 0.160601, 0.130056, '2026-04-18 00:39:34'),
(137, 1, 0.047069, 0.0428505, '2026-04-18 00:39:39'),
(138, 1, 0.0427091, 0.0229543, '2026-04-19 19:19:48'),
(139, 1, 0.128242, 0.0916038, '2026-04-19 19:19:48'),
(140, 1, 0.268567, 0.252995, '2026-04-19 19:19:49'),
(141, 1, 0.414277, 0.420916, '2026-04-19 19:19:50'),
(142, 1, 0.561381, 0.570428, '2026-04-19 19:19:51'),
(143, 1, 0.731145, 0.713419, '2026-04-19 19:19:52'),
(144, 1, 0.846941, 0.824764, '2026-04-19 19:19:53'),
(145, 1, 0.948803, 0.936248, '2026-04-19 19:19:55'),
(146, 1, 0.933738, 0.957079, '2026-04-19 19:20:18'),
(147, 1, 0.937905, 0.936753, '2026-04-19 19:20:20'),
(148, 1, 0.89884, 0.892165, '2026-04-19 19:20:21'),
(149, 1, 0.656854, 0.657475, '2026-04-19 19:20:23'),
(150, 1, 0.505426, 0.490487, '2026-04-19 19:20:24'),
(151, 1, 0.346631, 0.343924, '2026-04-19 19:20:25'),
(152, 1, 0.201155, 0.191629, '2026-04-19 19:20:26'),
(153, 1, 0.0726738, 0.0718848, '2026-04-19 19:20:27'),
(154, 1, 0.0523957, 0.0306889, '2026-04-19 20:29:31'),
(155, 1, 0.137856, 0.105614, '2026-04-19 20:29:32'),
(156, 1, 0.275603, 0.265698, '2026-04-19 20:29:33'),
(157, 1, 0.427657, 0.430306, '2026-04-19 20:29:34'),
(158, 1, 0.573152, 0.58504, '2026-04-19 20:29:35'),
(159, 1, 0.734048, 0.743545, '2026-04-19 20:29:36'),
(160, 1, 0.845852, 0.845606, '2026-04-19 20:29:37'),
(161, 1, 0.941934, 0.951061, '2026-04-19 20:29:38'),
(162, 1, 0.0645748, 0.0400917, '2026-04-20 13:29:13'),
(163, 1, 0.15204, 0.116399, '2026-04-20 13:29:14'),
(164, 1, 0.292564, 0.280103, '2026-04-20 13:29:15'),
(165, 1, 0.43762, 0.439486, '2026-04-20 13:29:16'),
(166, 1, 0.600896, 0.588598, '2026-04-20 13:29:17'),
(167, 1, 0.748704, 0.729179, '2026-04-20 13:29:18'),
(168, 1, 0.854744, 0.840246, '2026-04-20 13:29:19'),
(169, 1, 0.949254, 0.947253, '2026-04-20 13:29:20'),
(170, 1, 0.966369, 0.964607, '2026-04-20 13:35:36'),
(171, 1, 0.924633, 0.945175, '2026-04-20 13:35:39'),
(172, 1, 0.836262, 0.862064, '2026-04-20 13:35:40'),
(173, 1, 0.691634, 0.696735, '2026-04-20 13:35:41'),
(174, 1, 0.549757, 0.52658, '2026-04-20 13:35:42'),
(175, 1, 0.389229, 0.363289, '2026-04-20 13:35:43'),
(176, 1, 0.227673, 0.220342, '2026-04-20 13:35:44'),
(177, 1, 0.127213, 0.121986, '2026-04-20 13:35:45'),
(178, 1, 0.013766, 0.0335246, '2026-04-20 13:35:47');

-- --------------------------------------------------------

--
-- Table structure for table `Robot`
--

DROP TABLE IF EXISTS `Robot`;
CREATE TABLE `Robot` (
  `RobotID` int(11) NOT NULL,
  `Nombre` varchar(50) NOT NULL,
  `Descripcion` varchar(255) DEFAULT NULL,
  `Bateria` int(11) NOT NULL,
  `CamaraActiva` tinyint(1) NOT NULL,
  `UltimaComunicacion` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

--
-- Dumping data for table `Robot`
--

INSERT INTO `Robot` (`RobotID`, `Nombre`, `Descripcion`, `Bateria`, `CamaraActiva`, `UltimaComunicacion`) VALUES
(1, 'Roberto1', 'GuiaPuertas', 85, 1, '2026-04-12 16:13:33'),
(2, 'Roberto2', 'GuiaOcio', 42, 1, '2026-04-12 16:13:33'),
(3, 'ROBERTO', 'Robot de transporte de equipaje (Terminal 1)', 85, 1, '2026-04-12 21:06:20');

-- --------------------------------------------------------

--
-- Table structure for table `Tecnico`
--

DROP TABLE IF EXISTS `Tecnico`;
CREATE TABLE `Tecnico` (
  `TecnicoID` int(11) NOT NULL,
  `Nombre` varchar(100) NOT NULL,
  `Email` varchar(100) NOT NULL,
  `Contrasena` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

--
-- Dumping data for table `Tecnico`
--

INSERT INTO `Tecnico` (`TecnicoID`, `Nombre`, `Email`, `Contrasena`) VALUES
(1, 'John Doe', 'john@airport.com', 'pass123'),
(2, 'Jane Smith', 'jane@airport.com', 'secure456'),
(3, 'Operador Principal', 'admin@aeropuerto.com', 'admin1234');

-- --------------------------------------------------------

--
-- Table structure for table `Zona`
--

DROP TABLE IF EXISTS `Zona`;
CREATE TABLE `Zona` (
  `ZonaID` int(11) NOT NULL,
  `AeropuertoCodigo` varchar(10) NOT NULL,
  `Nombre` varchar(50) NOT NULL,
  `TipoZona` varchar(50) DEFAULT NULL,
  `PosX` float NOT NULL,
  `PosY` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

--
-- Dumping data for table `Zona`
--

INSERT INTO `Zona` (`ZonaID`, `AeropuertoCodigo`, `Nombre`, `TipoZona`, `PosX`, `PosY`) VALUES
(3, 'MAD', 'Puerta 12', 'Puerta', 0, 0),
(4, 'MAD', 'Puerta 4', 'Puerta', 1, 1),
(5, 'MAD', 'Puerta 8', 'Puerta', 0.275, -0.775),
(6, 'MAD', 'Puerta 21', 'Puerta', 0.45, -1),
(7, 'MAD', 'Restaurante VIP', 'Comida', 0.15, -0.43875),
(8, 'MAD', 'Burger King', 'Comida', 0.125, -0.375),
(9, 'MAD', 'Cafetería Starbucks', 'Comida', 0.13875, -0.4),
(10, 'MAD', 'Tapas Bar', 'Comida', 0.175, -0.475),
(11, 'MAD', 'Duty Free Principal', 'Ocio', 0.2, -0.5),
(12, 'MAD', 'Tienda de Electrónica', 'Ocio', 0.2125, -0.525),
(13, 'MAD', 'Librería y Prensa', 'Ocio', 0.20625, -0.5125),
(14, 'MAD', 'Farmacia y Salud', 'Ocio', 0.225, -0.55),
(15, 'MAD', 'Salida Principal T1', 'Salida', 0.025, -0.05),
(16, 'MAD', 'Recogida de Equipajes', 'Salida', 0.0375, -0.0625),
(17, 'MAD', 'Parada de Taxis', 'Salida', 0.0125, -0.025),
(18, 'MAD', 'Alquiler de Coches', 'Salida', 0.05, -0.0875);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `Aeropuerto`
--
ALTER TABLE `Aeropuerto`
  ADD PRIMARY KEY (`CodigoIATA`);

--
-- Indexes for table `Evento`
--
ALTER TABLE `Evento`
  ADD PRIMARY KEY (`EventoID`),
  ADD KEY `RobotID` (`RobotID`),
  ADD KEY `PosicionID` (`PosicionID`);

--
-- Indexes for table `Interaccion`
--
ALTER TABLE `Interaccion`
  ADD PRIMARY KEY (`InteraccionID`),
  ADD KEY `RobotID` (`RobotID`),
  ADD KEY `ZonaActualID` (`ZonaActualID`),
  ADD KEY `ZonaDestinoID` (`ZonaDestinoID`);

--
-- Indexes for table `Mantenimiento`
--
ALTER TABLE `Mantenimiento`
  ADD PRIMARY KEY (`MantenimientoID`),
  ADD KEY `RobotID` (`RobotID`),
  ADD KEY `TecnicoID` (`TecnicoID`);

--
-- Indexes for table `PosicionRobot`
--
ALTER TABLE `PosicionRobot`
  ADD PRIMARY KEY (`PosicionID`),
  ADD KEY `RobotID` (`RobotID`);

--
-- Indexes for table `Robot`
--
ALTER TABLE `Robot`
  ADD PRIMARY KEY (`RobotID`);

--
-- Indexes for table `Tecnico`
--
ALTER TABLE `Tecnico`
  ADD PRIMARY KEY (`TecnicoID`);

--
-- Indexes for table `Zona`
--
ALTER TABLE `Zona`
  ADD PRIMARY KEY (`ZonaID`),
  ADD KEY `AeropuertoCodigo` (`AeropuertoCodigo`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `Evento`
--
ALTER TABLE `Evento`
  MODIFY `EventoID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `Interaccion`
--
ALTER TABLE `Interaccion`
  MODIFY `InteraccionID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=24;

--
-- AUTO_INCREMENT for table `Mantenimiento`
--
ALTER TABLE `Mantenimiento`
  MODIFY `MantenimientoID` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `PosicionRobot`
--
ALTER TABLE `PosicionRobot`
  MODIFY `PosicionID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=179;

--
-- AUTO_INCREMENT for table `Robot`
--
ALTER TABLE `Robot`
  MODIFY `RobotID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `Tecnico`
--
ALTER TABLE `Tecnico`
  MODIFY `TecnicoID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `Zona`
--
ALTER TABLE `Zona`
  MODIFY `ZonaID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=19;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `Evento`
--
ALTER TABLE `Evento`
  ADD CONSTRAINT `Evento_ibfk_1` FOREIGN KEY (`RobotID`) REFERENCES `Robot` (`RobotID`),
  ADD CONSTRAINT `Evento_ibfk_2` FOREIGN KEY (`PosicionID`) REFERENCES `PosicionRobot` (`PosicionID`);

--
-- Constraints for table `Interaccion`
--
ALTER TABLE `Interaccion`
  ADD CONSTRAINT `Interaccion_ibfk_1` FOREIGN KEY (`RobotID`) REFERENCES `Robot` (`RobotID`),
  ADD CONSTRAINT `Interaccion_ibfk_2` FOREIGN KEY (`ZonaActualID`) REFERENCES `Zona` (`ZonaID`),
  ADD CONSTRAINT `Interaccion_ibfk_3` FOREIGN KEY (`ZonaDestinoID`) REFERENCES `Zona` (`ZonaID`);

--
-- Constraints for table `Mantenimiento`
--
ALTER TABLE `Mantenimiento`
  ADD CONSTRAINT `Mantenimiento_ibfk_1` FOREIGN KEY (`RobotID`) REFERENCES `Robot` (`RobotID`),
  ADD CONSTRAINT `Mantenimiento_ibfk_2` FOREIGN KEY (`TecnicoID`) REFERENCES `Tecnico` (`TecnicoID`);

--
-- Constraints for table `PosicionRobot`
--
ALTER TABLE `PosicionRobot`
  ADD CONSTRAINT `PosicionRobot_ibfk_1` FOREIGN KEY (`RobotID`) REFERENCES `Robot` (`RobotID`);

--
-- Constraints for table `Zona`
--
ALTER TABLE `Zona`
  ADD CONSTRAINT `Zona_ibfk_1` FOREIGN KEY (`AeropuertoCodigo`) REFERENCES `Aeropuerto` (`CodigoIATA`);
  
-- Volvemos a activar la comprobación de claves foráneas
SET FOREIGN_KEY_CHECKS = 1;

COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;