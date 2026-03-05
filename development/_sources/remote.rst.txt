
Remote Execution
=================
AttackMate can be used for remote command execution.
This section explains hoe the server handles authentication, logging, and AttackMate instances.

Authentication
--------------

The AttackMate API server secures its endpoints using **token-based authentication**.

* **Login Endpoint**: Clients must first authenticate by sending a username and password to the `/login` endpoint (e.g., `https://localhost:8445/login`). This endpoint is defined in `main.py` and uses FastAPI's `OAuth2PasswordRequestForm` for standard form encoding.
* **Token Generation**: Upon successful authentication, the server generates an access token and returns it to the client. 
* **Token Storage and Usage**:
    * The provided token is received and then stored globally (`CURRENT_TOKEN`) and optionally in an environment variable (`ATTACKMATE_API_TOKEN`).
    * For subsequent requests to protected endpoints (like `/command` or `/playbooks`), the client include this token in the `X-Auth-Token` header.
    * The `update_token_from_response` function in `client.py` also suggests a mechanism for token renewal, where the server might return a new token in a response.
* **SSL/TLS**: The `main.py` server is configured to run with HTTPS on port `8443`, requiring `key.pem` and `cert.pem` files for SSL/TLS encryption. Clients should specify the path to the server's public certificate.

Logging
-------

The AttackMate API server provides the following logging features:

* **Centralized Logging**: `main.py` initializes several loggers (`attackmate_api`, `playbook`, `output`, `json`) at startup.
* **Instance-Specific Logging**: For remote command and playbook executions, AttackMate implements instance-specific logging.
    * The `instance_logging` context manager (from `log_utils.py`) creates dedicated log files for each AttackMate instance based on its `instance_id`.
    * These logs are stored in a `attackmate_server_logs` directory (relative to the project root, or a configurable absolute path like `/var/log/attackmate_instances`).
    * Each remote command or playbook execution within an instance generates new timestamped log files (e.g., `20240715_123456_my_instance_output.log`).
    * This ensures that logs from different concurrent AttackMate instances remain separate.
* **Log Levels**: Log levels can be adjusted for debugging, providing more verbose output when needed.

AttackMate Instances
--------------------

The AttackMate API server manages AttackMate instances to handle multiple execution contexts.

* **Default Instance**: On startup, `main.py` initializes a single default AttackMate instance named `default_context`. This instance handles request to process entire playbooks.
* **Instance Management**: 
    * The server can create and manage multiple AttackMate instances, each identified by a unique `instance_id`.
* **Instance Lifecycle**:
    * Instances are stored in a global dictionary (`state.INSTANCES`).
    * When the API server starts (`lifespan` function in `main.py`), it loads a global AttackMate configuration and creates the `default_context` instance.
    * When the API server shuts down, it iterates through all active instances, performing cleanup operations like `clean_session_stores()` and `kill_or_wait_processes()` to ensure resources are properly released.
* **Command and Playbook Execution**:
    * The API routes (`commands`, `playbooks` routers included in `main.py`) receive client requests.
    * These requests specify an `instance_id` (or implicitly use `default_context`).
    * The API then dispatches the command or playbook to the designated AttackMate instance for execution. This allows for isolated execution environments, where variables and session data for one instance do not interfere with another.
* **State Management**: 
    * Each AttackMate instance maintains its own internal state, including a `VariableStore`. 
