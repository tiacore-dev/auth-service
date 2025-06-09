# app/utils/user_event_builder.py

from tiacore_lib.pydantic_models.auth_models import UserCompanyRelationOut
from tiacore_lib.rabbit.models import EventType, UserData, UserEvent

from app.database.models import User, UserCompanyRelation
from app.utils.permissions_get import get_company_permissions_for_user


async def build_user_event(user: User, event_type: EventType) -> UserEvent:
    relations = (
        await UserCompanyRelation.filter(user=user).prefetch_related("company").all()
    )
    relation_list = [UserCompanyRelationOut.model_validate(r) for r in relations]
    company_list = [r.company.id for r in relations]
    permissions = await get_company_permissions_for_user(user)

    return UserEvent(
        event=event_type,
        email=user.email,
        payload=UserData(
            user_id=str(user.id),
            is_superadmin=user.is_superadmin,
            permissions=permissions,
            companies=company_list,
            relations=relation_list,
        ),
    )
