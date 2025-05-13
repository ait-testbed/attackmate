from typing import Dict, Optional

from fastapi import Depends, HTTPException, Path
from src.attackmate.attackmate import AttackMate
from src.attackmate.schemas.config import Config

# Define shared state variables here
INSTANCES: Dict[str, AttackMate] = {}
attackmate_config: Optional[Config] = None


def get_instances_dict() -> Dict[str, AttackMate]:
    """Dependency to get the shared INSTANCES dictionary."""
    # returns the global dict reference
    return INSTANCES


def get_attackmate_config() -> Config:
    """Dependency to get the shared AttackMate configuration."""
    if attackmate_config is None:
        raise RuntimeError('Server configuration is not available.')
    return attackmate_config


def get_instance_by_id(
    instance_id: str = Path(...),
    instances: Dict[str, AttackMate] = Depends(get_instances_dict)
) -> AttackMate:
    """Dependency to get a specific AttackMate instance, raising 404 if not found."""
    instance = instances.get(instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail=f"AttackMate instance '{instance_id}' not found.")
    return instance


def get_persistent_instance(
    instances: Dict[str, AttackMate] = Depends(get_instances_dict)
) -> AttackMate:
    """Dependency to get the default context persistent AttackMate instance, raising 404 if not found."""
    instance = instances.get('default_context')
    if not instance:
        raise HTTPException(status_code=404, detail='Persistent AttackMate instance not found.')
    return instance
