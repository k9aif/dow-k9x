from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class DiagramSpec(BaseModel):
    kind: str
    source: str = ""
    caption: str = ""
    figure_number: int = 0
    png_bytes: Optional[bytes] = None

    class Config:
        arbitrary_types_allowed = True


class IcdSection(BaseModel):
    id: str
    level: int = 1
    title: str
    body: str = ""
    diagrams: list[DiagramSpec] = Field(default_factory=list)


class IcdMetadata(BaseModel):
    program_name: str = ""
    acat_level: str = ""
    validation_authority: str = ""
    approval_authority: str = ""
    milestone_authority: str = ""
    designation: str = ""
    prepared_for: str = ""
    date: str = ""
    version: str = "1.0"
    classification: str = "UNCLASSIFIED"


class IcdContent(BaseModel):
    metadata: IcdMetadata = Field(default_factory=IcdMetadata)
    executive_summary: str = ""
    sections: list[IcdSection] = Field(default_factory=list)
    acronyms: dict[str, str] = Field(default_factory=dict)
    glossary: dict[str, str] = Field(default_factory=dict)
    references: list[str] = Field(default_factory=list)
