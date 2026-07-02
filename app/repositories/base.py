from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Base repository providing common CRUD operations.
    """

    def __init__(
        self,
        db: Session,
        model: type[ModelType],
    ) -> None:
        self.db = db
        self.model = model

    def create(
        self,
        entity: ModelType,
    ) -> ModelType:
        """
        Persist a new entity.
        """

        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)

        return entity

    def get_by_id(
        self,
        entity_id: int,
    ) -> ModelType | None:
        """
        Retrieve an entity by its primary key.
        """

        statement = select(self.model).where(
            self.model.id == entity_id
        )

        result = self.db.execute(statement)

        return result.scalar_one_or_none()

    def update(
        self,
        entity: ModelType,
    ) -> ModelType:
        """
        Persist changes made to an existing entity.
        """

        self.db.commit()
        self.db.refresh(entity)

        return entity

    def delete(
        self,
        entity: ModelType,
    ) -> None:
        """
        Delete an entity.
        """

        self.db.delete(entity)
        self.db.commit()