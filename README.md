# PYTAJNIKS

Simple and funny solution for common lecturers issues.

## Project description

No time to write it - codding stuffs are more important for now :)

## Developer gude

### Project setup
In order to set up the project you have to hold the following prerequisites:
* docker installed 
* docker-compose installed
* dockerd running

#### How to make it running
__Make project directory your current directory__

Set up executable rights:
```bash
chmod ugo+x start.sh
```

At the beginning download/build the docker images:
```bash
docker-compose build
```
Beware that this may need admin privileges depending on your setup.


At the initial run you would also need database migration to be proceed.
```bash
docker-compose run web python manage.py migrate
```

If everything is fine you should see something like that (otherwise you have 
to deal with it on your own)
```bash
Starting pytajnix_db_1 ... done
Operations to perform:
  Apply all migrations: admin, application, auth, contenttypes, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying admin.0003_logentry_add_action_flag_choices... OK
  Applying application.0001_initial... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying auth.0008_alter_user_username_max_length... OK
  Applying auth.0009_alter_user_last_name_max_length... OK
  Applying auth.0010_alter_group_name_max_length... OK
  Applying auth.0011_update_proxy_permissions... OK
  Applying sessions.0001_initial... OK
```

To create django superuser account:
```bash
docker-compose run web python manage.py createsuperuser
```

At the end it should look like that (if not - again - please handle with this)

```bash
Starting pytajnix_db_1 ... done
Username (leave blank to use 'root'): root
Email address: email@gmail.com
Password: 
Password (again): 
Superuser created successfully.
```

At the end finally you are ready to start working. 

In order to start the app run the following command:
```bash
docker-compose up
```

### Golden rules

* settings.py is only present to ease the development. __UNDER NO CIRCUMSTANCES
 PUT THE PRODUCTION CREDENTIALS THERE.__
* Do not push to master - __create pull request.__
* Master is for things that work, dev is for development.
* Create branches specific for task you are working on.