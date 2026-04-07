#!/usr/bin/env python
"""
Project Setup Script - Creates directory structure and initializes the project.
Run this first: python setup_dirs.py
"""
import os
import sys

# Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DIRS = [
    'data/raw',
    'data/processed', 
    'src',
    'app',
    'api',
    'models',
    'notebooks'
]

def setup_project():
    """Create all necessary directories for the project."""
    print(f"Setting up project in: {BASE_DIR}\n")
    
    for d in DIRS:
        full_path = os.path.join(BASE_DIR, d)
        os.makedirs(full_path, exist_ok=True)
        
        # Create __init__.py for Python packages
        if d in ['src', 'app', 'api']:
            init_file = os.path.join(full_path, '__init__.py')
            if not os.path.exists(init_file):
                with open(init_file, 'w') as f:
                    f.write(f'"""{d.capitalize()} package for Insurance Risk Engine."""\n')
        
        # Create .gitkeep for empty directories
        gitkeep = os.path.join(full_path, '.gitkeep')
        if not os.path.exists(gitkeep) and d not in ['src', 'app', 'api']:
            with open(gitkeep, 'w') as f:
                f.write('')
        
        print(f"Created: {d}/")
    
    print("\n" + "="*50)
    print("Project structure created successfully!")
    print("="*50)
    print("\nNext steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Generate dataset: python src/data_generator.py")
    print("3. Run the app: streamlit run app/streamlit_app.py")
    
    return True

if __name__ == "__main__":
    setup_project()
