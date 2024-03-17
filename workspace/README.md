# Mirko.ai Workspace

[Workspace: Base Docker Env Setup](https://github.com/markokraemer/mirko.ai/issues/1)

## Requirements
* Docker

## Setup

From this `workpace` dir. 

This will build the container and open a shell

```
# Use -d for detached mode or a separate terminal
docker-compose up --build -d

# Run a shell
docker-compose exec dev-env bash

# When done, if detached
docker-compose down
```

## Using the docker env

Example usage from the docker shell, checking out a repo and running its tests.

```
mkdir checkout
cd checkout
git clone https://github.com/jxnl/instructor.git
cd instructor
pyenv global 3.12

python -m pip install poetry
poetry install --with dev

OPENAI_API_KEY=X poetry run pytest tests/ -k "not openai"
```
