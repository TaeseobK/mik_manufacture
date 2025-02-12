I'll guide you to deploy this for production


===================================================================================
Run This To migrate

python manufacture/manage.py migrate inventory --database=inventory
python manufacture/manage.py migrate master --database=master
python manufacture/manage.py migrate manufacturing --database=manufacturing
python manufacture/manage.py migrate user_profile --database=profile
python manufacture/manage.py migrate core --database=dump
python manufacture/manage.py migrate auth --database=default
python manufacture/manage.py migrate admin --database=default
python manufacture/manage.py migrate contenttypes --database=default
python manufacture/manage.py migrate sessions --database=default
python manufacture/manage.py migrate

===================================================================================
All the requirement is on requirement.txt, execute this to install all the requirements :

pip install -r requirement.txt

===================================================================================
Create env :

python -m venv env

===================================================================================
Create SuperAdmin or SuperUser

python manufacture/manage.py createsuperuser

===================================================================================
Activate env just put ths into terminal "env/Scripts/activate"


===================================================================================
How to Run the server

go to "MIK/manufacture" and run "py manage.py runserver"


===================================================================================
All the settings is in "MIK/manufacture/manufacture/settings.py"

including :
- Databases
- Middleware
- Directory for Media
- staticfiles
- all apps
- Hosts
- Debugging

===================================================================================
for the Databases
'default': {
        'ENGINE': 'django.db.backends.mysql',           #this is for the engine like mysql, postgresql, sqlite3 or whatever
        'NAME': 'default',                              #this for the name of the database
        'USER' : 'root',                                #this is for the User on the database e.g adminer.php, PhpMyAdmin
        'PASSWORD' : '2025',                            #Password from your database
        'HOST' : 'localhost',                           #The Host from the database
        'PORT' : '3306'                                 #PORT from the databases
    },


===================================================================================
Explaination for every databases

default :
Default database is default Django Databases. including authentication for users, groups, role and there's so much.

profile :
Profile database for user profile, maybe it's useless for now, but then it's powerful when i decided to use multiple databases.

master :
Master database is for storing master data that can't be deleted e.g Company, JobPositiion, Employment, etc.

dump :
Storing all user logs and some data that'll go bigger in short time.

inventory :
Inventory database used for storing data that used by 'Inventory' apps

manufacturing :
Stored for data that used by 'Manufacture' apps


===================================================================================
Domain

Set your domain at settings.py

there's a "DEBUG = True", you can change it to False if you deploy it to production

and "ALLOWED_HOSTS = []" for you domain example

ALLOWED_HOSTS = ['youdomain.com', 'www.yourdomain.co.id']

don't forget to check if your domain has https or https

if your domain is http
then in your settings.py should be like this
#To Deploy u must change this to True

CSRF_COOKIE_SECURE = False

SESSION_COOKIE_SECURE = False

if your domain is https
then your settings.py should be like this
#To Deploy u must change this to True

CSRF_COOKIE_SECURE = True

SESSION_COOKIE_SECURE = True