from typing import List

from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from .base import Base
from .climber import Climber


class Team(Base):

    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    emoji: Mapped[str] = mapped_column(String(5))
    climbers: Mapped[List["Climber"]] = relationship()

    def __repr__(self) -> str:
        return f"Climber(id={self.id!r}, name={self.name!r})"
