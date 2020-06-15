#!/bin/bash

set +ex

#@--- install kubectl and doctl ---@#
install_kubectl_doctl() {
    if [[ $TRAVIS_BRANCH == "dev" ]] || \
        [[ $TRAVIS_BRANCH == "ISS-171" ]]; then
        echo "++++++++++++ install kubectl ++++++++++++"
        curl -LO https://storage.googleapis.com/kubernetes-release/release/`curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt`/bin/linux/amd64/kubectl

        # Make downloaded binary executable
        chmod +x ./kubectl

        # Add binary to path
        sudo mv ./kubectl /usr/local/bin/kubectl

        # Check the version
        kubectl version --client

        # Install digital ocean cli tool
        sudo apt-get install snapd -y
        sudo snap install doctl
        sudo snap connect doctl:kube-config

        sudo apt-get install gettext -y

        mkdir /home/travis/.kube
    fi
}

#@--- Authorize kubectl to cluster ---@#
auth_kubectl_cluster() {
    # Authenticate kubectl to the cluster
    if [[ $TRAVIS_BRANCH == "dev" ]] || \
        [[ $TRAVIS_BRANCH == "ISS-171" ]]; then
        doctl auth init -t $SERVICE_ACCESS_TOKEN
        doctl -t $SERVICE_ACCESS_TOKEN kubernetes cluster kubeconfig save $CLUSTER_NAME
        kubectl create namespace $APPLICATION_ENV || echo "++++++ Namespace Exists ++++++"
        kubectl create namespace ingress-nginx || echo "++++++ Namespace ingress-nginx Exists ++++++"
    fi

    # fetch cluster nodes
    kubectl get nodes

    echo "+++ Kubectl installed and configured to the cluster +++++"
}

#@--- Clone infrastructure repo ---@#
clone_deployfiles_repo() {
    git clone -b infrastructure_1 $INFRASTRUCTURE_REPO
    cd deployment-files/deploy_yamls
}

#@--- Function to deploy the app ---@#
deploy_app() {
    echo "-------- deploy application -------------"

    echo "-------- generate secret for dockerhub -----------"
    docker login -p=$DOCKER_HUB_PASSWD -u=$DOCKER_HUB_USERNM
    kubectl create secret generic regcred \
        --from-file=.dockerconfigjson=$FILE_PATH \
        --type=kubernetes.io/dockerconfigjson -n $APPLICATION_ENV

    if [[ $TRAVIS_BRANCH == "dev" ]] || \
        [[ $TRAVIS_BRANCH == "ISS-171" ]]; then
        echo "------- generate deployfiles --------------"
        envsubst < ./api/deployment-limits > deployment.yaml
        envsubst < ./api/service > service.yaml
        envsubst < ./api/autoscaler > autoscaler.yaml
        envsubst < ./shared_api_web_files/api-web-ingress-config > ingress-config.yaml
        envsubst < ./cert-config/cert-issuer > cert-issuer.yaml
        envsubst < ./cert-config/cert-secret > cert-secret.yaml
        envsubst < ./cert-config/shared-certificate > certificate.yaml

        echo "+++++++  make deployments with kubectl +++++++"
        kubectl create clusterrolebinding serviceaccounts-cluster-admin --clusterrole=cluster-admin --group=system:serviceaccounts
        kubectl apply -f man.yaml
        kubectl apply --validate=false -f cert-config/cert-manager-0.12.0.yaml
        kubectl apply --validate=false -f metrics-server.yaml
        sleep 70

        kubectl apply -f ingress-service.yaml
        kubectl apply -f cert-secret.yaml
        kubectl apply -f cert-issuer.yaml
        kubectl apply -f certificate.yaml
        kubectl apply -f deployment.yaml
        kubectl apply -f service.yaml
        kubectl apply -f autoscaler.yaml
        kubectl apply -f ingress-config.yaml
        echo "--------- deployment made !! ----------------"
        #@--- Check if the last command run successfuly ---@#
        if [[ $? -eq 0 ]]; then
            export DEPLOY="success"
        else
            export DEPLOY="fail"
        fi
    fi
}

#@--- Function to replace some key variables ---@#
replace_variables() {

    #@--- Replace necesary variables for dev  env ---@#
    if [[ $TRAVIS_BRANCH == "dev" ]]; then
        export CLUSTER_NAME=${CLUSTER_NAME_DEV_ENV}
        export HOST_DOMAIN=${HOST_DOMAIN_DEV_ENV}
        export APPLICATION_ENV=${APPLICATION_ENV_DEV}
    fi

    #@--- Replace necesary variables for staging  env ---@#
    if [[ $TRAVIS_BRANCH == "ISS-171" ]]; then
        export CLUSTER_NAME=${CLUSTER_NAME_STAGING}
        export HOST_DOMAIN_WEB=${HOST_DOMAIN_WEB_STAGING}
        export HOST_DOMAIN_API=${HOST_DOMAIN_API_STAGING}
        export APPLICATION_ENV=${APPLICATION_ENV_STAGING}
    fi

}

#@--- Send slack notification ---@#
notify_team_on_slack() {

    cd ..
    chmod 777 helper_scripts/slack_notification.sh
    ./helper_scripts/slack_notification.sh

}

#@--- Main Function ---@#
main() {

    if [[ $TRAVIS_EVENT_TYPE != "pull_request" ]]; then
        #@--- Run install and setup function ---@#
        install_kubectl_doctl

        #@--- run the replace function ---@#
        replace_variables

        #@--- Run the setup function ---@#
        auth_kubectl_cluster

        #@--- run function to fetch deploy files ---@#
        clone_deployfiles_repo

        #@--- Run deployment function ---@#
        deploy_app

        #@--- Run notification fucntion ---@#
        # notify_team_on_slack
    fi

}

#@--- Run the main function ---@#
main
