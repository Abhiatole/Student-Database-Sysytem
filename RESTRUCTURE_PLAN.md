# Repository Restructuring Plan

## Current Issues
- Multiple versions of main files (Main.py, MainComplete.py, main_fixed.py)
- Test files scattered in root directory
- Documentation files not organized
- Build artifacts mixed with source code
- Temporary files in root directory

## New Structure Plan

```
Student-Database-System/
├── src/                          # Main source code
│   ├── main.py                   # Primary application entry point
│   ├── app/                      # Application modules (existing)
│   └── assets/                   # Static assets
│       ├── images/
│       └── profile_pictures/
├── tests/                        # All test files
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   └── data/                     # Test data and utilities
├── docs/                         # Documentation
│   ├── implementation/           # Implementation notes
│   ├── fixes/                    # Fix documentation
│   └── user/                     # User documentation
├── scripts/                      # Utility scripts
│   ├── setup/                    # Setup and seeding scripts
│   └── maintenance/              # Maintenance utilities
├── data/                         # Database and data files
├── build/                        # Build artifacts (existing)
├── dist/                         # Distribution files (existing)
└── config/                       # Configuration files
```

## Files to Reorganize
1. **Main Files**: Keep Main.py, remove duplicates
2. **Test Files**: Move to tests/ directory
3. **Documentation**: Move to docs/ directory
4. **Scripts**: Move to scripts/ directory
5. **Assets**: Organize in src/assets/
