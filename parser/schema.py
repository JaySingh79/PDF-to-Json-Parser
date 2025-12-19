from pydantic import BaseModel
from typing import List, Dict, Any

class TableRow(BaseModel):
    data: Dict[str, Any]
    confidence: float

class Table(BaseModel):
    table_id: str
    source: str
    confidence: float
    rows: List[TableRow]

class Section(BaseModel):
    section_id: str
    title: str
    content_type: str
    tables: List[Table] = []

class Page(BaseModel):
    page_number: int
    sections: List[Section]

class Document(BaseModel):
    document_metadata: Dict[str, Any]
    pages: List[Page]
