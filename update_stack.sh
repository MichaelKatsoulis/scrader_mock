#!/bin/bash
docker stack services -q prod \
  | while read service; do
    docker service update --force $service
  done
