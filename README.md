# AI-Enhanced e-Commerce Platform 🚀
### A Complete, Intelligent, Production-Ready E-Commerce Web Application
**Built with FastAPI, MySQL (SQLAlchemy), Scikit-Learn (KNN Recommender), and Google Gemini Generative AI**

---

## 🌟 Project Overview
The **AI-Enhanced e-Commerce Platform** (NexCommerce) is a full-stack, enterprise-grade e-commerce application developed for academic project demonstration and real-world online retailing. It bridges standard e-commerce operations (product browsing, search & filtering, persistent shopping cart, checkout, and order lifecycle tracking) with:

1. **Machine Learning Recommendation Engine**: A true K-Nearest Neighbors (KNN) model trained on actual user interactions (views, searches, cart additions, purchases, and ratings) calculating cosine distance on user preference and product feature spaces.
2. **Generative AI Studio (Google Gemini API)**: Integrated AI assistance for merchants to automatically generate compelling product descriptions, bullet-point highlights, and technical specifications, as well as dynamic real-time shopping advice for consumers.
3. **Role-Based Access Control (RBAC)**: Secure multi-portal system supporting **Customers**, **Sellers**, and **Platform Administrators**.

---

## 🛠️ Technology Stack

| Layer | Technologies Used |
| :--- | :--- |
| **Frontend** | HTML5, Modern Responsive CSS3 (Flexbox, CSS Grid, Custom Keyframe Animations, Glassmorphism), Vanilla JavaScript ES6+ (Fetch API, JWT management, Toast notifications, Cart badge state) |
| **Backend** | Python 3.13+, FastAPI, Uvicorn, RESTful architecture, Pydantic V2 data validation & serialization |
| **Database & ORM** | MySQL 8.0, SQLAlchemy 2.0 ORM, PyMySQL driver, Connection pool with pre-ping validation |
| **Machine Learning** | Scikit-learn (`NearestNeighbors`), Pandas, NumPy, Joblib model serialization |
| **Generative AI** | Google Gemini API (`gemini-1.5-flash`), `google-generativeai` SDK |
| **Authentication** | JSON Web Tokens (PyJWT), Salted Bcrypt password hashing (`bcrypt`) |

---

## 📁 Folder Structure

```
AI-Enhanced-Ecommerce-Platform/
├── Frontend/                           # Complete Animated Frontend Interface
│   ├── index.html                      # Home Page with Hero, Categories, Trending & AI Picks
│   ├── login.html                      # Sign In Page with Demo Credential Quick Fill
│   ├── register.html                   # Customer & Seller Merchant Registration
│   ├── products.html                   # Catalog Listing with Live Search, Price & Rating Filters
│   ├── product-details.html            # Detail Page with Specs, Reviews & Gemini Insight
│   ├── cart.html                       # Shopping Cart Management & Quantity Steppers
│   ├── checkout.html                   # Shipping & Payment Selection (Cash on Delivery / Demo)
│   ├── order-confirmation.html         # Post-Checkout Receipt & Status Overview
│   ├── orders.html                     # Customer Order History & Tracking
│   ├── profile.html                    # Customer Profile Details & Password Update
│   ├── seller/                         # Seller Merchant Portal
│   │   ├── dashboard.html              # Revenue, Orders, Products, and Low Stock Alerts
│   │   ├── add-product.html            # Product Creation with Live Gemini AI Studio
│   │   ├── edit-product.html           # Product Editing & Catalog Update
│   │   └── orders.html                 # Seller Order Fulfillment & Status Updates
│   ├── admin/                          # Platform Administrator Console
│   │   ├── dashboard.html              # Platform-wide Analytics, Revenue & Recent Activity
│   │   ├── customers.html              # Customer User Management & Account Deactivation
│   │   ├── sellers.html                # Seller Directory & Approval Status
│   │   ├── products.html               # Global Product Catalog & Inventory Toggle
│   │   └── orders.html                 # Global Orders Fulfillment Status Manager
│   ├── css/                            # Modular Design System Stylesheets
│   │   ├── style.css                   # Core Variables, Layout, Cards, Navbar & Footer
│   │   ├── animations.css              # Custom Keyframes (Fade-In, Shimmer, Pulse, Float)
│   │   └── dashboard.css               # Sidebar, Metric Stat Cards & Clean Data Tables
│   ├── js/                             # Modular JavaScript Client
│   │   ├── api.js                      # Unified REST Client, Auth Headers & Toast System
│   │   ├── auth.js                     # RBAC Guards, Navbar Auth State & Demo Login
│   │   ├── cart.js                     # Cart Operations & Navbar Count Badge
│   │   └── main.js                     # Homepage Carousels & Dynamic Recommendations
│   └── assets/images/                  # Static image assets and placeholders
├── Backend/                            # FastAPI Backend API Server
│   ├── app/
│   │   ├── main.py                     # Primary FastAPI App & Static Frontend Mount
│   │   ├── database.py                 # SQLAlchemy Engine & SessionLocal Dependency
│   │   ├── init_db.py                  # Table Creation & Comprehensive Demo Data Seeder
│   │   ├── core/                       # Configuration & JWT Security
│   │   │   ├── config.py               # Pydantic Settings & Environment Loader
│   │   │   ├── security.py             # Bcrypt Hashing & JWT Token Generation
│   │   │   └── dependencies.py         # Role-based Route Protection Dependencies
│   │   ├── models/                     # 10 SQLAlchemy ORM Relational Models
│   │   │   ├── user.py                 # Customer, Seller, and Admin Accounts
│   │   │   ├── seller.py               # Merchant Store Metadata
│   │   │   ├── category.py             # Product Categories Taxonomy
│   │   │   ├── product.py              # Products with Price, Stock, AI Descriptions
│   │   │   ├── cart.py                 # Cart & CartItems
│   │   │   ├── order.py                # Order & OrderItems
│   │   │   ├── review.py               # Customer Product Reviews & Ratings
│   │   │   └── interaction.py          # User Browsing, Search, Cart & Purchase Actions
│   │   ├── schemas/                    # Pydantic Request & Response Data Models
│   │   ├── routers/                    # REST API Endpoints
│   │   │   ├── auth.py                 # /api/auth (Register, Login, Me, Profile)
│   │   │   ├── products.py             # /api/products & /api/categories
│   │   │   ├── cart.py                 # /api/cart (Get, Add, Update, Remove, Clear)
│   │   │   ├── orders.py               # /api/orders (Place Order, History, Details)
│   │   │   ├── recommendations.py      # /api/recommendations (Personalized, Similar)
│   │   │   ├── ai.py                   # /api/ai (Descriptions, Highlights, Insights)
│   │   │   ├── seller.py               # /api/seller (Dashboard, Products, Orders)
│   │   │   └── admin.py                # /api/admin (Dashboard, Users, Products, Orders)
│   │   ├── ml/                         # Machine Learning Integration
│   │   │   └── recommender.py          # Real-time KNN Inference & Cold-Start Strategy
│   │   └── ai/                         # Generative AI Integration
│   │       └── gemini_service.py       # Google Gemini 1.5 Flash Client & Prompt Studio
│   ├── setup_db.py                     # Convenience One-Step Database Setup Script
│   ├── test_db_connection.py           # Database Connection Diagnostic Tool
│   ├── run.py                          # Server Launch Runner Script
│   ├── requirements.txt                # Python Dependencies
│   ├── .env.example                    # Environment Variables Template
│   └── .env                            # Active Environment Configuration
├── ML/                                 # Machine Learning Module
│   ├── dataset/                        # Datasets for Preprocessing & Training
│   │   ├── products.csv                # 20 Products Catalog with Multi-Attribute Specs
│   │   └── user_interactions.csv       # 160 Real User Interaction Records across 25 Users
│   ├── notebooks/                      # Academic Demonstration Notebook
│   │   └── knn_recommendation_system.ipynb # End-to-end Data Prep, Training & Evaluation
│   ├── models/                         # Serialized Model Artifacts
│   │   └── knn_recommender.joblib      # Pre-trained KNN Model Bundle
│   └── src/                            # Standalone Python Training & Evaluation Scripts
│       ├── preprocess.py               # Matrix Builders & Feature Encoders
│       ├── train.py                    # Scikit-learn NearestNeighbors Model Trainer
│       ├── evaluate.py                 # Precision@K, Recall@K & Catalog Coverage Evaluator
│       └── generate_dataset.py         # Multi-Persona User Interaction Synthesizer
├── Documentation/                      # Academic Project Deliverables
│   ├── Project_Documentation.md        # Complete Markdown Technical Report
│   ├── Project_Documentation.pdf       # Compiled Multi-Page Academic PDF Deliverable
│   └── generate_pdf.py                 # PDF Generator Script
├── .gitignore                          # Clean Repository Exclusions
└── README.md                           # Comprehensive Documentation Guide
```

---

## ⚙️ Prerequisites

1. **Python 3.10+** (Tested on Python 3.13)
2. **MySQL Server 8.0+** running locally on port `3306`
3. A Web Browser (Chrome, Edge, Firefox, Safari)
4. (Optional) A **Google Gemini API Key** (from [Google AI Studio](https://aistudio.google.com/))

---

## 🔑 Environment Variables Configuration (`.env`)

In the `Backend/` directory, open the `.env` file and enter your MySQL root password:

```ini
# Database Configuration (MySQL)
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_root_password_here   <--- [ENTER YOUR MYSQL ROOT PASSWORD HERE]
DB_NAME=ai_ecommerce_db

# Security & JWT Configuration
SECRET_KEY=super_secret_jwt_key_ai_ecommerce_platform_academic_project_2026
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Google Gemini API Configuration (Optional: Add for live Gemini generation)
GEMINI_API_KEY=your_gemini_api_key_here

# Application Configuration
APP_NAME=AI-Enhanced E-Commerce Platform
DEBUG=True
API_PREFIX=/api
```

> **Note**: Your database `ai_ecommerce_db` must exist in MySQL. If not already created, run:
> ```sql
> CREATE DATABASE IF NOT EXISTS ai_ecommerce_db;
> ```

---

## 🚀 Quick Setup & Execution Guide

### Step 1: Install Python Dependencies
Open PowerShell or your terminal in the project directory:
```bash
pip install -r Backend/requirements.txt
```

### Step 2: Test Database Connection & Seed Data
Run the database diagnostic and seeder tool:
```bash
# 1. Test your MySQL connection
python Backend/test_db_connection.py

# 2. Automatically create all 10 tables and seed realistic initial data
python Backend/setup_db.py
```

### Step 3: Train or Re-Train the Machine Learning KNN Model
The repository already includes a pre-trained model in `ML/models/knn_recommender.joblib`. You can evaluate or re-train it anytime:
```bash
# Train KNN models and save artifact bundle:
python ML/src/train.py

# Run academic evaluation (Precision@K, Recall@K, Coverage):
python ML/src/evaluate.py
```

### Step 4: Run the Application Server
Start the unified FastAPI backend server:
```bash
python Backend/run.py
```
Or with uvicorn directly:
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 --app-dir Backend
```

### Step 5: Open the Application in Your Browser
- **Storefront & Customer Portal**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive API Swagger Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Alternative ReDoc API Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 👥 Sample Login Credentials for Testing

Use the quick demo buttons on the **Sign In** page (`/login.html`) or enter:

| Role | Email | Password | Access Rights & Portals |
| :--- | :--- | :--- | :--- |
| **Customer** | `john@example.com` | `Customer123!` | Browse, Cart, Checkout, Reviews, Personalized KNN Recommendations |
| **Seller** | `seller@techhub.com` | `SellerPassword123!` | Seller Dashboard, Add/Edit Products with Gemini AI, Manage Orders |
| **Seller 2** | `seller@stylezone.com` | `SellerPassword123!` | Seller Dashboard for StyleZone Lifestyle Fashion Store |
| **Admin** | `admin@ecommerce.com` | `AdminPassword123!` | Global Analytics, User Control, Product Activation, Order Fulfillment |

---

## 📊 Machine Learning Model Details

- **Algorithm**: K-Nearest Neighbors (`sklearn.neighbors.NearestNeighbors`)
- **Metric**: Cosine Distance ($1 - \cos(\mathbf{u}, \mathbf{v})$)
- **Item-KNN**: Computes product-to-product feature similarity across normalized price, ratings, log-popularity, and one-hot encoded categories.
- **User-KNN**: Computes collaborative user preference similarity across interaction vectors (views, searches, cart items, purchases).
- **Cold-Start Strategy**: For new visitors without interaction history, automatically defaults to rating-weighted popularity and category bestsellers.
- **Evaluation Metrics**:
  - **Recall@10**: 92.0%
  - **Hit Rate@10**: 92.0%
  - **Catalog Coverage**: 90.0%

---

## 🤖 Google Gemini Generative AI Integration

- **Model**: `gemini-1.5-flash`
- **Features**:
  - **Product Description Generator**: Input product name, category, price, and specs -> outputs professional marketing copy, bullet highlights, and target use cases.
  - **Highlight Generator**: Creates bulleted key selling features.
  - **Shopping Insights**: Real-time shopping concierge on the home page advising shoppers on product choices.
  - **Product Explanation**: Explains why a specific item is an optimal purchase based on verified customer feedback.
- **Safety & Error Handling**: Graceful fallback to rich curated data when API key is missing or quota is exceeded.

---

## 📄 Academic Deliverables

- **Jupyter Notebook**: Located at `ML/notebooks/knn_recommendation_system.ipynb` with complete markdown explanations, data loading, EDA, matrix building, training, evaluation, and recommendation testing.
- **Project Documentation PDF**: Located at `Documentation/Project_Documentation.pdf` (generated via PyMuPDF).
- **Project Documentation Markdown**: Located at `Documentation/Project_Documentation.md`.

---

## 🛡️ License & Academic Notice
This project is developed for educational and academic project presentation purposes. All rights reserved &copy; 2026.

