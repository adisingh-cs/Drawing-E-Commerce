# Drawing Store

A Django-based e-commerce website for selling drawings, featuring a modern admin dashboard and a simple checkout process.

## Features

- Browse and view drawings
- Add drawings to cart
- Simple checkout process
- Admin dashboard with key metrics
- Email notifications for new orders
- Modern, responsive design using Bootstrap and FontAwesome

## Prerequisites

- Python 3.8 or higher
- Django 5.0 or higher
- Pillow (for image handling)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd drawing-store
```

2. Install the required packages:
```bash
pip install django pillow
```

3. Configure email settings:
   - Open `drawing_store/settings.py`
   - Update the email configuration with your Gmail credentials:
     ```python
     EMAIL_HOST_USER = 'your-email@gmail.com'
     EMAIL_HOST_PASSWORD = 'your-app-password'
     DEFAULT_FROM_EMAIL = 'your-email@gmail.com'
     ADMIN_EMAIL = 'your-email@gmail.com'
     ```
   - Note: For Gmail, you'll need to use an App Password. You can generate one in your Google Account settings.

4. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create a superuser for admin access:
```bash
python manage.py createsuperuser
```

## Running the Application

1. Start the development server:
```bash
python manage.py runserver
```

2. Open your browser and navigate to:
   - Main site: http://127.0.0.1:8000/
   - Admin dashboard: http://127.0.0.1:8000/admin-dashboard/
   - Django admin: http://127.0.0.1:8000/admin/

## Project Structure

- `store/` - Main application directory
  - `models.py` - Database models for Product and Order
  - `views.py` - View functions for handling requests
  - `urls.py` - URL routing configuration
  - `templates/` - HTML templates
  - `templatetags/` - Custom template filters
- `drawing_store/` - Project settings directory
  - `settings.py` - Project settings
  - `urls.py` - Main URL configuration
- `media/` - Directory for uploaded images
- `static/` - Directory for static files

