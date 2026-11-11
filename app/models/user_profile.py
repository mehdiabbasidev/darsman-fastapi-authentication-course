from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models import User

class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    full_name: Mapped[str] = mapped_column(String(150))
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    bio: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    user: Mapped["User"] = relationship(back_populates="profile")


    def to_dict(self) -> dict:
        created_at: str | None = None
        if self.created_at:
            created_at = self.created_at.isoformat()

        return {
            "user_id": self.user_id,
            "full_name": self.full_name,
            "avatar_url": self.avatar_url,
            "bio": self.bio,
            "created_at": created_at,
        }
