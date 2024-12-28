from pydantic import BaseModel


# Models
class SearchResponse(BaseModel):
    table_name: str
    column_name: str
    content: str
    content_rowid: int
