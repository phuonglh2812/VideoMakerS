from fastapi import APIRouter

class BaseWorkflow:
    """Base class cho tất cả workflow"""
    def __init__(self):
        self.router = None
        self.service = None
        
    def get_router(self):
        """Return FastAPI router của workflow"""
        if not self.router:
            raise NotImplementedError("Router must be implemented")
        return self.router

class BaseService:
    """Base class cho business logic"""
    pass

class BaseRouter:
    """Base class cho routing logic"""
    def __init__(self):
        self.router = APIRouter()
        self.init_routes()
    
    def init_routes(self):
        """Initialize routes - must be implemented by subclasses"""
        raise NotImplementedError
