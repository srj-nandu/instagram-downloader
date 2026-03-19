from pydantic import BaseModel, Field


class DownloadPostRequest(BaseModel):
    url: str = Field(min_length=1)


class DownloadStoriesRequest(BaseModel):
    profile_url: str = Field(min_length=1)
