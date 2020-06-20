#!/bin/bash

set -ex

#@--- Function to authenticate to docker hub ---@#
docker_hub_auth() {

    docker login -p=$DOCKER_HUB_PASSWD -u=$DOCKER_HUB_USERNM

}

#@--- Function to export env variables ---@#
export_variables() {
    touch .env.local
    echo export DJANGO_ALLOWED_HOSTS=${DJANGO_ALLOWED_HOSTS} >> .env.local
    echo export DB_PORT=${DB_PORT} >> .env.local
    # echo export DEFAULT_API_URL=${DEFAULT_API_URL} >> .env.local #this is env specific
    echo export SENDER_EMAIL=${SENDER_EMAIL} >> .env.local
    echo export EMAIL_HOST=${EMAIL_HOST} >> .env.local
    echo export EMAIL_PORT=${EMAIL_PORT} >> .env.local
    echo export EMAIL_HOST_USER=${EMAIL_HOST_USER} >> .env.local
    echo export EMAIL_HOST_PASSWORD=${EMAIL_HOST_PASSWORD}  >> .env.local
}

#@--- Build docker image  and push---@#
build_and_push_image() {

    #@--- Build image for deployment ---@#
    if [[ $TRAVIS_BRANCH == "dev" ]]; then
        echo "++++++++ Start building dev image +++++++++"

        #@--- Run export function ---@#
        export_variables

        echo export DEFAULT_API_URL=${DEFAULT_API_URL_DEV} >> .env.local
        echo export SECRET_KEY=${SECRET_KEY_DEV} >> .env.local
        echo export DB_NAME=${DB_NAME_DEV} >> .env.local
        echo export DB_USER=${DB_USER_DEV} >> .env.local
        echo export DB_PASSWORD=${DB_PASSWORD_DEV} >> .env.local
        echo export DB_HOST=${DB_HOST_DEV} >> .env.local
        echo export DOTS_MONGO_URI=${DOTS_MONGO_URI_DEV} >> .env.local
        echo export DOTS_MONGO_DB_NAME=${DOTS_MONGO_DB_NAME_DEV} >> .env.local
        echo export BASE_URL=${BASE_URL_DEV} >> .env.local
        echo export KOBO_URI=${KOBO_URI_DEV} >> .env.local
        echo export KOBO_API_KEY=${KOBO_API_KEY_DEV} >> .env.local
        export APPLICATION_ENV=${APPLICATION_ENV_DEV} >> .env.local


        docker build -t $REGISTRY_OWNER/activity:$APPLICATION_NAME-$APPLICATION_ENV-$TRAVIS_COMMIT -f .docker/Dockerfile .
        echo "-------- Building Image Done! ----------"

        echo "++++++++++++ Push Image built -------"
        docker push $REGISTRY_OWNER/activity:$APPLICATION_NAME-$APPLICATION_ENV-$TRAVIS_COMMIT

    fi

    #@--- Build staging image for deployment ---@#
    if [[ $TRAVIS_BRANCH == "ISS-171-A" ]]; then
        echo "++++++++ Start building staging image +++++++++"

        #@--- Run export function ---@#
        export_variables

        echo export DEFAULT_API_URL=${DEFAULT_API_URL_STAGING} >> .env.local
        echo export SECRET_KEY=${SECRET_KEY_STAGING} >> .env.local
        echo export DB_NAME=${DB_NAME_STAGING} >> .env.local
        echo export DB_USER=${DB_USER_DEV} >> .env.local
        echo export DB_PASSWORD=${DB_PASSWORD_DEV} >> .env.local
        echo export DB_HOST=${DB_HOST_DEV} >> .env.local
        echo export DOTS_MONGO_URI=${DOTS_MONGO_URI_STAGING} >> .env.local
        echo export DOTS_MONGO_DB_NAME=${DOTS_MONGO_DB_NAME_STAGING} >> .env.local
        echo export BASE_URL=${BASE_URL_STAGING} >> .env.local
        echo export KOBO_URI=${KOBO_URI_STAGING} >> .env.local
        echo export KOBO_API_KEY=${KOBO_API_KEY_STAGING} >> .env.local
        export APPLICATION_ENV=${APPLICATION_ENV_STAGING} >> .env.local


        docker build -t $REGISTRY_OWNER/activity:$APPLICATION_NAME-$APPLICATION_ENV-$TRAVIS_COMMIT -f .docker/Dockerfile .
        echo "-------- Building Image Done! ----------"

        echo "++++++++++++ Push Image built -------"
        docker push $REGISTRY_OWNER/activity:$APPLICATION_NAME-$APPLICATION_ENV-$TRAVIS_COMMIT

    fi

    #@--- Build production image for deployment ---@#
    if [[ ! -z $TRAVIS_TAG ]]; then
        echo "++++++++ Start building production image +++++++++"

        #@--- Run export function ---@#
        export_variables

        # Set debug to false
        sed -i "s/DEBUG = True/DEBUG = False/" dots/settings.py

        echo export DEFAULT_API_URL=${DEFAULT_API_URL_PROD} >> .env.local
        echo export SECRET_KEY=${SECRET_KEY_PROD} >> .env.local
        echo export DB_NAME=${DB_NAME_PROD} >> .env.local
        echo export DB_USER=${DB_USER_PROD} >> .env.local
        echo export DB_PASSWORD=${DB_PASSWORD_PROD} >> .env.local
        echo export DB_HOST=${DB_HOST_PROD} >> .env.local
        echo export DOTS_MONGO_URI=${DOTS_MONGO_URI_PROD} >> .env.local
        echo export DOTS_MONGO_DB_NAME=${DOTS_MONGO_DB_NAME_PROD} >> .env.local
        echo export BASE_URL=${BASE_URL_PROD} >> .env.local
        echo export KOBO_URI=${KOBO_URI_PROD} >> .env.local
        echo export KOBO_API_KEY=${KOBO_API_KEY_PROD} >> .env.local
        export APPLICATION_ENV=${APPLICATION_ENV_PROD} >> .env.local


        docker build -t $REGISTRY_OWNER/activity:$APPLICATION_NAME-$APPLICATION_ENV-$TRAVIS_COMMIT -f .docker/Dockerfile .
        echo "-------- Building Image Done! ----------"

        echo "++++++++++++ Push Image built -------"
        docker push $REGISTRY_OWNER/activity:$APPLICATION_NAME-$APPLICATION_ENV-$TRAVIS_COMMIT

    fi

    #@--- Logout from docker ---@#
    echo "--------- Logout dockerhub --------"
    docker logout
}


#@--- main function ---@#
main() {
    if [[ $TRAVIS_EVENT_TYPE != "pull_request" ]]; then
        #@--- Run the auth fucntion ---@#
        docker_hub_auth

        #@--- Run the build function ---@#
        build_and_push_image
    fi
}

#@--- Run the main function ---@#
main
