from enum import StrEnum

from pydantic import BaseModel


class Role(StrEnum):
    DOCTOR = "doctor"
    NURSE = "nurse"
    BILLING_EXECUTIVE = "billing_executive"
    TECHNICIAN = "technician"
    ADMIN = "admin"


class Collection(StrEnum):
    GENERAL = "general"
    CLINICAL = "clinical"
    NURSING = "nursing"
    BILLING = "billing"
    EQUIPMENT = "equipment"


class CollectionAccess(BaseModel):
    collection: Collection
    roles: list[Role]


# Which roles can read each document collection. admin is listed explicitly everywhere,
# so every query goes through the same filter path (no "skip filter for admin" branch).
# nursing includes doctor as per the assignment's Data Sources table.
COLLECTION_ACCESS: list[CollectionAccess] = [
    CollectionAccess(collection=Collection.GENERAL, roles=list(Role)),
    CollectionAccess(collection=Collection.CLINICAL, roles=[Role.DOCTOR, Role.ADMIN]),
    CollectionAccess(collection=Collection.NURSING, roles=[Role.NURSE, Role.DOCTOR, Role.ADMIN]),
    CollectionAccess(collection=Collection.BILLING, roles=[Role.BILLING_EXECUTIVE, Role.ADMIN]),
    CollectionAccess(collection=Collection.EQUIPMENT, roles=[Role.TECHNICIAN, Role.ADMIN]),
]


def roles_for_collection(collection: Collection) -> list[Role]:
    return next(access.roles for access in COLLECTION_ACCESS if access.collection == collection)


def collections_for_role(role: Role) -> list[Collection]:
    return [access.collection for access in COLLECTION_ACCESS if role in access.roles]
