"""Base repository interfaces and implementations."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Any, Dict
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

# Generic type for model
T = TypeVar('T')


class BaseRepositoryInterface(ABC, Generic[T]):
    """Abstract base repository interface defining common CRUD operations."""
    
    @abstractmethod
    def create(self, entity: T) -> T:
        """Create a new entity."""
        pass
    
    @abstractmethod
    def get_by_id(self, entity_id: UUID) -> Optional[T]:
        """Get entity by ID."""
        pass
    
    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all entities with pagination."""
        pass
    
    @abstractmethod
    def update(self, entity_id: UUID, update_data: Dict[str, Any]) -> Optional[T]:
        """Update entity by ID."""
        pass
    
    @abstractmethod
    def delete(self, entity_id: UUID) -> bool:
        """Delete entity by ID."""
        pass
    
    @abstractmethod
    def exists(self, entity_id: UUID) -> bool:
        """Check if entity exists."""
        pass


class BaseRepository(BaseRepositoryInterface[T]):
    """Base repository implementation with common database operations."""
    
    def __init__(self, db: Session, model_class: type):
        """Initialize repository with database session and model class.
        
        Args:
            db: SQLAlchemy database session
            model_class: The SQLAlchemy model class
        """
        self.db = db
        self.model_class = model_class
    
    def create(self, entity_data: Dict[str, Any]) -> T:
        """Create a new entity from dictionary data."""
        entity = self.model_class(**entity_data)
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity
    
    def get_by_id(self, entity_id: UUID) -> Optional[T]:
        """Get entity by ID."""
        return self.db.query(self.model_class).filter(
            self.model_class.id == entity_id
        ).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all entities with pagination."""
        return self.db.query(self.model_class).offset(skip).limit(limit).all()
    
    def update(self, entity_id: UUID, update_data: Dict[str, Any]) -> Optional[T]:
        """Update entity by ID."""
        entity = self.get_by_id(entity_id)
        if not entity:
            return None
        
        for key, value in update_data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)
        
        self.db.commit()
        self.db.refresh(entity)
        return entity
    
    def delete(self, entity_id: UUID) -> bool:
        """Delete entity by ID."""
        entity = self.get_by_id(entity_id)
        if not entity:
            return False
        
        self.db.delete(entity)
        self.db.commit()
        return True
    
    def exists(self, entity_id: UUID) -> bool:
        """Check if entity exists."""
        return self.db.query(self.model_class).filter(
            self.model_class.id == entity_id
        ).first() is not None
    
    def get_by_field(self, field: str, value: Any) -> Optional[T]:
        """Get entity by specific field."""
        return self.db.query(self.model_class).filter(
            getattr(self.model_class, field) == value
        ).first()
    
    def get_by_fields(self, filters: Dict[str, Any]) -> Optional[T]:
        """Get entity by multiple fields."""
        query = self.db.query(self.model_class)
        for field, value in filters.items():
            if hasattr(self.model_class, field):
                query = query.filter(getattr(self.model_class, field) == value)
        return query.first()
    
    def get_many_by_field(self, field: str, value: Any, skip: int = 0, limit: int = 100) -> List[T]:
        """Get multiple entities by field."""
        return self.db.query(self.model_class).filter(
            getattr(self.model_class, field) == value
        ).offset(skip).limit(limit).all()
    
    def count(self) -> int:
        """Count total entities."""
        return self.db.query(self.model_class).count()
    
    def count_by_field(self, field: str, value: Any) -> int:
        """Count entities by field."""
        return self.db.query(self.model_class).filter(
            getattr(self.model_class, field) == value
        ).count()