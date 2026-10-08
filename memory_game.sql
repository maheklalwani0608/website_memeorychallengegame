-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Oct 08, 2026 at 11:10 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `memory_game`
--

-- --------------------------------------------------------

--
-- Table structure for table `game_scores`
--

CREATE TABLE `game_scores` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `score` int(11) NOT NULL,
  `level` int(11) NOT NULL,
  `result` varchar(20) DEFAULT NULL,
  `played_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `game_type` varchar(20) NOT NULL DEFAULT 'Digits'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `game_scores`
--

INSERT INTO `game_scores` (`id`, `user_id`, `score`, `level`, `result`, `played_at`, `game_type`) VALUES
(35, 25, 20, 3, 'Lost', '2026-09-28 06:43:55', 'Digits'),
(40, 27, 10, 1, 'Won', '2026-09-28 07:28:11', 'Digits'),
(58, 22, 10, 1, 'Won', '2026-10-07 06:38:48', 'Words'),
(59, 22, 40, 1, 'Won', '2026-10-07 06:39:17', 'Words'),
(60, 22, 10, 2, 'Lost', '2026-10-07 06:40:19', 'Digits'),
(61, 25, 20, 3, 'Lost', '2026-10-08 05:51:06', 'Digits'),
(62, 25, 0, 1, 'Lost', '2026-10-08 05:52:31', 'Digits'),
(63, 25, 0, 1, 'Lost', '2026-10-08 05:52:55', 'Words'),
(64, 25, 20, 3, 'Lost', '2026-10-08 06:10:56', 'Digits'),
(65, 25, 30, 1, 'Won', '2026-10-08 06:17:19', 'Words'),
(66, 25, 10, 2, 'Lost', '2026-10-08 07:40:11', 'Digits');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `email`, `password`, `created_at`) VALUES
(22, 'a', 'a@gmail.com', 'a', '2026-09-19 03:10:09'),
(23, 'B', 'b@gmail.com', 'b', '2026-09-19 06:12:38'),
(25, 'bhumika', 'bh@gmail.com', 'bh', '2026-09-28 05:24:23'),
(26, 'jon', 'j@gmail.com', 'j', '2026-09-28 07:04:28'),
(27, 'RT', 'rt@gmail.com', '123', '2026-09-28 07:19:15'),
(28, 'aarti', 'a@gmail.com', 'a', '2026-10-07 05:52:52'),
(29, 'bhumika', 'bh@gmail.com', 'bh', '2026-10-08 05:49:42');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `game_scores`
--
ALTER TABLE `game_scores`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `game_scores`
--
ALTER TABLE `game_scores`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=67;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=30;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `game_scores`
--
ALTER TABLE `game_scores`
  ADD CONSTRAINT `game_scores_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
