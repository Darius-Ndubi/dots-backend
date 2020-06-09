#!/bin/bash

set -ex

#@--- install and setup python ---@#
setup_python() {
    sudo add-apt-repository ppa:deadsnakes/ppa -y
    sudo apt-get update -y
    sudo apt-get install software-properties-common python-software-properties -y
    sudo apt-get install python3.7 -y
    sudo apt-get install python3-pip python3-setuptools -y
    sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.5 2
    sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 10
    pip3 install --upgrade pip
}

#@--- Setup mongo db ---@#
setup_mongo() {
    wget -qO - https://www.mongodb.org/static/pgp/server-4.2.asc | sudo apt-key add -
    sudo apt-get install gnupg
    echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/4.2 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.2.list
    sudo apt-get update -y
    sudo apt-get install -y mongodb-org
    sudo systemctl start mongod
}

#@--- Setup postgresdb ---@#
setup_postgresql() {
    #@--- setup postgres db with docker, just for the test ---@#
    docker run -dp 5432:5432 -e POSTGRES_PASSWORD='test_user' -e POSTGRES_USER="postgres" -e POSTGRES_DB='test_db' postgres:11
    sleep 5
    #@--- Check if db is up ---@#
    docker ps
}

#@--- Install and activate virtualenv ---@#
install_activate_virtualenv() {
    pip3 install pipenv
    pipenv install
    source $(python3 -m pipenv --venv)/bin/activate
    pip install -r test_requirements.txt

    #@ --- export variables for the postgres db ---@#
    export DB_NAME="test_db"
    export DB_USER=postgres
    export DB_HOST=0.0.0.0
    export DB_PORT=5432
    export DB_PASSWORD='test_user'

}

#@--- run tests --- @#
run_tests() {
    echo "++++++++++++++++ Run tests ++++++++++++++++"
    coverage run --source='.' manage.py test core
}

#@--- function to report coverage ---@#
report_coverage() {
    coverage xml
    bash <(curl -s https://codecov.io/bash) -y codecov.yml
}

#@--- Main function ---@#
main() {

    #@--- run Setup function ---@#
    setup_python

    #@-- Run  mongo setup function ---@#
    setup_mongo

    #@-- Run postgreswl setup function ---@#
    setup_postgresql

    #@--- start virtualenv ---@#
    install_activate_virtualenv

    #@--- Run tests ---@#
    run_tests

    #@--- Report Coverage ---@#
    report_coverage
    exit 0
}

#@--- Run main function ---@#
main
