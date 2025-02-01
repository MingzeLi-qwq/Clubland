# Team miHoyo

## Team members 

- *Mingze Li*
- *Ruijie Li*
- *Qilan Lin*
- *Peize Li*
- *Jiale She*
- *Yu-Tang Huang*
- *Youyou Wu*

虚拟环境的搭建 To begin, set up and activate a local (virtual) development environment. Make sure download the python(3.13.1). From the root of this project:
```
$ python -m venv venv
$ source venv/Scripts/activate
```

Install all required packages:

```
$ pip3 install -r requirements.txt
```


测试用户数据的生成和删除 To populate or delete the database with initial data:
```
$ python manage.py seed_users
$ python manage.py unseed_users

```
测试代码的运行 To ensure everything is working correctly, run all tests:
```
$ python manage.py test

```

启动 Django 开发服务器，运行本地网站 To run the Django development server, use the following command:
```
$ python manage.py runserver

```