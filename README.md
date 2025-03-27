# Team miHoyo

## Team members 

- *Mingze Li*
- *Ruijie Li*
- *Qilan Lin*
- *Peize Li*
- *Jiale She*
- *Yu-Tang Huang*
- *Youyou Wu*

  
# Team miHoyo

## Team Members

- *Mingze Li*
- *Ruijie Li*
- *Qilan Lin*
- *Peize Li*
- *Jiale She*
- *Yu-Tang Huang*
- *Youyou Wu*

## How to Start

### 1. **Set Up Local Development Environment**

To begin, set up and activate a local (virtual) development environment to ensure all dependencies and settings are isolated. Follow these steps:

```
$ python -m venv venv
```
On macOS and Linux:
```
$ source venv/bin/activate
```
On Windows:
```
$ source venv/Scripts/activate

```

#### 1.1. Install Python (3.13.1)

Make sure that you have Python 3.13.1 installed. You can download it from the official Python website: [Python Downloads](https://www.python.org/downloads/release/python-3131/).

#### 1.2. Install Node.js (22.14.0) and Node Package Manager (npm) (10.9.2)
Install Node.js and npm by following the instructions on the official Node.js website: [Node.js Downloads](https://nodejs.org/en/download).
On Windows:
```
$ winget install Schniz.fnm
$ fnm install 22.14.0
```
On macOS and Linux:
```
$ curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.2/install.sh | bash
$ nvm install 22.14.0
```

#### 1.3. Activate Virtual Environment and Install Dependencies
```
$ python -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

### 2. **Populate or Delete Database with Initial Data**

To populate or delete the database with initial data:
```
$ python manage.py seed
```
To delete the database and re-seed it with initial data:
```
$ python manage.py unseed
```
### 3. **Run Test**
To ensure everything is working correctly, run all tests:
```
$ python manage.py test
```

### 4. **Run the Django Development Server**
To run the Django development server, use the following command:
```
$ python manage.py runserver
```
The server will be hosted at http://127.0.0.1:8000/ by default.

If you want to specify a different port, you can use the following command:
```
$ python manage.py runserver <port_number>  
```

### 5. **Run the React Development Server**
To run the React development server, use the following command:
```
$ npm run dev
```


## Practical User Instances in Seed Data

The following user instances will only be created after running the command `$ python manage.py seed`:

- User: `@john_doe`
  - A default-generated Manager account for the Book Club, intended for accessing Club Manager-specific functionalities.
- User: `@admin`
  - To ensure system security, only administrator accounts can register new administrator users. Therefore, an initial administrator account is necessary.
  - The `@admin` user is an administrator account explicitly created via `seed_user.py`, enabling access to functionalities that require admin permissions.

## Deployed Version

You can access the deployed version of this system at [http://51.21.191.188:8000/](http://51.21.191.188:8000/).

## Troubleshooting
Common Errors:
Database Connection Error: Ensure that the database credentials in settings.py are correctly set for your local or production environment.

Missing Environment Variables: If the application fails to start, double-check that all necessary environment variables (e.g., DJANGO_SECRET_KEY, REACT_APP_API_URL) are set correctly.

Frontend Build Errors: If there are issues with building the React app, try deleting the node_modules folder and running npm install again.
