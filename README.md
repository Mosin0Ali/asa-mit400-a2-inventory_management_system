# asa-mit400-a2-inventory_management_system
Inventory Management System — A simple system for small businesses to manage products, sales, and orders. Features include adding new products, updating stock after sales/returns, generating sales reports, and visualizing top-selling products and stock levels through an interactive GUI dashboard.


🧠 Flask Inventory Management System (Raw SQL Version)

A Flask-based Inventory Management System using MySQL. It allows you to manage products, create orders, handle sales returns, and view weekly sales graphs. Built with Flask, Bootstrap 5, and Chart.js.

🚀 Features

Add, edit, and delete products

Create orders with inventory checks

Process product returns and update stock

POS-style dashboard with weekly sales chart

View sales history: who bought which products

Dark mode UI with Bootstrap 5

🛠️ Prerequisites

Python 3.10+

MySQL 5.7+ / 8.0+

Git (optional)

💾 Database Setup

Create a MySQL database:

CREATE DATABASE inventory_db;


Use the database:

USE inventory_db;


Create tables:

CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    stock_quantity INT NOT NULL DEFAULT 0,
    unit_price DECIMAL(10,2) NOT NULL,
    cost_price DECIMAL(10,2) NOT NULL,
    reorder_point INT NOT NULL DEFAULT 10,
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sales (
    sale_id INT AUTO_INCREMENT PRIMARY KEY,
    sale_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    customer_name VARCHAR(255),
    total_amount DECIMAL(10,2) NOT NULL
);

CREATE TABLE sale_items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    sale_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity_sold INT NOT NULL,
    sale_price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (sale_id) REFERENCES sales(sale_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE RESTRICT
);

CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    order_date DATE NOT NULL,
    supplier_name VARCHAR(255) NOT NULL,
    expected_delivery_date DATE,
    status ENUM('Pending','Shipped','Received','Cancelled') NOT NULL DEFAULT 'Pending',
    total_cost DECIMAL(10,2),
    notes TEXT
);

🚀 Setup Instructions

Open your terminal and navigate to the project folder:

cd path/to/your/project


Create a virtual environment:

python3 -m venv myvenv


You can name it anything, e.g., sanojvenv.

Activate the virtual environment:

macOS / Linux:

source myvenv/bin/activate


Windows:

myvenv\Scripts\activate


Install dependencies:

pip install -r requirements.txt


Example requirements.txt:

blinker==1.9.0
cffi==2.0.0
click==8.3.0
cryptography==46.0.3
Flask==3.1.2
Flask-SQLAlchemy==3.1.1
itsdangerous==2.2.0
Jinja2==3.1.6
MarkupSafe==3.0.3
PyMySQL==1.1.2
SQLAlchemy==2.0.44
typing_extensions==4.15.0
Werkzeug==3.1.3


Run the Flask application:

python app.py


You should see:

Serving Flask app 'app_rawsql'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit


Open your browser: http://127.0.0.1:5000

🧩 Usage Notes

Ensure MySQL is running and connection details in app.py are correct.

Use this setup for development only.

Stop Flask server: CTRL + C

Deactivate virtual environment: deactivate

📂 Example File Structure
project/
│
├── app.py
├── requirements.txt
├── templates/
│   ├── dashboard.html
│   ├── products.html
│   ├── create_order.html
│   ├── return_order.html
│   └── ...
├── static/
│   └── css, js, images
└── README.md
