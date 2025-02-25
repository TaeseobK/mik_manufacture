Write-Host "Installing pipenv..."
pip install pipenv

Write-Host "Installing dependencies..."
pipenv install

Write-Host "Activating virtual environment..."
pipenv shell

Write-Host "Running database migrations..."
python manufacture/manage.py migrate
python manufacture/manage.py migrate master --database=master
python manufacture/manage.py migrate manufacturing --database=manufacturing
python manufacture/manage.py migrate inventory --database=inventory
python manufacture/manage.py migrate user_profile --database=profile
python manufacture/manage.py migrate core --database=dump

Write-Host "Collect static files..."
py manufacture/manage.py collectstatic

Write-Host "Running server..."
py manufacture/manage.py runserver