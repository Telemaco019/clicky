TAG ?= latest
PROJECT_NAME ?= clicky

# Docker
DOCKER_REGISTRY ?= ghcr.io/Telemaco019
DOCKER_IMAGE ?= $(DOCKER_REGISTRY)/$(PROJECT_NAME):$(TAG)


##@ General
.PHONY: help
help: ## Display this help.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)


##@ Dev
.PHONY: ruff
ruff: ## Run ruff linter
	uv run ruff check src tests

.PHONY: format
format: ## Fix formatting
	uv run black src tests

.PHONY: format-check
format-check: ## Check formatting
	uv run black src tests --check

.PHONY: type-check
type-check: ## Runs the type checker (mypy) against the app code
	uv run mypy src tests --strict

.PHONY: lint
lint: ruff format type-check  ## Run linting checks

.PHONY: prettier-format
prettier-format:
	npx prettier src/templates --write

.PHONY: prettier-check
prettier-check:
	npx prettier src/templates --check

.PHONY: lint-fix
lint-fix: format prettier-format ## Run the linter and fix issues
	uv run ruff check src tests --fix

.PHONY: revision
revision: ## Create an Alembic revision with the provided message
	uv run alembic revision --autogenerate -m "$(msg)"

.PHONY: run
run: ## Run the backend
	uv run src/clicky

.PHONY: run-dev
run-dev: ## Run the backend using dev env
	ENV=devdb uv run python src/app/__main__.py

.PHONY: test
test: ## Run the unit tests
	uv run pytest --cov=src --cov-context=test --cov-report=xml -v
	uv run coverage report
	uv run coverage xml

.PHONY: check
check: lint prettier-check format-check test ## Run the linter and the unit tests


##@ Docker
.PHONY: docker-image ## Show the Docker full image name
docker-image:
	@echo $(DOCKER_IMAGE)

.PHONY: docker-pull
docker-pull: ## Build the Docker image
	docker pull $(DOCKER_IMAGE)

.PHONY: docker-build
docker-build: ## Build the Docker image
	docker build -t $(DOCKER_IMAGE) --target runtime

.PHONY: docker-push
docker-push: ## Push the Docker image to the registry
	docker push $(DOCKER_IMAGE)


##@ Install
.PHONY: uv
uv: ## Install uv
	@which uv || pip install uv==1.8.3

.PHONY: install
install: uv  ## Install the dependencies
	uv sync --no-dev

.PHONY: install-dev
install-dev: uv  ## Install all the dependencies, including the dev ones
	uv sync
