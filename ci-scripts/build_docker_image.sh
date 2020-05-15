#!/bin/bash

set +ex

#@--- Function to authenticate to docker hub ---@#
docker_hub_auth() {

    docker login -p=$DOCKER_HUB_PASSWD -u=$DOCKER_HUB_USERNM

}

#@--- Function to export env variables ---@#
export_variables() {
    touch .env.local
    source .env.local
    echo export DJANGO_ALLOWED_HOSTS=${DJANGO_ALLOWED_HOSTS} >> .env.local
    echo export DB_PORT=${DB_PORT} >> .env.local
    echo export DEFAULT_API_URL=${DEFAULT_API_URL} >> .env.local
}

#@--- Build docker image  and push---@#
build_and_push_image() {

    #@--- Build image for deployment ---@#
    echo "++++++++ Start building image +++++++++"
    if [[ $TRAVIS_BRANCH == "dev" ]]; then

        #@--- Run export function ---@#
        export_variables

        echo export SECRET_KEY=${SECRET_KEY_DEV} >> .env.local
        echo export DB_NAME=${DB_NAME_DEV} >> .env.local
        echo export DB_USER=${DB_USER_DEV} >> .env.local
        echo export DB_PASSWORD=${DB_PASSWORD_DEV} >> .env.local
        echo export DB_HOST=${DB_HOST_DEV} >> .env.local
        echo export DOTS_MONGO_URI=${DOTS_MONGO_URI_DEV} >> .env.local
        echo export DOTS_MONGO_DB_NAME=${DOTS_MONGO_DB_NAME_DEV} >> .env.local
        export APPLICATION_ENV=${APPLICATION_ENV_DEV} >> .env.local


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
