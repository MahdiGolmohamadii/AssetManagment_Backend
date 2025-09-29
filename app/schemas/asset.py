from pydantic import BaseModel


class AssetVersionNew(BaseModel):
    version_number: float
    file_path: str
    asset_id: int

class AssetVersionInDb(AssetVersionNew):
    id: int

class AssetNew(BaseModel):
    name: str

class AssetInDb(BaseModel):
    id: int
    name: str
    version: list[AssetVersionInDb]



    