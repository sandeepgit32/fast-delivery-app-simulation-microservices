CREATE DATABASE IF NOT EXISTS food_delivery;

USE food_delivery;

CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_time DATETIME NOT NULL,
    customer_name VARCHAR(255) NOT NULL,
    customer_distance VARCHAR(255) NOT NULL,
    order_status VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    item_id INT NOT NULL,
    quantity INT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (item_id) REFERENCES stock(item_id)
);

CREATE TABLE IF NOT EXISTS deliveries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    delivery_person_id INT NOT NULL,
    delivery_status VARCHAR(20) NOT NULL,
    created_at DATETIME NOT NULL,
    delivered_at DATETIME,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (delivery_person_id) REFERENCES delivery_persons(id)
);

CREATE TABLE IF NOT EXISTS stock (
    item_id VARCHAR(50) PRIMARY KEY,
    item_name VARCHAR(255) NOT NULL,
    quantity INT NOT NULL
);

CREATE TABLE IF NOT EXISTS delivery_persons (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    phone_number VARCHAR(50) NOT NULL,
    person_status VARCHAR(20) NOT NULL
);