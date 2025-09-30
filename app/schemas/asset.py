from pydantic import BaseModel, ConfigDict
from datetime import datetime

#ASSET VERSION

class AssetVersionNew(BaseModel):
    version_number: int
    file_path: str
    

class AssetVersionInDb(AssetVersionNew):
    model_config = ConfigDict(from_attributes=True)

    id: int
    asset_id: int

class AssetVersionOut(AssetVersionNew):
    model_config = ConfigDict(from_attributes=True)

    id: int
    asset_id: int



#ASSETS

class AssetNew(BaseModel):
    name: str
    description: str

class AssetInDb(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    description : str
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

    