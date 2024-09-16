
.PHONY = deps up down destroy all help

# デフォルトターゲットを最初に定義
.DEFAULT_GOAL := help

# to check if docker is installed on the machine
DOCKER := $(shell command -v docker)
DOCKER_COMPOSE := $(shell command -v docker-compose)

deps:
ifndef DOCKER
	@echo "Docker is not available. Please install docker"
	@echo "try running sudo apt-get install docker"
	@exit 1
endif
ifndef DOCKER_COMPOSE
	@echo "docker-compose is not available. Please install docker-compose"
	@echo "try running sudo apt-get install docker-compose"
	@exit 1
endif

up: deps down
	docker-compose up --build;

down: deps
	docker volume ls
	docker-compose ps
	docker images
	docker-compose down;

destroy: deps
	docker images | grep -i llm_code_navigator | awk '{print $$3}' | xargs docker rmi -f
	docker volume prune -f

# すべてのターゲットを実行
all: deps destroy up

######################
# HELP
######################

help:
	@echo '----'
	@echo 'deps             - check docker env'
	@echo 'up               - start llm_code_navigator'
	@echo 'down				- stop llm_code_navigator'
	@echo 'destroy          - remove docker images'
	@echo 'all              - start after destroy'