#!/bin/bash

# Function to check and install pipenv if not installed
check_and_install_pipenv() {
    if ! [ -x "$(command -v pipenv)" ]; then
        echo "pipenv not installed. Installing pipenv..."
        pip install pipenv
    else
        echo "pipenv is already installed."
    fi
}

# Check if pipenv is installed, if not, install it
check_and_install_pipenv

# Install dependencies
echo "Installing dependencies..."
pipenv install

# Activate virtual environment
echo "Activating virtual environment..."
pipenv shell

# Run migrations
echo "Running migrations..."
python manufacture/manage.py migrate
python manufacture/manage.py migrate master --database=master
python manufacture/manage.py migrate manufacturing --database=manufacturing
python manufacture/manage.py migrate inventory --database=inventory
python manufacture/manage.py migrate user_profile --database=profile
python manufacture/manage.py migrate core --database=dump

# Collect static files
echo "Collecting static files..."
python manufacture/manage.py collectstatic

# Run Django server (this step might be omitted on production)
echo "Starting Django server..."
python manufacture/manage.py runserver
