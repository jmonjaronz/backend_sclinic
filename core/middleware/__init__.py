#core/middleware/__init__.py
from .tenant import MultiDomainMiddleware

__all__ = ['MultiDomainMiddleware']
