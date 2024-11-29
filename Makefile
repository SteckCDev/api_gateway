include environment.config

prepare:
    $(PYTHON_CMD) -m venv ${VENV_DIR}
    ${VENV_SCRIPTS_PATH}/python -m pip install -U pip poetry
    $(VENV_SCRIPTS_PATH)/poetry config virtualenvs.create false
    $(VENV_SCRIPTS_PATH)/poetry install --no-root
    $(VENV_SCRIPTS_PATH)/poetry run pre-commit install

    cp ${SRC_DIR}/.env.example ${SRC_DIR}/.env

inspect:
    ${VENV_SCRIPTS_PATH}/poetry run ruff check --fix .
    ${VENV_SCRIPTS_PATH}/poetry run mypy ${SRC_DIR}
    ${VENV_SCRIPTS_PATH}/poetry run pytest .

startup:
    docker compose --env-file ${SRC_DIR}/.env up -d --build --force-recreate --remove-orphans --renew-anon-volumes
    sleep 2
    ${VENV_SCRIPTS_PATH}/python ${SRC_DIR}/main.pyß

build: prepare inspect startup
