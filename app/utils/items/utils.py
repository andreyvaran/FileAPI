from fastapi import HTTPException, status
from sqlalchemy import select, update, literal_column
from app.models.item import Items
from app.schems.item import SystemItemType
from typing import Set, Tuple


def get_pk(model) -> str:
    return list(model.__table__.primary_key)[0].name


async def check_in_base(session, model, param_id):
    result = await session.get(
        model,
        {get_pk(model): param_id}
    )
    if result is None:
        return False, None

    return True, result


async def get_or_404(session, model, param_id):
    result = await session.get(
        model,
        {get_pk(model): param_id}
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Not found in {model.__tablename__} data with primary key = {param_id}",
        )
    return result


async def select_all_fiels_id(session):
    query = select(Items).where(Items.type == SystemItemType.FILE)
    result = (await session.execute(query)).scalars().all()
    return list(map(lambda x: x.id, result))


async def update_size_by_files_id(session, files_data: Set[Tuple[str, int]]) -> None:

    for file_data in files_data:
        print("We are here ")
        print(file_data)
        parent = await session.get(Items, file_data[0])
        print(f"{parent.size}")
        add_size = parent.size - file_data[1]
        print(f"we want to add {add_size=}")
        parent = parent.parent_id
        while parent:
            update_parent = update(Items).where(Items.id == parent).values(size=Items.size + add_size).returning(
                literal_column("parent_id"))
            parent = (await session.execute(update_parent)).scalars().first()
