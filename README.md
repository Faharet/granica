# Form Management System Demo

A simple Django-based form management system with manager and submitter roles. Built with Django and django-daisy for a clean, modern interface.

## Features

- **Role-based Access Control**: Two user types:
  - Managers: Can view and manage all form submissions
  - Submitters: Can submit new forms
- **Clean Interface**: Built with django-daisy UI components
- **Secure**: Proper authentication and authorization
- **Mobile-friendly**: Responsive design

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/yourusername/deli-bike-admin.git
cd deli-bike-admin
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your settings
```

5. Initialize the database:
```bash
python manage.py migrate
```

6. Create demo users and sample data:
```bash
python manage.py setup_demo
```

7. Run the development server:
```bash
python manage.py runserver
```

8. Visit http://127.0.0.1:8000/ and log in with demo credentials:

## Demo Credentials

- Admin User:
  - Username: admin
  - Password: admin

- Manager User:
  - Username: manager
  - Password: manager

- Submitter User:
  - Username: submitter
  - Password: submitter

## Project Structure

- `platform_manager/`: Main application
  - `models.py`: Form response model
  - `views.py`: Form submission and management views
  - `admin.py`: Admin interface customization

## Development

1. Make sure you have Python 3.8+ installed
2. Install development dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

All configuration is done through environment variables. See `.env.example` for available options.

## License

This project is open-source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.