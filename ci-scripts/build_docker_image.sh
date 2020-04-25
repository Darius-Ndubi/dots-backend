#!/bin/bash

set +ex

#@--- Function to authenticate to docker hub ---@#
docker_hub_auth() {

    docker login -p=$DOCKER_HUB_PASSWD -u=$DOCKER_HUB_USERNM

}

#@--- Function to export env variables ---@#
export_variables() {
    touch .env.deploy
    echo export DJANGO_ALLOWED_HOSTS=${DJANGO_ALLOWED_HOSTS} >> .env.deploy
    echo export DB_PORT=${DB_PORT} >> .env.deploy
}

#@--- Build docker image  and push---@#
build_and_push_image() {

    #@--- Build image for deployment ---@#
    echo "++++++++ Start building image +++++++++"
    if [[ $TRAVIS_BRANCH == "dev" ]]; then

        #@--- Run export function ---@#
        export_variables

        echo export SECRET_KEY=${SECRET_KEY_DEV} >> .env.deploy
        echo export DB_NAME=${DB_NAME_DEV} >> .env.deploy
        echo export DB_USER=${DB_USER_DEV} >> .env.deploy
        echo export DB_PASSWORD=${DB_PASSWORD_DEV} >> .env.deploy
        echo export DB_HOST=${DB_HOST_DEV} >> .env.deploy
        echo export MONGO_URI=${DOTS_MONGO_URI_DEV} >> .env.deploy
        echo export MONGO_DB_NAME=${DOTS_MONGO_DB_NAME_DEV} >> .env.deploy
        export APPLICATION_ENV=${APPLICATION_ENV_DEV} >> .env.deploy
        

        docker build -t $REGISTRY_OWNER/activity:$APPLICATION_NAME-$APPLICATION_ENV-$TRAVIS_COMMIT -f docker-deploy/Dockerfile .  
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
