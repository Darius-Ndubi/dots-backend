# dots-backend [![codecov](https://codecov.io/gh/hikaya-io/dots-backend/branch/master/graph/badge.svg)](https://codecov.io/gh/hikaya-io/dots-backend)


## How to setup

- Create a virtual environment
- Install requirements using `pip install -r requirements.txt`
- Run migrations using `python manage.py migrate`
- Optional create a new superuser using `python manage.py createsuperuser`
- Run django server `python manage.py runserver`

### Docker setup

#### Prerequisites
- Ensure you stop postgresql from running as this will prevent postgres container from starting up. On linux run `sudo service postgresql stop` enter your password and proceed

#### Setting Up
- Check on the .env.dev_sample and rename it to .env.local using `cp .env.dev_sample .env.local`. This will be needed to add more variables to the dev docker environment
- Inside the project directory run the command `docker-compose build` to build application image
- To start dev env docker environment run `docker-compose up` wait until the log shows the IP and port the app is serving on. Access the API on `0.0.0.0:8000`
- To stop running the dev environment run press `Ctrl+c` in the docker environment terminal to stop the containers.


## How to use swagger
Once the server is running, you can access swagger at http://127.0.0.1:8000/docs

- Get access token using `/token` endpoint under token tab(value of `access` in the response).
- Hit the authorize button on top left and paste the new created access token with `Bearer` prefix i.e. `Bearer access_token`
- Hit authorize button again and you should see all the endpoints.
