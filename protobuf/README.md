## neccessary tools

grpcio grpcio-tools protobuf PyYAML pydantic


## compile from proto files: 
python -m grpc_tools.protoc -I./protobuf -I/usr/local/share/attackmate/venv/lib/python3.13/site-packages/grpc_tools/_proto --python_out=./remote --pyi_out=./remote --grpc_python_out=./remote protobuf/common.proto protobuf/command.proto protobuf/playbook.proto protobuf/attackmate_service.proto

server and generated files in the same directory.

still needed: "from . import etc." for sibling files