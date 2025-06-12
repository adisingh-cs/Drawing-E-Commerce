# 🖼️ Drawing Store

A **Django-based e-commerce platform** for showcasing and selling drawings. It features a sleek, responsive design, a streamlined checkout process, and a modern admin dashboard to manage products and track orders efficiently.

---

## 🚀 Features

* 🔍 Browse and view high-quality drawings
* 🛒 Add drawings to a cart and complete orders with ease
* 📬 Email notifications for new orders
* 📊 Admin dashboard with key performance metrics
* 📱 Fully responsive UI using **Bootstrap** and **FontAwesome**
* 🛠️ Built with **Django 5.0+**, powered by a clean and maintainable codebase

---

## 🧰 Prerequisites

* Python 3.8 or higher
* Django 5.0 or higher
* Pillow (for image processing)

---

## 📦 Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd drawing-store
   ```

2. **Install dependencies**

   ```bash
   pip install django pillow
   ```

3. **Configure email settings**
   Edit `drawing_store/settings.py` and update the following:

   ```python
   EMAIL_HOST_USER = 'your-email@gmail.com'
   EMAIL_HOST_PASSWORD = 'your-app-password'
   DEFAULT_FROM_EMAIL = 'your-email@gmail.com'
   ADMIN_EMAIL = 'your-email@gmail.com'
   ```

   ⚠️ *Use a [Gmail App Password](https://support.google.com/accounts/answer/185833) instead of your regular password for secure authentication.*

4. **Apply migrations**

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a superuser**

   ```bash
   python manage.py createsuperuser
   ```

---

## ▶️ Running the Application

1. **Start the development server**

   ```bash
   python manage.py runserver
   ```

2. **Access the application:**

   * 🌐 Main site: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
   * 📈 Admin dashboard: [http://127.0.0.1:8000/admin-dashboard/](http://127.0.0.1:8000/admin-dashboard/)
   * ⚙️ Django admin: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 🗂️ Project Structure

```
drawing-store/
├── store/                     # Main application
│   ├── models.py              # Product and Order models
│   ├── views.py               # View logic for user and admin interactions
│   ├── urls.py                # App-specific URL routing
│   ├── templates/             # HTML templates
│   └── templatetags/          # Custom template filters
│
├── drawing_store/            # Project settings
│   ├── settings.py            # Global configuration
│   └── urls.py                # Root URL configuration
│
├── media/                    # Uploaded images
├── static/                   # Static assets (CSS, JS, images)
```

---

## 📮 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you’d like to add.

