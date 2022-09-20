from fastapi import FastAPI
from pydantic import BaseSettings

# from .import_fiels import router as some_router

# router_list = [some_router]

# def bind_routes(application: FastAPI, router_modules: list, settings: BaseSettings) -> None:
#     """
#     Bind routes to application
#
#     :param application: FastAPI application
#     :param router_modules: List of router modules
#     :param settings: Application settings
#     :return: None
#     """
#
#     for router_module in router_modules:
#         router = router_module.api_router
#
#         #Router's prefix is added twice when using class-based views due the bug,
#         #https://github.com/dmontagu/fastapi-utils/issues/154
#         #so remove the duplication
        # for route in router.routes:
        #     route.path = route.path.replace(router.prefix + router.prefix, router.prefix)
        #
        # application.include_router(router, prefix="")