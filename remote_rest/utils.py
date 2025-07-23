import logging
from typing import Any, Dict

from src.attackmate.variablestore import VariableStore

from remote_rest.schemas import VariableStoreStateModel

logger = logging.getLogger(__name__)


def varstore_to_state_model(varstore: VariableStore) -> VariableStoreStateModel:
    """Converts AttackMate VariableStore to Pydantic VariableStoreStateModel."""
    combined_vars: Dict[str, Any] = {}
    combined_vars.update(varstore.variables)
    combined_vars.update(varstore.lists)
    return VariableStoreStateModel(variables=combined_vars)
