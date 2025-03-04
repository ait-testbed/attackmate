from fastapi import FastAPI
from jsonrpc import JSONRPCResponseManager, dispatcher
from attackmate.attackmate import AttackMate
from attackmate.command import Command, CommandRegistry
import logging
import json

# Initialize FastAPI app
app = FastAPI(title="AttackMate JSON-RPC API", description="API for executing commands via JSON-RPC", version="1.0")

# Initialize logger
logger = logging.getLogger("attackmate-server")
logging.basicConfig(level=logging.INFO)

attackmate_instance = AttackMate()

@dispatcher.add_method
def do_command(type, cmd, **kwargs):
    """
    Execute a command using AttackMate.
    Expects JSON-RPC input with a command dictionary.
    """
    # Retrieve the correct Pydantic model based on type
    CommandClass = CommandRegistry.get_command_class(type)
    if not CommandClass:
        raise ValueError(f"Unknown command type: {type}")
    
    CommandClass.model_validate(type=type, cmd=cmd, **kwargs)
   
    try:
        # Create the command instance
        command = Command.create(type=type, cmd=cmd, **kwargs)
        result = attackmate_instance.run_command(command)
        return {"output": result.stdout, "status": result.returncode}
    except Exception as e:
        return {"error": str(e)}

@app.post("/attackmate")
async def json_rpc_handler(request: dict):
    response = JSONRPCResponseManager.handle(json.dumps(request), dispatcher)
    return response.json
