from pydantic import BaseModel, ConfigDict
from datetime import datetime
from enum import Enum

class AssetStatus(str, Enum):
    InProgress = "InProgress"
    ReadyForReview = "ReadyForReview"
    NeedEdit = "NeedEdit"
    Published = "Published"

class AssetType(str, Enum):
    texture = "texture"
    mode = "model"
    rig = "rig"
    animaton = "animation"


#ASSET VERSION
class AssetVersionNew(BaseModel):
    version_number: int
    file_path: str
    status: AssetStatus = AssetStatus.InProgress
    

class AssetVersionInDb(AssetVersionNew):
    model_config = ConfigDict(from_attributes=True)

    id: int
    asset_id: int
    status : AssetStatus

class AssetVersionOut(AssetVersionNew):
    model_config = ConfigDict(from_attributes=True)
    id: int
    asset_id: int

class AssetVersionUpdate(BaseModel):
    version_number: int | None = None
    file_path: str | None = None
    status: AssetStatus | None = None
    


#ASSETS

class AssetNew(BaseModel):
    name: str
    description: str
    asset_type: AssetType

class AssetInDb(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    description : str
    asset_type: AssetType
    created_at : datetime
    last_update: datetime
    versions: list[AssetVersionInDb] | None

class AssetOut(AssetNew):
    model_config = ConfigDict(from_attributes=True)

    id: int
    versions: list[AssetVersionInDb] | None


class AssetUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    asset_type: AssetType | None = None

class AssetSearch(BaseModel):
    id: int | None = None
    name: str | None = None
    asset_type: AssetType | None = None
    limit: int = 10
    offset: int = 0
