from pydantic import BaseModel, field_validator, model_validator

from app.utils.validate_helpers import sanitize_input


class CleanableBaseModel(BaseModel):
    @model_validator(mode="before")
    @classmethod
    def sanitize_strings(cls, values: dict) -> dict:
        for key, val in values.items():
            if isinstance(val, str):
                values[key] = sanitize_input(val)
        return values


def exists_validator(model_cls, field_name):
    @field_validator(field_name, mode="before")
    @classmethod
    async def validator(cls, value):
        if not await model_cls.exists(id=value):
            raise ValueError(f"{model_cls.__name__} не найден")
        return value

    return validator
