# 📦 StockMate - Django Inventory Management System

A comprehensive, full-stack inventory management system built with Django, featuring machine learning-powered product categorization, supplier management, and real-time stock tracking.


---

## 🌟 Features

### Core Functionality

- **Inventory Management**: Complete CRUD operations for stock items
- **Supplier Management**: Track suppliers and brands with relationship management
- **Stock Transactions**: Receive and issue items with automatic quantity updates
- **Transaction History**: Comprehensive audit trail of all inventory movements
- **Low Stock Alerts**: Visual indicators for items below reorder levels
- **Search & Filtering**: Advanced search with date range filtering and pagination

### Advanced Features

- **🤖 ML-Powered Categorization**: Automatic product categorization using FastAI computer vision
- **📊 Real-time Analytics**: Dashboard with inventory statistics
- **🖼️ Image Management**: Product image upload and display
- **👥 User Authentication**: Secure login/logout with Django's auth system
- **📱 Responsive Design**: Bootstrap 5 for mobile-friendly interface
- **🔍 Advanced Search**: Multi-criteria search with date filtering

---

## 🛠️ Tech Stack

### Backend

- **Framework**: Django 4.x
- **Database**: MySQL / SQLite
- **ORM**: Django ORM
- **ML Framework**: FastAI
- **Image Processing**: Pillow (PIL)

### Frontend

- **Framework**: Bootstrap 5
- **Icons**: Font Awesome
- **Forms**: Django Crispy Forms
- **JavaScript**: Vanilla JS for dynamic interactions

### Additional Libraries

- `django-crispy-forms` - Enhanced form rendering

---

## 📋 Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- MySQL Server (optional, SQLite works too)
- Git

---

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/STEALTH-GOD/django-Inv_Management_App.git
cd "Inv Management"
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Configuration

#### Option A: MySQL (Recommended for Production)

1. Create a MySQL database:

```sql
CREATE DATABASE invmanagement;
```

2. Update `djangoproject/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'invmanagement',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

#### Option B: SQLite (Default for Development)

SQLite is configured by default. No additional setup required.

### 5. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### 7. Collect Static Files

```bash
python manage.py collectstatic
```

### 8. Run Development Server

```bash
python manage.py runserver
```

Access the application at: **http://127.0.0.1:8000/**

---

## 📁 Project Structure

```
Inv Management/
├── djangoproject/          # Main project settings
│   ├── settings.py        # Project configuration
│   ├── urls.py           # Root URL routing
│   └── wsgi.py           # WSGI configuration
│
├── inventorymgmt/         # Core inventory app
│   ├── models.py         # Stock and StockHistory models
│   ├── views.py          # Business logic
│   ├── forms.py          # Form definitions
│   ├── urls.py           # App URL routing
│   └── admin.py          # Admin interface config
│
├── suppliers/             # Supplier management app
│   ├── models.py         # Supplier and Brand models
│   ├── views.py          # Supplier CRUD operations
│   ├── forms.py          # Supplier forms
│   └── urls.py           # Supplier URL routing
│
├── mlpredict/            # ML prediction app
│   ├── views.py          # Prediction API endpoints
│   ├── models/           # Pre-trained ML models
│   └── urls.py           # ML API routing
│
├── accounts/             # User authentication app
│   ├── views.py          # Login/logout logic
│   └── urls.py           # Auth URL routing
│
|
│
├── templates/            # HTML templates
│   ├── base/            # Base templates & navbar
│   ├── inventory/       # Inventory templates
│   ├── suppliers/       # Supplier templates
│   └── accounts/        # Auth templates
│
├── static/              # Static files
│   ├── css/            # Stylesheets
│   ├── img/            # Images
│   └── js/             # JavaScript files
│
├── media/               # User-uploaded files
│   ├── product_images/ # Product photos
│
├── db.sqlite3          # SQLite database
├── manage.py           # Django management script
└── requirements.txt    # Python dependencies
```

---

## 🎯 Usage Guide

### Adding Products

1. Navigate to **"Add Items"** from the navbar
2. Fill in product details (name, quantity, category, brand, price)
3. Upload product image (optional)
4. Select or create a supplier
5. Click **"Save"** - barcode is auto-generated

### Managing Inventory

- **View All Items**: Navigate to "List Items"
- **Search**: Use filters (name, brand, category, date)
- **Update Stock**: Click on item → "Receive" or "Issue"
- **View Details**: Click on any row to see full details
- **Delete Items**: Use delete button (with confirmation)

### Supplier Management

1. Navigate to **"List Suppliers"**
2. Click **"Add Supplier"**
3. Enter supplier details and brands (comma-separated)
4. View supplier details with associated brands

### ML Auto-Categorization

1. When adding an item, upload a product image
2. The system automatically predicts the category
3. Category field is auto-filled with confidence score
4. Manual override available if needed

---

## 🔐 Security Features

- **Authentication Required**: Login required for all inventory operations
- **CSRF Protection**: All forms include CSRF tokens
- **Input Validation**: Server-side form validation
- **SQL Injection Prevention**: Django ORM prevents SQL injection
- **File Upload Security**: Image validation and size limits
- **Password Hashing**: Django's built-in password hashing

---

## 📊 Database Models

### Stock Model

```python
- item_name: CharField
- quantity: IntegerField
- category: CharField
- brand: CharField
- price: CharField
- supplier: ForeignKey(Supplier)
- image: ImageField
- reorder_level: IntegerField
- created_at: DateTimeField
- last_updated: DateTimeField
```

### Supplier Model

```python
- name: CharField (unique)
- phone_number: CharField
- email: EmailField
- address: TextField
- brands: ManyToManyField(Brand)
- created_at: DateTimeField
```

### StockHistory Model

```python
- stock_id: IntegerField
- item_name: CharField
- quantity: IntegerField
- receive_quantity: IntegerField
- issue_quantity: IntegerField
- supplier: ForeignKey(Supplier)
- last_updated: DateTimeField
```

---

## 🤖 Machine Learning Integration

### Model Details

- **Framework**: FastAI (PyTorch-based)
- **Architecture**: ResNet34 (Transfer Learning)
- **Input**: 224x224 RGB images
- **Output**: Product category + confidence score

### Supported Categories

The `kitchen_classifier.pkl` model can detect:

- Cookware (pots, pans, skillets)
- Utensils (spatulas, ladles, whisks)
- Cutlery (knives, forks, spoons)
- Tableware (plates, bowls, mugs)

### API Endpoint

```
POST /mlpredict/predict/
Content-Type: multipart/form-data

Request:
- image: [Image file]

Response:
{
    "success": true,
    "category": "Kitchen Appliance",
    "confidence": 92.34,
    "all_predictions": [...]
}
```

---

## 🎨 UI/UX Features

- **Modern Design**: Clean, professional interface with custom color scheme (#078080)
- **Responsive Layout**: Works on desktop, tablet, and mobile
- **Visual Feedback**: Success/error messages for all actions
- **Hover Effects**: Interactive elements with smooth transitions
- **Pagination**: 10 items per page for better performance
- **Loading Indicators**: Shows loading state during operations
- **Modal Views**: Image preview in modals
- **Clickable Rows**: Click any row to view details

---

## 🧪 Testing

Run tests with:

```bash
python manage.py test
```

### Test Coverage

- Model tests (CRUD operations)
- View tests (URL routing, response codes)
- Form tests (validation, data processing)
- ML integration tests (prediction accuracy)

---

## 📈 Performance Optimizations

### Database

- **Query Optimization**: `select_related()` for ForeignKey queries
- **Indexing**: Database indexes on frequently searched fields
- **Pagination**: Limits query results to improve load times

### ML Model

- **Model Caching**: Models loaded once at startup (1000x faster)
- **Singleton Pattern**: Single model instance across requests
- **Response Time**: <300ms for predictions

### Frontend

- **Asset Optimization**: Minified CSS/JS
- **Lazy Loading**: Images loaded on demand
- **CDN**: Bootstrap and Font Awesome from CDN

---


---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---



---

## 👨‍💻 Author

**STEALTH-GOD**

- GitHub: [@STEALTH-GOD](https://github.com/STEALTH-GOD)
- Repository: [django](https://github.com/STEALTH-GOD/django-Inv_Management_App)

---

## 🙏 Acknowledgments

- Django Software Foundation
- FastAI community
- Bootstrap team
- Font Awesome
- All open-source contributors

---

## 🔮 Future Enhancements

- [ ] REST API with Django REST Framework
- [ ] Mobile app (React Native/Flutter)
- [ ] Advanced analytics dashboard
- [ ] Multi-location inventory tracking
- [ ] Purchase order automation
- [ ] Email notifications for low stock
- [ ] Barcode scanning via mobile app
- [ ] Export reports (PDF, Excel)
- [ ] Multi-language support

---

