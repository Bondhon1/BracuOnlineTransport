-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Dec 18, 2024 at 04:27 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `mydatabase`
--

-- --------------------------------------------------------

--
-- Table structure for table `admins`
--

CREATE TABLE `admins` (
  `admin_id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `email` varchar(200) NOT NULL,
  `password` varchar(200) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `admins`
--

INSERT INTO `admins` (`admin_id`, `name`, `email`, `password`) VALUES
(1, 'bondhon', 'bondhon1@gmail.com', 'bondhon1'),
(3, 'sadman', 'sadman@gmail.com', '123456');

-- --------------------------------------------------------

--
-- Table structure for table `bus_routes`
--

CREATE TABLE `bus_routes` (
  `route_id` int(11) NOT NULL,
  `route_name` varchar(100) NOT NULL,
  `bus_number` varchar(50) NOT NULL,
  `driver_name` varchar(100) DEFAULT NULL,
  `capacity` int(11) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `bus_routes`
--

INSERT INTO `bus_routes` (`route_id`, `route_name`, `bus_number`, `driver_name`, `capacity`, `created_at`) VALUES
(1, 'Abdullahpur', '01', 'Rahim', 30, '2024-12-17 03:20:34'),
(6, 'Mirpur', '02', 'Karim', 30, '2024-12-17 03:31:09'),
(7, 'Gabtoli', '10', 'Sadman', 50, '2024-12-18 04:17:34');

-- --------------------------------------------------------

--
-- Table structure for table `bus_schedules`
--

CREATE TABLE `bus_schedules` (
  `id` int(11) NOT NULL,
  `route_name` varchar(100) NOT NULL,
  `departure_time` time NOT NULL,
  `arrival_time` time NOT NULL,
  `bus_number` varchar(50) NOT NULL,
  `driver_name` varchar(100) DEFAULT NULL,
  `capacity` int(11) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `bus_schedules`
--

INSERT INTO `bus_schedules` (`id`, `route_name`, `departure_time`, `arrival_time`, `bus_number`, `driver_name`, `capacity`, `created_at`) VALUES
(1, 'Abdullahpur', '07:00:00', '08:00:00', '1', 'Rahim', 30, '2024-12-16 17:49:19');

-- --------------------------------------------------------

--
-- Table structure for table `feedback`
--

CREATE TABLE `feedback` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `bus_number` varchar(50) NOT NULL,
  `feedback` text NOT NULL,
  `rating` int(11) NOT NULL,
  `journey_date` date NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `name` varchar(50) NOT NULL,
  `email` varchar(50) NOT NULL,
  `reply` varchar(200) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `feedback`
--

INSERT INTO `feedback` (`id`, `user_id`, `bus_number`, `feedback`, `rating`, `journey_date`, `created_at`, `name`, `email`, `reply`) VALUES
(1, 3, '1', 'yjtasfcuhcu sdiuvh sdiuch Worst', 1, '2024-12-17', '2024-12-18 03:49:13', 'Test2', 'test@gmail.com', '?'),
(2, 3, '02', 'iusd jhsdsh iusdh kids', 5, '2024-12-09', '2024-12-18 04:12:17', 'Test2', 'test@gmail.com', '?'),
(3, 3, '3', 'good dggfchcfgh', 2, '2024-12-04', '2024-12-18 04:32:47', 'Test2', 'test@gmail.com', '!'),
(4, 3, '01', 'dth fgbgfgb dfb xf dfbdg', 3, '2024-12-17', '2024-12-18 14:17:44', 'Test2', 'test@gmail.com', '.....');

-- --------------------------------------------------------

--
-- Table structure for table `route_stops`
--

CREATE TABLE `route_stops` (
  `stop_id` int(11) NOT NULL,
  `route_id` int(11) NOT NULL,
  `stop_name` varchar(100) NOT NULL,
  `pickup_time` time NOT NULL,
  `dropoff_time` time NOT NULL,
  `fare` decimal(10,2) NOT NULL,
  `stop_type` enum('pickup','dropoff') NOT NULL,
  `seat_numbers` text NOT NULL,
  `male_seats` int(11) NOT NULL,
  `female_seats` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `route_stops`
--

INSERT INTO `route_stops` (`stop_id`, `route_id`, `stop_name`, `pickup_time`, `dropoff_time`, `fare`, `stop_type`, `seat_numbers`, `male_seats`, `female_seats`) VALUES
(1, 1, 'Abdullahpur', '06:40:00', '07:30:00', 90.00, 'pickup', '', 0, 0),
(2, 6, 'Mirpur Bangla Collage', '06:20:00', '08:30:00', 90.00, 'pickup', '', 0, 0),
(3, 1, 'House Building', '06:43:00', '07:30:00', 90.00, 'pickup', 'A1, A2, B1, B2', 2, 2),
(4, 7, 'Kollyanpur', '07:00:00', '07:30:00', 50.00, 'pickup', 'A1,A2,B1,B2', 2, 2);

-- --------------------------------------------------------

--
-- Table structure for table `staffs`
--

CREATE TABLE `staffs` (
  `id` int(11) NOT NULL,
  `initial` varchar(3) NOT NULL,
  `email` varchar(200) NOT NULL,
  `password` varchar(200) NOT NULL,
  `full_name` varchar(200) NOT NULL,
  `pin` int(11) NOT NULL,
  `department` varchar(20) NOT NULL,
  `address` varchar(200) NOT NULL,
  `mobile_number` int(11) NOT NULL,
  `blood_group` varchar(20) NOT NULL,
  `registration_date` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `profile_image` varchar(200) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `staffs`
--

INSERT INTO `staffs` (`id`, `initial`, `email`, `password`, `full_name`, `pin`, `department`, `address`, `mobile_number`, `blood_group`, `registration_date`, `profile_image`) VALUES
(1, 'ZAZ', 'izaz@bracu.ac.bd', '$2b$12$z0mfv8qGsrZ2CnsMPaxSweqN6z2/SiGFBzzUDKj5Zy7x6IUMslwMS', '', 0, '', '', 0, '', '2024-12-17 18:36:02', '');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `email` varchar(200) NOT NULL,
  `password` varchar(200) NOT NULL,
  `full_name` varchar(200) NOT NULL,
  `student_id` int(11) NOT NULL,
  `department` varchar(20) NOT NULL,
  `address` varchar(200) NOT NULL,
  `mobile_number` int(11) NOT NULL,
  `blood_group` varchar(20) NOT NULL,
  `registration_date` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `profile_image` varchar(200) NOT NULL,
  `Gender` varchar(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `name`, `email`, `password`, `full_name`, `student_id`, `department`, `address`, `mobile_number`, `blood_group`, `registration_date`, `profile_image`, `Gender`) VALUES
(3, 'Test2', 'test@gmail.com', '$2b$12$V1NHub3q9r.beB4JasL6/u8B0Ex1CpOWWQ7WUWNK0P/JAfXWatSR2', 'Bondhon', 22101459, 'CSE', '16/2 Rajshahi1', 1796381258, 'B+', '2024-12-17 18:00:08', '20220205_130930.jpg', 'male');

-- --------------------------------------------------------

--
-- Table structure for table `vehicle_requests`
--

CREATE TABLE `vehicle_requests` (
  `id` int(11) NOT NULL,
  `staff_id` int(11) NOT NULL,
  `journey_date` date NOT NULL,
  `pickup_location` varchar(100) NOT NULL,
  `destination` varchar(100) NOT NULL,
  `capacity` int(11) NOT NULL,
  `status` varchar(50) DEFAULT 'Pending',
  `reply` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `vehicle_requests`
--

INSERT INTO `vehicle_requests` (`id`, `staff_id`, `journey_date`, `pickup_location`, `destination`, `capacity`, `status`, `reply`, `created_at`) VALUES
(1, 1, '2012-12-24', 'BRACU', 'Abdullahpur', 10, 'Approved', '01', '2024-12-18 03:29:41'),
(2, 1, '0000-00-00', 'BRACU', 'Badda', 4, 'Approved', '01', '2024-12-18 04:04:21'),
(3, 1, '0000-00-00', 'BRACU', 'Badda', 4, 'Approved', '01', '2024-12-18 04:05:11'),
(4, 1, '2024-12-12', 'asc', 'def', 2, 'Pending', NULL, '2024-12-18 04:07:13'),
(5, 1, '2024-12-12', 'Bracu', 'Badda', 6, 'Pending', NULL, '2024-12-18 04:34:45');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `admins`
--
ALTER TABLE `admins`
  ADD PRIMARY KEY (`admin_id`);

--
-- Indexes for table `bus_routes`
--
ALTER TABLE `bus_routes`
  ADD PRIMARY KEY (`route_id`);

--
-- Indexes for table `bus_schedules`
--
ALTER TABLE `bus_schedules`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `feedback`
--
ALTER TABLE `feedback`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `route_stops`
--
ALTER TABLE `route_stops`
  ADD PRIMARY KEY (`stop_id`),
  ADD KEY `route_id` (`route_id`);

--
-- Indexes for table `staffs`
--
ALTER TABLE `staffs`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `vehicle_requests`
--
ALTER TABLE `vehicle_requests`
  ADD PRIMARY KEY (`id`),
  ADD KEY `staff_id` (`staff_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `admins`
--
ALTER TABLE `admins`
  MODIFY `admin_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `bus_routes`
--
ALTER TABLE `bus_routes`
  MODIFY `route_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `bus_schedules`
--
ALTER TABLE `bus_schedules`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `feedback`
--
ALTER TABLE `feedback`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `route_stops`
--
ALTER TABLE `route_stops`
  MODIFY `stop_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `staffs`
--
ALTER TABLE `staffs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `vehicle_requests`
--
ALTER TABLE `vehicle_requests`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `feedback`
--
ALTER TABLE `feedback`
  ADD CONSTRAINT `feedback_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `route_stops`
--
ALTER TABLE `route_stops`
  ADD CONSTRAINT `route_stops_ibfk_1` FOREIGN KEY (`route_id`) REFERENCES `bus_routes` (`route_id`) ON DELETE CASCADE;

--
-- Constraints for table `vehicle_requests`
--
ALTER TABLE `vehicle_requests`
  ADD CONSTRAINT `vehicle_requests_ibfk_1` FOREIGN KEY (`staff_id`) REFERENCES `staffs` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
