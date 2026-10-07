# Simple E-commerce Product Management System

A clean and simple Product Management web application built with **Python**, **Django**, and **SQLite**, styled with **Bootstrap 5**.

---

## 📌 Project Overview
This project was developed for the Junior Python/Django Developer assessment. It allows administrators to log in and manage store products with full CRUD operations, live API integration with DummyJSON, responsive search and filters, stock tracking, and pagination.

---

## 🚀 Technologies Used
- **Backend**: Python 3.13, Django 5.1
- **Database**: SQLite3
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5 (via CDN), Bootstrap Icons
- **Data Source**: [DummyJSON Products API](https://dummyjson.com/products)
- **Version Control**: Git

---

## 🔑 Default Login Credentials
- **Username**: `admin`
- **Password**: `admin123`

*(These credentials are created automatically when running the seed command)*

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd "E-commerce Product Management"
```

### 2. Create and Activate Virtual Environment (Optional but Recommended)
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install django pillow
```

### 4. Apply Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Fetch Products from DummyJSON API & Create Admin
Run the built-in management command to automatically create the superuser (`admin`/`admin123`) and fetch live products from `https://dummyjson.com/products`:
```bash
python manage.py seed_data
```

---

## 💻 How to Run the Application

Start the Django local development server:
```bash
python manage.py runserver
```

Open your browser and navigate to:
```
http://127.0.0.1:8000/
```
You will be greeted with the Login page. Log in using `admin` / `admin123`.

---

## 🧪 Running Automated Tests
Run Django's built-in test suite:
```bash
python manage.py test
```
All 8 unit and integration tests will execute and verify authentication, CRUD operations, validations, and the DummyJSON integration.

---

## 📱 Pages & Features Implemented

1. **Login Page (`/login/`)**:
   - Secure login form with validation and error alerts.
   - Redirects to Dashboard upon successful login.
   - Logout functionality with confirmation message.

2. **Dashboard (`/dashboard/`)**:
   - Quick overview cards:
     - **Total Products**
     - **Active Products**
     - **Inactive Products**
     - **Low Stock Products** (stock ≤ 5)
   - Navigation links to Products, Add Product, and Logout.

3. **Product List Page (`/products/`)**:
   - Clean tabular display with thumbnails, categories, formatted prices, and stock counts.
   - Real-time search by product name.
   - Category and Active/Inactive status filtering.
   - **Low Stock** badge indicator when stock ≤ 5.
   - **Sync DummyJSON** button to fetch latest products directly from the API.
   - Modal detail popup on clicking **View**.
   - Safe delete confirmation modal before removing any product.
   - Basic pagination (10 items per page).

4. **Add / Edit Product Page (`/products/add/` & `/products/<id>/edit/`)**:
   - Reusable single form with clean validation:
     - Product Name (required)
     - SKU (required and unique)
     - Category (required)
     - Price (must be greater than 0)
     - Stock Quantity (cannot be negative)
     - Product Image & Description
     - Status (Active / Inactive)
   - Redirects directly back to Product List upon saving.
