import logging
from typing import Any, Dict

from remote_rest.schemas import VariableStoreStateModel
from src.attackmate.variablestore import VariableStore

logger = logging.getLogger(__name__)


def varstore_to_state_model(varstore: VariableStore) -> VariableStoreStateModel:
    """Converts AttackMate VariableStore to Pydantic VariableStoreStateModel."""
    if not isinstance(varstore, VariableStore):
        logger.error(f"Invalid type passed to varstore_to_state_model: {type(varstore)}")
        return VariableStoreStateModel(variables={'error': 'Internal state error'}) # Prevent crashes
    combined_vars: Dict[str, Any] = {}
    combined_vars.update(varstore.variables)
    combined_vars.update(varstore.lists)
    return VariableStoreStateModel(variables=combined_vars)
