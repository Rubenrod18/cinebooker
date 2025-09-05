import importlib
import logging

logger = logging.getLogger(__name__)


def get_attr_from_module(module: str, attr: str) -> any:
    """Get attribute from a module.

    Parameters
    ----------
    module : str
        Module absolute path.
    attr : str
        Module's attribute. It could be any kind of variable belongs
        to module.

    Examples
    --------
    >>> module_path = 'app.routes.base'
    >>> module_attr = 'router'
    >>> get_attr_from_module(module_path, module_attr)

    Raises
    ------
    ImportError
        Module doesn't exist.
    AttributeError
        Attribute doesn't exist in module.

    """
    m = importlib.import_module(module)
    return getattr(m, attr)


def exists_attr_in_module(module: str, attr: str) -> bool:
    """Check if an attribute exists in a module.

    Parameters
    ----------
    module : str
        Module absolute path.
    attr : str
        Module's attribute. It could be any kind of variable belongs
        to module.

    Returns
    -------
    bool
        True if exists, otherwise False.

    Example
    -------
    >>> module_path = 'app.routes.base'
    >>> module_attr = 'router'
    >>> exists_attr_in_module(module_path, module_attr)
    True

    """
    exists = False
    try:
        attr = get_attr_from_module(module, attr)
        if attr:
            exists = True
    except (ImportError, AttributeError) as e:
        logger.warning(e)
        exists = False

    return exists
