#!/bin/bash
set -e
docker compose -p llm -f docker-compose.yml -f docker-compose-build.yml build $1
docker compose -p llm -f docker-compose.yml up -d --remove-orphans
