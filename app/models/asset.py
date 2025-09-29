from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    versions: Mapped[list["AssetVersion"]] = relationship(back_populates="parent_asset")


class AssetVersion(Base):
    __tablename__ = "asset_versions"

    id: Mapped[int] = mapped_column(primary_key=True)
    version_number: Mapped[float] = mapped_column(nullable=False)
    file_path : Mapped[str] = mapped_column(nullable=False)

    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"))
    parent_asset: Mapped["Asset"] = relationship(back_populates="versions")
    