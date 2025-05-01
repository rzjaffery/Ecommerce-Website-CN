# Online Shopping System

A full-featured e-commerce website built with Django, MySQL, and responsive frontend design.

## Features

- **User Authentication**
  - User registration and login
  - Profile management with address and contact information
  - Role-based access (customer, admin, customer support)

- **Product Management**
  - Product listings with images, descriptions, and prices
  - Categories and search functionality
  - Product detail views with related products

- **Shopping Cart & Checkout**
  - Add/remove items from cart
  - Update quantities
  - Checkout process with shipping/billing info
  - Order confirmation and history

- **Live Chat Support System**
  - Real-time customer support via WebSockets
  - Secure authentication with JWT tokens
  - Message history and notifications
  - Support staff dashboard for managing multiple chats
  - SSL/TLS encryption for secure communication

## Tech Stack

- **Frontend**: HTML, CSS (Bootstrap 5), JavaScript
- **Backend**: Django (Python)
- **Database**: MySQL
- **WebSockets**: Django Channels with Redis
- **Authentication**: JWT tokens for secure WebSocket connections

## Setup Instructions

### Prerequisites

- Python 3.x
- MySQL Server
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/ecommerce.git
   cd ecommerce
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Configure MySQL:
   - Create a MySQL database named `ecommerce_db`
   - Update the database settings in `ecommerce/settings.py` if needed

5. Apply migrations:
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```

6. Create superuser (admin):
   ```
   python manage.py createsuperuser
   ```

7. Start the development server:
   ```
   python manage.py runserver
   ```

8. Visit `http://127.0.0.1:8000` in your browser to see the application

## Setting Up Redis for WebSockets

The chat functionality requires Redis as a channel layer for Django Channels:

1. Install Redis:
   - **Windows**: Install through WSL or use [Redis for Windows](https://github.com/microsoftarchive/redis/releases)
   - **macOS**: `brew install redis`
   - **Linux**: `sudo apt install redis-server`

2. Start Redis server:
   - **Windows**: Start the Redis service
   - **macOS/Linux**: `redis-server`

## Secure WebSockets with SSL/TLS

For secure WebSocket connections (wss://), you need SSL certificates:

1. Generate self-signed certificates for local development:
   ```
   python generate_ssl_cert.py
   ```

2. Run the server with SSL support:
   ```
   daphne -e ssl:8000:privateKey=ssl/localhost.key:certKey=ssl/localhost.crt ecommerce.asgi:application
   ```

3. Visit `https://localhost:8000` in your browser

Note: For production, use proper SSL certificates from a certificate authority.

## Testing the Chat System

1. Log in as an admin user to act as support staff
2. Grant support staff status to the admin user through the Django admin panel
3. Open another browser (or incognito window) and log in as a regular user
4. Click the chat button in the bottom right corner to start a conversation
5. Switch to the admin browser to respond to the chat request

## Admin Access

To access the admin panel:
1. Go to `http://127.0.0.1:8000/admin`
2. Log in with the superuser credentials you created

## Project Structure

- `users` - User authentication and profile management
- `products` - Product catalog and listings
- `cart` - Shopping cart and checkout functionality
- `chat` - Real-time customer support system
- `templates` - HTML templates
- `static` - CSS, JavaScript and image files
- `media` - User-uploaded media files (product images, etc.)

## License

This project is licensed under the MIT License - see the LICENSE file for details. 