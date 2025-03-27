# Team miHoyo

## Team members 

- *Mingze Li*
- *Ruijie Li*
- *Qilan Lin*
- *Peize Li*
- *Jiale She*
- *Yu-Tang Huang*
- *Youyou Wu*

  
## How to start
To begin, set up and activate a local (virtual) development environment. Make sure download the python(3.13.1). From the root of this project:
```
$ python -m venv venv
$ source venv/Scripts/activate
```

Install all required packages:

```
$ pip3 install -r requirements.txt
```


 To populate or delete the database with initial data:
```
$ python manage.py seed
$ python manage.py unseed_users
```
o ensure everything is working correctly, run all tests:
```
$ python manage.py test
```

To run the Django development server, use the following command:
```
$ python manage.py runserver
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
