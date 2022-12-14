import uvicorn as uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette import status
from config.settings import Settings
from lib.db_acessor import DatabaseAccessor
from app.models.db import Base
from app.endpoints.import_fiels import router as imp_router


def bind_exceptions(app: FastAPI) -> None:
    @app.exception_handler(Exception)
    async def unhandled_error(_: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": str(exc)},
        )


def bind_events(app: FastAPI, db_settings: dict) -> None:
    @app.on_event("startup")
    async def set_engine():
        db = DatabaseAccessor(db_settings=db_settings)
        await db.run()
        # await db.init_db(Base)
        app.state.db = db
        app.tree = dict()

    @app.on_event("shutdown")
    async def close_engine():
        await app.state.db.stop()


def get_app() -> FastAPI:
    settings = Settings()
    app = FastAPI(
        title="Yandex DB",
        description="Хранилище данных",
        docs_url="/swagger",
    )
    bind_events(app, settings.db_settings)
    bind_exceptions(app)
    app.include_router(imp_router, prefix="")
    # app.include_router(tg_router, prefix="")

    # add_pagination(app)
    return app


app = get_app()
if __name__ == '__main__':

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8080,
    )
