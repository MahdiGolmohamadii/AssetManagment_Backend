from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base




class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column()
    created_at :  Mapped[datetime] = mapped_column(default=datetime.now)
    last_update: Mapped[datetime] = mapped_column(default=datetime.now, onupdate=datetime.now)

    versions: Mapped[list["AssetVersion"]] = relationship(back_populates="parent_asset", cascade="all, delete-orphan")


class AssetVersion(Base):
    __tablename__ = "asset_versions"

    id: Mapped[int] = mapped_column(primary_key=True)
    version_number: Mapped[int] = mapped_column(nullable=False)
    file_path : Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    last_update: Mapped[datetime] = mapped_column(default=datetime.now, onupdate=datetime.now)

    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id", ondelete='CASCADE'))
    parent_asset: Mapped["Asset"] = relationship(back_populates="versions")
    