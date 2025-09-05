"""Registers FastAPI routers."""

import os

from app.utils.dynamic_imports import get_attr_from_module


def get_routers() -> list:
    """Get Routers via dynamic way."""

    def get_router_modules() -> list:
        """Get Routers modules."""
        abs_path = os.path.abspath(__file__)
        path = os.path.dirname(abs_path)
        dirs = os.listdir(path)

        dirs.remove(os.path.basename(__file__))

        return dirs

    def get_router_instances(modules: list) -> list:
        """Get Routers instances."""
        routers = []

        for item in modules:
            if item.endswith('.py'):
                abs_path_module = f'{__name__}.{item[:-3]}'
                router = get_attr_from_module(abs_path_module, 'router')
                routers.append(router)

        return routers

    router_modules = get_router_modules()
    return get_router_instances(router_modules)
