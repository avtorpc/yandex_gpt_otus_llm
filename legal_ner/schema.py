"""Pydantic models for extracted facts and saved annotations."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


NonEmptyText = Annotated[str, Field(min_length=1)]
INN = Annotated[str, Field(pattern=r"^(?:[0-9]{10}|[0-9]{12})$")]
# Preserve a digit string as printed in the source, even if its length is unusual.
KPP = Annotated[str, Field(pattern=r"^[0-9]+$")]


class SchemaModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Party(SchemaModel):
    name: NonEmptyText | None
    role: NonEmptyText
    inn: INN | None
    kpp: KPP | None
    evidence: NonEmptyText


class DateEntry(SchemaModel):
    kind: NonEmptyText
    date: NonEmptyText | None
    evidence: NonEmptyText


class Amount(SchemaModel):
    amount: NonEmptyText | None
    kind: NonEmptyText
    evidence: NonEmptyText


class Deadline(SchemaModel):
    kind: NonEmptyText
    value: int | None
    unit: NonEmptyText | None
    start_event: NonEmptyText | None
    due_date: NonEmptyText | None
    evidence: NonEmptyText


class Extraction(SchemaModel):
    """Facts that the model extracts from the text of a single act."""

    case_number: NonEmptyText | None
    act_type: NonEmptyText | None
    parties: list[Party]
    dates: list[DateEntry]
    amounts: list[Amount]
    deadlines: list[Deadline]


class AnnotatedDocument(Extraction):
    """Saved record with an identifier obtained from the source filename."""

    document_id: NonEmptyText
