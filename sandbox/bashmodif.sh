#!/bin/bash
dockers=$(docker ps -a | perl -ne 'chomp; @cols = split /\s{2,}/, $_; $name=pop @cols; printf "%-28s %-20s %-20s %-30s\n", $name, $cols[1], $cols[3], $cols[4]' | grep -v IMAGE | awk '{print $2}')

url="https://deployment.digital.gob.cl/obtain-docker-tag?repo="

for docker in $dockers; do
     IFS=':' read -ra repo <<< "$docker"
     new=$(curl -s $url"${repo[0]}")

    # curl -s https://deployment.digital.gob.cl/obtain-docker-tag?repo="egob/totems-autoatencion"
    # v1.165

     script=$(docker ps -a | perl -ne 'chomp; @cols = split /\s{2,}/, $_; $name=pop @cols; printf "%-28s %-20s %-20s %-30s\n", $name, $cols[1], $cols[3], $cols[4]' | grep $docker | awk '{print $1}')
     if [[ "$new" =~ ^v[0-9]{1,4}\.[0-9]{1,4}$ ]] || [[ "$new" =~ ^v[0-9]{1,2}$  ]]; then
         if [ ! "$new" == "ERROR" ]; then
             if [ ! "$new" == "${repo[1]}" ]; then
                 if [ -f /storage/APP_GENERAL/conf/docker_scripts/$script.sh ]; then
                     /usr/bin/docker pull "${repo[0]}:"$new
                     /usr/bin/docker stop $script
                     /usr/bin/docker rm $script
                     /usr/bin/docker rmi $docker
                     /storage/APP_GENERAL/conf/docker_scripts/$script.sh $script "${repo[0]}:"$new
                 fi
             fi
         fi
     fi
done


------
docker container run -d --rm -it -v /var/run/docker.sock:/var/run/docker.sock -v /storage:/storage --name post_deployment egob/post_deployment_webhook:v1 sh
--------

import docker
import requests

client = docker.APIClient(base_url='unix://var/run/docker.sock')
container = client.containers(filters={'name':'totems-autoatencion'})
image_name = container[0]['Image']
container_version = image_name.split(':')[1]
container_id = container[0]['Id']
image_id = container[0]['ImageID']
repo_version =  requests.get('http://deployment.digital.gob.cl/obtain-docker-tag?repo=egob/totems-autoatencion').text
if container_version != repo_version:
    client.pull(image_name, repo_version)
    client.stop(container_id)
    client.remove_container(container_id)
    client.remove_image(image_id)

client





