import datetime
from sqlalchemy import insert as sa_insert, literal_column, delete as sa_delete, select, update as sa_update
from fastapi import APIRouter, status, Request
from app.models.item import Items
from sqlalchemy.orm import joinedload
from app.utils.delete import delete_from_dict
from app.schems import ItemRequestData, ItemResponseData
from app.utils.items.utils import check_in_base, get_or_404, select_all_fiels_id, update_size_by_files_id

router = APIRouter(
    prefix="",
    tags=["Some tag"],
)


@router.post(
    "/import",
    status_code=status.HTTP_201_CREATED,
)
async def create(
        request: Request,
        model: ItemRequestData,
):
    async with request.app.state.db.get_session() as session:
        files_data = set()
        for item in model.items:
            in_base, res = await check_in_base(session, Items, item.id)
            if item.parent_id:
                await get_or_404(session, Items, item.parent_id)
            if in_base:
                data = item.dict()
                del data["id"]
                data["date"] = model.updateDate.replace(tzinfo=None)
                query = sa_update(Items). \
                    where(Items.id == item.id). \
                    values(**data). \
                    returning(literal_column("*"))

            else:
                item.date = model.updateDate.replace(tzinfo=None)
                query = sa_insert(Items). \
                    values(**item.dict()). \
                    returning(literal_column("*"))

            await session.execute(query)

            old_size = 0  # Необходим для того что бы при обновлении размера файла
            if item.type == "FILE":
                if in_base:
                    old_size = res.size
                files_data.add((item.id, old_size))

        await update_size_by_files_id(session, files_data)

        await session.commit()


@router.delete('/delete/{id}',
               status_code=status.HTTP_204_NO_CONTENT,
               )
async def delete(request: Request, id: str, date: datetime.datetime):
    query = sa_delete(Items).where(Items.id == id)

    async with request.app.state.db.get_session() as session:
        res = await get_or_404(session, Items, id)
        minus_size = res.size
        res = res.parent_id

        delete_from_dict(request.app.tree, id)

        while res:
            update_parent = sa_update(Items). \
                where(Items.id == res). \
                values(date=date.replace(tzinfo=None), size=Items.size - minus_size). \
                returning(literal_column("parent_id"))

            res = (await session.execute(update_parent)).scalars().first()
        await session.execute(query)
        await session.commit()


@router.get('/get_files', status_code=status.HTTP_200_OK)
async def get_files(request: Request):
    async with request.app.state.db.get_session() as session:
        files_id = await select_all_fiels_id(session)
        return files_id


@router.get('/nodes/{id}', response_model=ItemResponseData, status_code=status.HTTP_200_OK)
async def get_files(id: str, request: Request):
    async with request.app.state.db.get_session() as session:

        query = select(Items).where(Items.id == id).options(joinedload(Items.children))
        res = await session.execute(query)
        root = res.scalars().first()

        stack = [*root.children]
        while stack:
            cur = stack.pop()
            if not cur:
                continue
            query = select(Items).where(Items.id == cur.id).options(joinedload(Items.children))
            res = await session.execute(query)
            temp = res.scalars().first()
            for i in temp.children:
                stack.append(i)
    return root



