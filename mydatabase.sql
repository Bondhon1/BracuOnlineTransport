-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Dec 31, 2024 at 05:35 PM
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
(1, 'bondhon', 'bondhon1@gmail.com', 'bondhon1');

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
(1, 'Abdullahpur', '01', 'Rahim', 40, '2024-12-17 03:20:34'),
(8, 'Mirpur-A', '02', 'Karim', 40, '2024-12-23 13:45:21');

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
  `reply` varchar(200) DEFAULT NULL,
  `viewed` tinyint(1) DEFAULT 0,
  `route_name` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `feedback`
--

INSERT INTO `feedback` (`id`, `user_id`, `bus_number`, `feedback`, `rating`, `journey_date`, `created_at`, `name`, `email`, `reply`, `viewed`, `route_name`) VALUES
(1, 3, '1', 'yjtasfcuhcu sdiuvh sdiuch Worst', 1, '2024-12-17', '2024-12-18 03:49:13', 'Test2', 'test@gmail.com', '?', 1, ''),
(2, 3, '02', 'iusd jhsdsh iusdh kids', 5, '2024-12-09', '2024-12-18 04:12:17', 'Test2', 'test@gmail.com', '?', 1, ''),
(3, 3, '3', 'good dggfchcfgh', 2, '2024-12-04', '2024-12-18 04:32:47', 'Test2', 'test@gmail.com', '!', 1, ''),
(4, 3, '01', 'dth fgbgfgb dfb xf dfbdg', 3, '2024-12-17', '2024-12-18 14:17:44', 'Test2', 'test@gmail.com', '.....', 1, ''),
(5, 3, '2', 'zfd fdv dffv dfvvdfv', 5, '2024-12-18', '2024-12-19 13:02:18', 'Test2', 'test@gmail.com', 'ok', 1, ''),
(6, 3, '02', 'yg jhg hgf ygx jhgx', 4, '2024-12-20', '2024-12-21 05:47:18', 'Test2', 'test@gmail.com', '1', 1, ''),
(8, 11, '01', 'fv ffb dv sdf sdc', 2, '2024-12-25', '2024-12-26 13:51:06', 'Bondhon2', 'bondhon0101@gmail.com', 'ok', 1, 'Abdullahpur'),
(9, 11, '02', 'ghgc ttu ygj gj', 5, '2024-12-25', '2024-12-27 11:39:32', 'Bondhon2', 'bondhon0101@gmail.com', 'ok', 1, 'Abdullahpur'),
(10, 11, '01', 'sdcf vfds ddff', 5, '2024-12-25', '2024-12-27 11:46:57', 'Bondhon2', 'bondhon0101@gmail.com', 'ok', 1, 'Abdullahpur'),
(11, 11, '01', 'ffbb gg fbh fbfg f', 5, '2024-12-26', '2024-12-27 11:59:52', 'Bondhon2', 'bondhon0101@gmail.com', 'pp', 1, 'Abdullahpur'),
(12, 11, '02', 'hh fdb fdv dvsd dv', 4, '2024-12-27', '2024-12-28 16:34:50', 'Bondhon2', 'bondhon0101@gmail.com', 'ok', 1, 'Mirpur-A');

-- --------------------------------------------------------

--
-- Table structure for table `route_stops`
--

CREATE TABLE `route_stops` (
  `stop_id` int(11) NOT NULL,
  `route_id` int(11) NOT NULL,
  `stop_name` varchar(100) NOT NULL,
  `pickup_time` time DEFAULT NULL,
  `dropoff_time` time DEFAULT NULL,
  `fare` decimal(10,2) NOT NULL,
  `stop_type` enum('pickup','dropoff') NOT NULL,
  `seat_numbers` text NOT NULL,
  `male_seats` text DEFAULT NULL,
  `female_seats` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `route_stops`
--

INSERT INTO `route_stops` (`stop_id`, `route_id`, `stop_name`, `pickup_time`, `dropoff_time`, `fare`, `stop_type`, `seat_numbers`, `male_seats`, `female_seats`) VALUES
(6, 1, 'Abdullahpur', '06:40:00', '07:30:00', 90.00, 'pickup', 'A1,A2,B1,B2', 'A1,A2', 'B1,B2'),
(7, 1, 'House Building (Labaid Diagnostic)', '06:43:00', '07:30:00', 90.00, 'pickup', 'A3,A4,B3,B4', 'A3,A4', 'B3,B4'),
(8, 1, 'Azampur (in front of Uttara East Police Station)', '06:46:00', '07:30:00', 90.00, 'pickup', 'C1,C2,C3,C4', 'C1,C2', 'C3,C4'),
(9, 1, 'Jasimuddin (Popular Diagnostic Centre)', '06:49:00', '07:30:00', 90.00, 'pickup', 'D1,D2,D3,D4', 'D1,D2', 'D3,D4'),
(10, 1, 'Airport (in front of police box)', '06:51:00', '07:30:00', 90.00, 'pickup', 'E1,E2,E3,E4', 'E1,E2', 'E3,E4'),
(11, 1, 'Kawla (near foot over-bridge)', '06:52:00', '07:30:00', 90.00, 'pickup', 'F1,F2,F3,F4', 'F1,F2', 'F3,F4'),
(12, 1, 'Khilkhet (first foot over-bridge coming from Uttara)', '06:56:00', '07:30:00', 90.00, 'pickup', 'G1,G2,G3,G4', 'G1,G2', 'G3,G4'),
(13, 1, 'Biswa Road (near foot over-bridge)', '06:59:00', '07:30:00', 90.00, 'pickup', 'H1,H2,H3,H4', 'H1,H2', 'H3,H4'),
(14, 1, 'Shewrah (near foot over-bridge)', '07:00:00', '07:30:00', 90.00, 'pickup', 'I1,I2,I3,I4', 'I1,I2', 'I3,I4'),
(16, 8, 'Mirpur Bangla College', '06:20:00', '07:20:00', 90.00, 'pickup', 'A1,A2,B1,B2', 'A1,A2', 'B1,B2'),
(17, 8, 'Sony Cinema Hall (near KFC)', '06:24:00', '07:20:00', 90.00, 'pickup', 'C1,C2,D1,D2', 'C1,C2', 'D1,D2'),
(18, 8, 'Mirpur College Gate (Mirpur 2)', '06:26:00', '07:20:00', 90.00, 'pickup', 'E1,E2,E3,E4', 'E1,E2', 'E3,E4'),
(19, 8, 'Swimming Federation Gate (Mirpur stadium)', '06:28:00', '07:20:00', 90.00, 'pickup', 'F1,F2,F3,F4', 'F1,F2', 'F3,F4'),
(20, 8, 'Popular Diagnostic Centre (Mirpur 6)', '06:31:00', '07:20:00', 80.00, 'pickup', 'G1,G2,G3,G4', 'G1,G2', 'G3,G4'),
(21, 8, 'Pallabi Post Office (near Purobi Cinema Hall)', '06:34:00', '07:20:00', 70.00, 'pickup', 'A3,A4,B3,B4', 'A3,A4', 'B3,B4'),
(22, 8, 'Mirpur Ceramics (near CNG filling station)', '06:36:00', '07:20:00', 70.00, 'pickup', 'C3,C4,D3,D4', 'C3,C4', 'D3,D4'),
(23, 8, 'Mirpur DOHS Gate (near Trust bus stop)', '06:40:00', '07:20:00', 60.00, 'pickup', 'H1,H2,H3,H4', 'H1,H2', 'H3,H4'),
(24, 8, 'Pallabi Thana (Shagufta mour)', '06:43:00', '07:20:00', 60.00, 'pickup', 'I1,I2,I3,I4', 'I1,I2', 'I3,I4'),
(25, 8, 'Kalshi Bus Stand', '06:45:00', '07:20:00', 50.00, 'pickup', 'J1,J3', 'J1', 'J3'),
(26, 8, 'ECB Chattar', '06:48:00', '07:20:00', 50.00, 'pickup', 'J2,J4', 'J2', 'J4'),
(27, 1, 'Abdullahpur', NULL, '14:05:00', 90.00, 'dropoff', 'A1,A2,B1,B2', 'A1,A2', 'B1,B2'),
(28, 8, 'ABC', NULL, '07:00:00', 90.00, 'dropoff', 'D1,D2,D3,D4,E1,E2', 'D1,D2,D3', 'D4,E1,E2'),
(29, 8, 'DEF', NULL, NULL, 80.00, 'pickup', 'A1,A2,A3,A4', 'A1,A2', 'A3,A4'),
(30, 8, 'DEF', NULL, NULL, 70.00, 'dropoff', 'B1,B2,B3,B4', 'B1,B2', 'B3,B4');

-- --------------------------------------------------------

--
-- Table structure for table `seat_bookings`
--

CREATE TABLE `seat_bookings` (
  `booking_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `route_id` int(11) NOT NULL,
  `stop_id` int(11) NOT NULL,
  `seat_number` varchar(10) NOT NULL,
  `journey_date` date NOT NULL,
  `journey_type` varchar(15) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `seat_bookings`
--

INSERT INTO `seat_bookings` (`booking_id`, `user_id`, `route_id`, `stop_id`, `seat_number`, `journey_date`, `journey_type`) VALUES
(41, 11, 1, 6, 'A1', '2024-12-25', 'pickup'),
(55, 11, 1, 9, 'D1', '2024-12-26', 'pickup'),
(59, 11, 8, 28, 'D1', '2024-12-27', 'dropoff'),
(73, 12, 1, 8, 'C1', '2024-12-30', 'pickup'),
(74, 12, 1, 11, 'F1', '2024-12-31', 'pickup');

-- --------------------------------------------------------

--
-- Table structure for table `seat_status`
--

CREATE TABLE `seat_status` (
  `route_id` int(11) NOT NULL,
  `seat_number` varchar(10) NOT NULL,
  `journey_date` date NOT NULL,
  `journey_type` enum('Pickup','Dropoff') NOT NULL,
  `status` enum('Available','Booked') DEFAULT 'Available',
  `reserved_for` enum('Male','Female','None') DEFAULT 'None'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

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
  `profile_image` varchar(200) NOT NULL,
  `verified` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `staffs`
--

INSERT INTO `staffs` (`id`, `initial`, `email`, `password`, `full_name`, `pin`, `department`, `address`, `mobile_number`, `blood_group`, `registration_date`, `profile_image`, `verified`) VALUES
(1, 'ZAZ', 'bondhonfiles@gmail.com', '$2b$12$z0mfv8qGsrZ2CnsMPaxSweqN6z2/SiGFBzzUDKj5Zy7x6IUMslwMS', 'Ihzaz Ahmed', 12345, 'CSE', 'Dhaka', 1711111111, 'O+', '2024-12-20 09:16:17', '20220211_172426.jpg', 0);

-- --------------------------------------------------------

--
-- Table structure for table `trip_times`
--

CREATE TABLE `trip_times` (
  `trip_id` int(11) NOT NULL,
  `stop_id` int(11) NOT NULL,
  `trip_time` time NOT NULL,
  `shift` int(11) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `trip_times`
--

INSERT INTO `trip_times` (`trip_id`, `stop_id`, `trip_time`, `shift`) VALUES
(1, 29, '06:40:00', 1),
(2, 30, '06:45:00', 1),
(3, 30, '12:45:00', 1),
(4, 6, '06:40:00', 1),
(5, 7, '06:43:00', 1),
(6, 8, '06:46:00', 1),
(7, 9, '06:49:00', 1),
(8, 10, '06:51:00', 1),
(9, 11, '06:52:00', 1),
(10, 12, '06:56:00', 1),
(11, 13, '06:59:00', 1),
(12, 14, '07:00:00', 1),
(13, 16, '06:20:00', 1),
(14, 17, '06:24:00', 1),
(15, 18, '06:26:00', 1),
(16, 19, '06:28:00', 1),
(17, 20, '06:31:00', 1),
(18, 21, '06:34:00', 1),
(19, 22, '06:36:00', 1),
(20, 23, '06:40:00', 1),
(21, 24, '06:43:00', 1),
(22, 25, '06:45:00', 1),
(23, 26, '06:48:00', 1),
(35, 27, '14:05:00', 2),
(36, 28, '07:00:00', 1);

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
  `Gender` varchar(6) NOT NULL,
  `verified` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `name`, `email`, `password`, `full_name`, `student_id`, `department`, `address`, `mobile_number`, `blood_group`, `registration_date`, `profile_image`, `Gender`, `verified`) VALUES
(3, 'Test2', 'test@gmail.com', '$2b$12$V1NHub3q9r.beB4JasL6/u8B0Ex1CpOWWQ7WUWNK0P/JAfXWatSR2', 'Bondhon', 22101459, 'CSE', '16/2 Rajshahi1', 1796381258, 'B+', '2024-12-22 18:19:27', '20220211_172451.jpg', 'Female', 1),
(11, 'Bondhon2', 'bondhon0101@gmail.com', '$2b$12$9P7EZzfbXDOTwMNCQX6nc.nFCoIEBxXsgh27Z0cdJGlW9DL.zWdp2', 'Bondhon 2', 22101458, 'CSE', '16/2 Rajshahi1', 1711111100, 'B+', '2024-12-22 13:01:16', '20220216_174052.jpg', 'Male', 1),
(12, 'Bondhon3', 'samiul.haque.bondhon@g.bracu.ac.bd', '$2b$12$hAC3uW/eLNkWY8cEtHj8b.NET/ZTiIVhl1698D6YWnhwGsV4zYfAq', 'Bondhon 3', 22101459, 'CSE', 'Dhaka', 1111111111, 'B-', '2024-12-24 17:42:13', '20220216_174052.jpg', 'Male', 1);

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
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `viewed` tinyint(1) DEFAULT 0,
  `pickup_time` time DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `vehicle_requests`
--

INSERT INTO `vehicle_requests` (`id`, `staff_id`, `journey_date`, `pickup_location`, `destination`, `capacity`, `status`, `reply`, `created_at`, `viewed`, `pickup_time`) VALUES
(9, 1, '2025-01-01', 'Badda', 'Mohakhali', 5, 'Approved', 'ok', '2024-12-20 13:34:50', 1, NULL),
(10, 1, '2025-12-31', 'Dhaka', 'Rajshahi', 1, 'Approved', 'ok', '2024-12-20 17:48:45', 1, NULL),
(11, 1, '2022-12-21', 'Mars', 'Earth', 12, 'Approved', 'ok.....', '2024-12-21 05:49:58', 1, NULL),
(12, 1, '2024-12-22', 'Dg', 'As', 12, 'Rejected', 'rejected', '2024-12-21 14:14:40', 1, '12:12:00'),
(13, 1, '2024-12-31', 'BRACU', 'Badda', 4, 'Approved', 'Ok', '2024-12-28 14:33:33', 1, '07:00:00'),
(14, 1, '2024-12-31', 'BRACU', 'Mars', 2, 'Rejected', 'rejected', '2024-12-28 14:39:58', 1, '08:30:00');

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
-- Indexes for table `seat_bookings`
--
ALTER TABLE `seat_bookings`
  ADD PRIMARY KEY (`booking_id`),
  ADD KEY `route_id` (`route_id`),
  ADD KEY `stop_id` (`stop_id`);

--
-- Indexes for table `seat_status`
--
ALTER TABLE `seat_status`
  ADD PRIMARY KEY (`route_id`,`seat_number`,`journey_date`,`journey_type`);

--
-- Indexes for table `staffs`
--
ALTER TABLE `staffs`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `trip_times`
--
ALTER TABLE `trip_times`
  ADD PRIMARY KEY (`trip_id`),
  ADD KEY `stop_id` (`stop_id`);

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
  MODIFY `admin_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `bus_routes`
--
ALTER TABLE `bus_routes`
  MODIFY `route_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `feedback`
--
ALTER TABLE `feedback`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT for table `route_stops`
--
ALTER TABLE `route_stops`
  MODIFY `stop_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=31;

--
-- AUTO_INCREMENT for table `seat_bookings`
--
ALTER TABLE `seat_bookings`
  MODIFY `booking_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=75;

--
-- AUTO_INCREMENT for table `staffs`
--
ALTER TABLE `staffs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `trip_times`
--
ALTER TABLE `trip_times`
  MODIFY `trip_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=37;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT for table `vehicle_requests`
--
ALTER TABLE `vehicle_requests`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

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
-- Constraints for table `seat_status`
--
ALTER TABLE `seat_status`
  ADD CONSTRAINT `seat_status_ibfk_1` FOREIGN KEY (`route_id`) REFERENCES `bus_routes` (`route_id`);

--
-- Constraints for table `trip_times`
--
ALTER TABLE `trip_times`
  ADD CONSTRAINT `trip_times_ibfk_1` FOREIGN KEY (`stop_id`) REFERENCES `route_stops` (`stop_id`) ON DELETE CASCADE;

--
-- Constraints for table `vehicle_requests`
--
ALTER TABLE `vehicle_requests`
  ADD CONSTRAINT `vehicle_requests_ibfk_1` FOREIGN KEY (`staff_id`) REFERENCES `staffs` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
