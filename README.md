# dots-backend

## How to setup

- Create a virtual environment
- Install requirements using `pip install -r requirements.txt`
- Run migrations using `python manage.py migrate`
- Optional create a new superuser using `python manage.py createsuperuser`
- Run django server `python manage.py runserver`


## How to use swagger
Once the server is running, you can access swagger at http://127.0.0.1:8000/docs

- Get access token using `/token` endpoint under token tab(value of `access` in the response).
- Hit the authorize button on top left and paste the new created access token with `Bearer` prefix i.e. `Bearer access_token`
- Hit authorize button again and you should see all the endpoints.
