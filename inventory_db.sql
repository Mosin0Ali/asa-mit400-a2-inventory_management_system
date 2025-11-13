-- phpMyAdmin SQL Dump
-- version 5.2.2
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Nov 13, 2025 at 12:50 AM
-- Server version: 9.3.0
-- PHP Version: 8.2.28

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `inventory_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `orders`
--

CREATE TABLE `orders` (
  `order_id` int NOT NULL,
  `order_date` date NOT NULL,
  `supplier_name` varchar(255) NOT NULL,
  `expected_delivery_date` date DEFAULT NULL,
  `status` enum('Pending','Shipped','Received','Cancelled') NOT NULL DEFAULT 'Pending',
  `total_cost` decimal(10,2) DEFAULT NULL,
  `notes` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `orders`
--

INSERT INTO `orders` (`order_id`, `order_date`, `supplier_name`, `expected_delivery_date`, `status`, `total_cost`, `notes`) VALUES
(1, '2025-11-09', 'Mega Supply Co.', '2025-12-01', 'Pending', 500.00, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `products`
--

CREATE TABLE `products` (
  `product_id` int NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` text,
  `stock_quantity` int NOT NULL DEFAULT '0',
  `unit_price` decimal(10,2) NOT NULL,
  `cost_price` decimal(10,2) NOT NULL,
  `reorder_point` int NOT NULL DEFAULT '10',
  `date_added` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `products`
--

INSERT INTO `products` (`product_id`, `name`, `description`, `stock_quantity`, `unit_price`, `cost_price`, `reorder_point`, `date_added`) VALUES
(1, 'Product A - Widgets', 'Standard small widget.', 27, 9.99, 4.50, 15, '2025-11-09 08:08:19'),
(2, 'Product B - Gadgets', 'Advanced electronic gadget.', 6, 49.99, 25.00, 5, '2025-11-09 08:08:19'),
(3, 'Product C - Doodads', 'Decorative item for homes.', 0, 15.00, 7.50, 30, '2025-11-09 08:08:19'),
(5, 'Mac Air m2', 'Mac Air m2', 8, 200.00, 100.00, 10, '2025-11-09 18:43:24'),
(6, 'Nike Air Jordans', 'Nike Air Superfly SP TM · Nike Air Superfly SP TM Women\'s Shoes ; Jordan Tatum 4 · Jordan Tatum 4 Basketball Shoes ; Air Jordan 1 Low · Air Jordan ...', 12, 220.00, 120.00, 10, '2025-11-10 19:51:02'),
(7, 'Nora Coleman', 'Culpa at magnam faci', 888, 682.00, 238.00, 43, '2025-11-11 06:57:28'),
(8, 'Mac Pro', 'Mac ProMac ProMac ProMac ProMac ProMac Pro', 9, 2500.00, 2100.00, 10, '2025-11-12 03:20:32'),
(9, 'Toilet paper', 'soft smooth', 993, 3.99, 2.00, 10, '2025-11-13 00:33:47');

-- --------------------------------------------------------

--
-- Table structure for table `sales`
--

CREATE TABLE `sales` (
  `sale_id` int NOT NULL,
  `sale_date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `customer_name` varchar(255) DEFAULT NULL,
  `total_amount` decimal(10,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `sales`
--

INSERT INTO `sales` (`sale_id`, `sale_date`, `customer_name`, `total_amount`) VALUES
(1, '2025-11-09 19:08:19', 'Alice Johnson', 59.98),
(2, '2025-11-10 05:49:33', 'Mohsin', 9.99),
(3, '2025-11-10 05:49:59', 'Mozil', 200.00),
(4, '2025-11-11 06:39:55', 'Deepak', 5.00),
(5, '2025-11-11 06:40:58', 'Sanjog', 29.99),
(6, '2025-11-11 06:46:37', 'Manjo', 25.00),
(7, '2025-11-11 06:49:27', 'Bob', 7.50),
(8, '2025-11-11 06:51:19', 'Micheal', 66.00),
(9, '2025-11-11 17:57:38', 'Mark', 99.90),
(10, '2025-11-12 12:57:00', 'Hasan', 7500.00),
(11, '2025-11-12 14:20:50', 'Mark', 25000.00),
(12, '2025-11-13 11:35:20', 'Mohsin', 4261.88);

-- --------------------------------------------------------

--
-- Table structure for table `sale_items`
--

CREATE TABLE `sale_items` (
  `item_id` int NOT NULL,
  `sale_id` int NOT NULL,
  `product_id` int NOT NULL,
  `quantity_sold` int NOT NULL,
  `sale_price` decimal(10,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `sale_items`
--

INSERT INTO `sale_items` (`item_id`, `sale_id`, `product_id`, `quantity_sold`, `sale_price`) VALUES
(1, 1, 1, 1, 9.99),
(2, 1, 2, 1, 49.99),
(3, 2, 1, 1, 9.99),
(5, 3, 5, 1, 200.00),
(6, 4, 1, 10, 5.00),
(7, 5, 2, 3, 29.99),
(8, 6, 2, 1, 25.00),
(9, 7, 3, 10, 7.50),
(10, 8, 6, 3, 66.00),
(11, 9, 1, 10, 9.99),
(12, 10, 3, 500, 15.00),
(13, 11, 8, 10, 2500.00),
(14, 12, 1, 2, 9.99),
(15, 12, 2, 3, 49.99),
(16, 12, 5, 1, 200.00),
(17, 12, 7, 2, 682.00),
(18, 12, 8, 1, 2500.00),
(19, 12, 9, 7, 3.99);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `orders`
--
ALTER TABLE `orders`
  ADD PRIMARY KEY (`order_id`);

--
-- Indexes for table `products`
--
ALTER TABLE `products`
  ADD PRIMARY KEY (`product_id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Indexes for table `sales`
--
ALTER TABLE `sales`
  ADD PRIMARY KEY (`sale_id`);

--
-- Indexes for table `sale_items`
--
ALTER TABLE `sale_items`
  ADD PRIMARY KEY (`item_id`),
  ADD KEY `sale_id` (`sale_id`),
  ADD KEY `product_id` (`product_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `orders`
--
ALTER TABLE `orders`
  MODIFY `order_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `products`
--
ALTER TABLE `products`
  MODIFY `product_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `sales`
--
ALTER TABLE `sales`
  MODIFY `sale_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT for table `sale_items`
--
ALTER TABLE `sale_items`
  MODIFY `item_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `sale_items`
--
ALTER TABLE `sale_items`
  ADD CONSTRAINT `sale_items_ibfk_1` FOREIGN KEY (`sale_id`) REFERENCES `sales` (`sale_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `sale_items_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`) ON DELETE RESTRICT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
