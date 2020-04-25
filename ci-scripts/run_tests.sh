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

#@--- Install and activate virtualenv ---@#
install_activate_virtualenv() {
    pip3 install pipenv
    pipenv install
    source $(python3 -m pipenv --venv)/bin/activate
    pip install -r test_requirements.txt
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

    #@--- run Setup finction ---@#
    setup_python

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
