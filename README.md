# Student Database Management System

A comprehensive student management system built with Python and Tkinter, featuring modern UI/UX design, advanced reporting capabilities, and integrated communication tools.

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Student-Database-System
   ```

2. **Install dependencies**
   ```bash
   pip install -r config/requirements.txt
   ```

3. **Run the application**
   ```bash
   python run.py
   ```

## 📁 Project Structure

```
Student-Database-System/
├── src/                          # Main source code
│   ├── main.py                   # Primary application entry point
│   ├── app/                      # Application modules
│   │   ├── gui/                  # GUI components
│   │   ├── db/                   # Database operations
│   │   └── utils/                # Utility functions
│   └── assets/                   # Static assets
│       ├── images/               # UI images and icons
│       └── profile_pictures/     # Student profile pictures
├── tests/                        # Test suite
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   └── data/                     # Test data and utilities
├── docs/                         # Documentation
│   ├── fixes/                    # Implementation and fix notes
│   └── user/                     # User documentation
├── scripts/                      # Utility scripts
│   ├── setup/                    # Setup and seeding scripts
│   └── maintenance/              # Maintenance utilities
├── data/                         # Database files
├── config/                       # Configuration files
├── run.py                        # Main application entry point
└── README.md                     # This file
```

## ✨ Features

### Core Functionality
- **Student Management**: Complete CRUD operations for student records
- **Course Management**: Manage courses, academic years, and faculties
- **Marks Management**: Track and manage student grades
- **Payment Tracking**: Record and manage fee payments
- **ID Card Generation**: Generate student ID cards with profile pictures

### Advanced Features
- **Professional Dashboard**: Live statistics and analytics
- **Advanced Reporting**: PDF and CSV export capabilities
- **Email Integration**: Share reports and documents via email
- **Visual Analytics**: Interactive charts and graphs
- **Communication Hub**: Integrated feedback and announcement system
- **Modern UI/UX**: Built with ttkbootstrap for a modern look

### Profile Picture Support
- Upload and manage student profile pictures
- Automatic resizing and optimization
- Integration with ID card generation
- Support for multiple image formats (PNG, JPG, JPEG, GIF, BMP)

## 🛠️ Development

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test category
python -m pytest tests/unit/
python -m pytest tests/integration/

# Run specific test file
python tests/integration/test_id_card_with_photos.py
```

### Database Setup
```bash
# Initialize database with sample data
python scripts/setup/seed_data.py

# Set up test profile pictures
python scripts/setup/setup_test_photos.py
```

### Project Management
```bash
# Check database status
python scripts/setup/check_db.py

# View system credentials (for testing)
python scripts/setup/show_credentials.py
```

## 📊 Testing Profile Pictures

To test the profile picture functionality:

1. **Setup test data**:
   ```bash
   python scripts/setup/setup_test_photos.py
   ```

2. **Run the application**:
   ```bash
   python run.py
   ```

3. **Test ID card generation**:
   - Navigate to the "ID Card" tab
   - Enter roll number: STU001, STU002, STU003, etc.
   - Click "Load Student" then "Generate ID Card"
   - The ID card should display the student's profile picture

### Available Test Students
- **STU001** (John Doe)
- **STU002** (Jane Smith)
- **STU003** (Michael Brown)
- **STU004** (Emily Davis)
- **STU005** (Robert Wilson)
- **STU006** (Sarah Anderson)
- **STU007** (David Taylor)

## 🔧 Configuration

### Database Configuration
The database is located at `data/student_management_system.db` and is automatically created on first run.

### Asset Paths
- **Profile Pictures**: `src/assets/profile_pictures/`
- **UI Images**: `src/assets/images/`
- **Configuration**: `config/`

### Email Configuration
To enable email functionality, update the email settings in `src/main.py`:
```python
EMAIL_ADDRESS = "your_email@gmail.com"
EMAIL_PASSWORD = "your_app_password"
```

## 📖 Documentation

- **User Guide**: `docs/user/USER_GUIDE.md`
- **Implementation Notes**: `docs/fixes/`
- **API Documentation**: Available in source code docstrings

## 🐛 Troubleshooting

### Common Issues

1. **Database not found**: Run `python scripts/setup/seed_data.py` to initialize
2. **Profile pictures not showing**: Run `python scripts/setup/setup_test_photos.py`
3. **Missing dependencies**: Run `pip install -r config/requirements.txt`

### Logging
The application logs important events and errors. Check the console output for debugging information.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- **Rushikesh Atole** - *Initial work and development*
- **Team Contributors** - *Feature enhancements and testing*

## 🙏 Acknowledgments

- Built with Python and Tkinter
- UI styled with ttkbootstrap
- PDF generation using ReportLab
- Charts and analytics with Matplotlib
- Database operations with SQLite

---

**Version**: 2.0  
**Last Updated**: December 2024  
**Status**: Production Ready ✅
