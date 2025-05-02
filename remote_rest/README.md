pip install fastapi uvicorn httpx PyYAML pydantic


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
