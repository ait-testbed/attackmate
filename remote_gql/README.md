# Attackmate remote execution with graphQl API

## Dependencies
pip install "strawberry-graphql[debug-server]" httpx PyYAML uvicorn stringcasepython-dotenv pydantic

debug server includes uvicorn and ASGI support?

types queires and mutations are defined in schema.py

dependency injextion a bit tricky, how to access attackmate instance in schema?
subclass GraphQL with get_context() method

## run server
python -m remote_gql.server

## run client
### sending whole playbook as yml
python -m remote_gql.client playbook examples/playbook.yml

### sending filepath to playbook on the attacker
python -m remote_gql.client remote-playbook playbook.yml

### shell command
python -m remote_gql.client command shell 'echo GraphQL Test'
python -m remote_gql.client command shell 'echo GraphQL Test' --background

###  Set variable
python -m remote_gql.client command setvar MY_VAR "hello"

###  Debug
python -m remote_gql.client command debug  "Debug this" --varstore

### Example: Sleep
python -m remote_gql.client command sleep --seconds 3

### Example: Mktemp (create file)
python -m remote_gql.client command mktemp MY_TEMP_FILE

### Example: Mktemp (create dir)
python -m remote_gql.client command mktemp MY_TEMP_DIR --make-dir
