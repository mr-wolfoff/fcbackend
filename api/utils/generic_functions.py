from typing import Any


def set_model_from_another_model(from_model: Any, to_model: Any) -> Any:
    """Sets the fields that exist in to_model and are not None in from_model."""
    from_data = from_model.dict(exclude_unset=True)
    for key, value in from_data.items():
        setattr(to_model, key, value)
    return to_model