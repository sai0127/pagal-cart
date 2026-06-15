# Pagal Cart 🛒

A full-stack e-commerce web application built with Python Flask, PostgreSQL and vanilla JavaScript.

## 🔗 Live Demo
https://pagal-cart.onrender.com

## Features
- User authentication with OTP email verification
- JWT token based sessions
- Product listing with search
- Shopping cart with quantity management
- Wishlist
- Address page for orders
- Order history dashboard
- Admin panel with product management
- Database viewer in admin panel
- Responsive design
- PostgreSQL database

## Technologies Used
- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python Flask
- **Database:** PostgreSQL
- **Authentication:** JWT, bcrypt, OTP via Resend
- **Deployment:** Render

## How to Run
1. Clone the repository
2. Install dependencies:
   pip install -r requirements.txt
3. Set environment variables:
   - DATABASE_URL
   - JWT_SECRET_KEY
   - RESEND_API_KEY
4. Run the backend:
   python ecommerce.py
5. Open browser at http://127.0.0.1:5000

## Pages
- `/` - Landing page
- `/shop` - Products page
- `/cart` - Shopping cart
- `/dashboard` - User dashboard
- `/wishlist` - Wishlist
- `/admin` - Admin panel (admin only)
- `/admin-login` - Admin login