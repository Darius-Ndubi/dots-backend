FROM alpine:3.10 as build

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

# Working directory where all the setup would take place in the image
WORKDIR /dots-api

# The default user that should be used
USER root

# copy the requirements.txt file which contains dependencies to be installed
COPY ./requirements.txt /dots-api

# Install Alpine packages needed for the provisioning of the instance with python
# and other packages
RUN apk -U update 
RUN apk add --no-cache --update build-base 
RUN apk add curl git libffi-dev ncurses-dev openssl libressl python3-dev musl-dev libpq readline-dev tk-dev xz-dev zlib-dev py-psycopg2 linux-headers
RUN apk add bash zlib-dev zlib bzip2-dev libffi libffi-dev readline-dev postgresql-libs sqlite-dev py3-virtualenv postgresql-dev && \
    curl -L https://raw.githubusercontent.com/pyenv/pyenv-installer/master/bin/pyenv-installer | sh && \
    export PATH="/root/.pyenv/bin:$PATH" && \
    eval "$(pyenv init -)" && \
    eval "$(pyenv virtualenv-init -)"  && \
    pyenv install 3.7.7 -s && \
    export PATH="/root/.pyenv/versions/3.7.7:$PATH" && \
    export LC_ALL=C.UTF-8 && \
    export LANG=C.UTF-8 && \
    export PATH="/root/dots-api/start.sh:$PATH" && \
    pip3 install --user pipenv==2018.5.18 && \
    python3 -m pipenv install

# check the root dir for the .cache dir
RUN ls -ahl /root

# remove the .cache dir
RUN rm -rf /root/.cache

# build the minimal application image from Alpine
FROM alpine:3.10

USER root

# Install packages needed for the application to run
RUN apk -U update 

RUN apk add --no-cache curl git libffi-dev ncurses-dev openssl libressl python3  python3-dev musl-dev libpq readline-dev tk-dev xz-dev zlib-dev py-psycopg2 linux-headers \
    bash zlib-dev zlib bzip2-dev libffi libffi-dev readline-dev postgresql-libs sqlite-dev py3-virtualenv postgresql-dev

WORKDIR /dots-api

COPY --from=build /root /root

RUN export PATH="/root/.pyenv/versions/3.7.7:$PATH" 

RUN ls -ahl /root

RUN rm -rf /root/.cache

COPY . .

RUN chmod 777 docker-deploy/start.sh  && \
    source /root/.local/share/virtualenvs/dots-api-*/bin/activate && \
    source .env.deploy && \
    mkdir static || echo "directory exists" && \
    echo 'yes' | python3 manage.py collectstatic

#  command used to create the virtual environment before the application is started
CMD ["/bin/bash","-c","source /root/.local/share/virtualenvs/dots-api-*/bin/activate"]

#  the entry point where the application can be started on
ENTRYPOINT ["docker-deploy/start.sh"]
