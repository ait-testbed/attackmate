## neccessary tools

grpcio grpcio-tools protobuf PyYAML pydantic


## compile from proto files:
python -m grpc_tools.protoc -I./protobuf -I/usr/local/share/attackmate/venv/lib/python3.13/site-packages/grpc_tools/_proto --python_out=./remote --pyi_out=./remote --grpc_python_out=./remote protobuf/common.proto protobuf/command.proto protobuf/playbook.proto protobuf/attackmate_service.proto

server and generated files in the same directory.

still needed: "from . import etc." for files on the same level?

for example in playbook_pb2.py:

from . import common_pb2 as common__pb2

## base command structure:
python -m remote.client command <command_type> [specific_args...] [common_args...]

OR

python -m remote.client playbook <path_toplaybook>


example commands:
python -m remote.client command sleep --seconds 2

python -m remote.client command tempfile TEMP_DIR_VAR --make-dir

python -m remote.client command ssh 'id' --hostname <host_ip> --username <user> --password <password> --port 22 --creates-session my_ssh_session --exit-on-error

python -m remote.client command http-client GET https://example.com --output-headers --useragent "AttackMateClient/1.0



# TODO

--> type of arguments integer vs. float

--> Nested Parameter like payload_options

--> try playbooks

--> several persistent instances/server with sessions? session management? auth?

--> log levels of client and server?

--> grpc best practices

--> conversion methods really neccessary?

--> write Tests

