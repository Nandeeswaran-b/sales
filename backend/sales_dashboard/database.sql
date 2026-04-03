CREATE DATABASE IF NOT EXISTS sales_db;
USE sales_db;

CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    country VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS sales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT,
    customer_id INT,
    quantity INT,
    sale_date DATE,
    total_price DECIMAL(10,2),
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- Insert sample records for products
INSERT INTO products (name, category, price) VALUES
('MacBook Pro M2', 'Electronics', 1499.99),
('Dell XPS 13', 'Electronics', 1199.99),
('Sony Wireless Headphones', 'Audio', 349.99),
('Keychron K2 Keyboard', 'Accessories', 89.99),
('Logitech MX Master 3', 'Accessories', 99.99),
('Herman Miller Embody', 'Furniture', 1599.99),
('Samsung 32" Monitor', 'Electronics', 399.99),
('Jabra Elite Earbuds', 'Audio', 149.99);

-- Insert sample records for customers
INSERT INTO customers (name, email, country) VALUES
('Alice Smith', 'alice@example.com', 'USA'),
('Bob Johnson', 'bob@example.com', 'Canada'),
('Charlie Brown', 'charlie@example.com', 'UK'),
('Diana Prince', 'diana@example.com', 'USA'),
('Evan Wright', 'evan@example.com', 'Australia');

-- Insert 20+ sample records for sales spanning different months
INSERT INTO sales (product_id, customer_id, quantity, sale_date, total_price) VALUES
(1, 1, 1, '2023-01-15', 1499.99),
(3, 2, 2, '2023-01-20', 699.98),
(4, 3, 1, '2023-02-10', 89.99),
(6, 4, 1, '2023-02-14', 1599.99),
(5, 5, 2, '2023-03-05', 199.98),
(2, 2, 1, '2023-03-12', 1199.99),
(8, 1, 1, '2023-04-01', 149.99),
(5, 3, 3, '2023-04-18', 299.97),
(7, 5, 2, '2023-05-22', 799.98),
(3, 4, 2, '2023-05-30', 699.98),
(4, 1, 1, '2023-06-15', 89.99),
(1, 5, 1, '2023-06-25', 1499.99),
(8, 2, 2, '2023-07-04', 299.98),
(4, 4, 1, '2023-07-15', 89.99),
(3, 2, 2, '2023-08-08', 699.98),
(5, 1, 4, '2023-08-20', 399.96),
(6, 3, 1, '2023-09-12', 1599.99),
(2, 4, 1, '2023-10-05', 1199.99),
(7, 5, 1, '2023-11-11', 399.99),
(8, 3, 1, '2023-12-01', 149.99),
(4, 5, 1, '2023-12-15', 89.99),
(1, 1, 2, '2024-01-10', 2999.98);
