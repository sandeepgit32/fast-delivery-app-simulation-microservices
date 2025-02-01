CREATE DATABASE IF NOT EXISTS food_delivery;

USE food_delivery;

-- Create stock table first (no dependencies)
CREATE TABLE IF NOT EXISTS stock (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    item_name VARCHAR(255) NOT NULL,
    quantity INT NOT NULL
);

-- Create delivery_persons table (no dependencies)
CREATE TABLE IF NOT EXISTS delivery_persons (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    phone_number VARCHAR(50) NOT NULL,
    person_status VARCHAR(20) NOT NULL
);

-- Create orders table (no dependencies)
CREATE TABLE IF NOT EXISTS orders (
    id VARCHAR(50) PRIMARY KEY,
    order_time DATETIME NOT NULL,
    customer_name VARCHAR(255) NOT NULL,
    customer_distance VARCHAR(255) NOT NULL,
    order_status VARCHAR(50) NOT NULL
);

-- Create order_items table (depends on orders and stock)
CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT,
    order_id VARCHAR(50),
    item_id INT NOT NULL,
    quantity INT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (item_id) REFERENCES stock(item_id)
);

-- Create deliveries table (depends on orders and delivery_persons)
CREATE TABLE IF NOT EXISTS deliveries (
    id INT AUTO_INCREMENT,
    order_id VARCHAR(50),
    delivery_person_id INT NOT NULL,
    delivery_status VARCHAR(20) NOT NULL,
    created_at DATETIME NOT NULL,
    delivered_at DATETIME,
    PRIMARY KEY (id),
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (delivery_person_id) REFERENCES delivery_persons(id)
);

-- Insert sample data into stock table 
INSERT INTO stock (item_name, quantity) VALUES
('Product 1', 100),
('Product 2', 150),
('Product 3', 200),
('Product 4', 300),
('Product 5', 250),
('Product 6', 175),
('Product 7', 125),
('Product 8', 400),
('Product 9', 225),
('Product 10', 350);

-- Insert sample data into delivery_persons table
INSERT INTO delivery_persons (name, phone_number, person_status) VALUES
('John Doe', '1234567890', 'idle'),
('Jane Doe', '0987654321', 'idle'),
('Alice Smith', '1231231234', 'idle'),
('Bob Wilson', '4564564567', 'idle'),
('Charlie Brown', '7897897890', 'idle'),
('David Johnson', '1112223333', 'idle'),
('Eva Martinez', '4445556666', 'idle'),
('Frank Thomas', '7778889999', 'idle'),
('Grace Lee', '3334445555', 'idle'),
('Henry Garcia', '6667778888', 'idle');