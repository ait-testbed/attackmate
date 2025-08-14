pip install fastapi uvicorn httpx PyYAML pydantic argon2_cffi


uvicorn remote_rest.main:app --host 0.0.0.0 --port 8000 --reload

[] TODO sort out logs for different instances

[] TODO return logs to caller

[] TODO limit max. concurent instance number

[] TODO concurrency for several instances?

[] TODO add authentication

[] TODO queue requests for instances

[] TODO dynamic configuration of attackmate config

[] TODO make logging (debug, json etc) configurable at runtime (endpoint or user query paramaters?)

[] TODO ALLOWED_PLAYBOOK_DIR -> define in and load from configs

[] TODO add swagger examples

[] TODO generate/check OpenAPI schema

[x] TODO seperate router modules?





# Execute a playbook by sending its YAML content (uses a temporary instance)
python -m remote_rest.client playbook-yaml examples/playbook.yml

# Request the server execute a playbook from its allowed directory
 Ensure 'playbook.yml' exists in server's ALLOWED_PLAYBOOK_DIR

python -m remote_rest.client playbook-file safe_playbook.yml


# Single Command Execution (on a persistent Instance)

## Shell Command
```bash
python -m remote_rest.client command shell 'echo "Hello"'
```

### Run a command in the background or with metadata
    ```bash
    python -m remote_rest.client command shell 'echo hello' --metadata tactic=recon --metadata technique=TXXX
    ```

## Run a Sleep Command (Background):
    ```bash
    python -m remote_rest.client command sleep --seconds 8 --background
    ```
    # (Client returns immediately, server sleeps)


# Certificate generation
preliminary, automate later?
with open ssl
    ```bash
    openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
    ```

Common Name: localhost (or ip adress the server will be)


running client:

```bash
python -m client --cacert <path_to_cert> login user user
```
