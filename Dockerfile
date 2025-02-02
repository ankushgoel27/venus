FROM python:3.7.14

COPY pyproject.toml ./pyproject.toml
COPY poetry.lock ./poetry.lock
COPY ./src ./src

ENV PYTHONPATH=${PYTHONPATH}:${PWD}

RUN pip3 install poetry==1.4.2 &&\
  poetry config virtualenvs.create false &&\
  poetry install

ENTRYPOINT ["poetry", "run", "start"]
