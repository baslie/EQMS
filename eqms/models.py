from sqlmodel import SQLModel, Field, create_engine
from datetime import datetime


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str
    password_hash: str
    role: str = 'inspector'


class Building(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str


class Entrance(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    building_id: int | None = Field(default=None, foreign_key='building.id')


class Elevator(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    entrance_id: int | None = Field(default=None, foreign_key='entrance.id')


class InspectionTemplate(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: str | None = None


class Inspection(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    elevator_id: int | None = Field(default=None, foreign_key='elevator.id')
    user_id: int | None = Field(default=None, foreign_key='user.id')
    created_at: datetime = Field(default_factory=datetime.utcnow)


class InspectionItem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    inspection_id: int | None = Field(default=None, foreign_key='inspection.id')
    template_id: int | None = Field(default=None, foreign_key='inspectiontemplate.id')
    score: int
    comment: str | None = None


class Photo(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    inspection_item_id: int | None = Field(default=None, foreign_key='inspectionitem.id')
    path: str

