import re
from typing import Any

from sqlalchemy.ext.declarative import declared_attr

from app.db.base import BaseModel

class CustomBase(BaseModel):
    __name__: str
    
    @declared_attr
    def __tablename__(cls) -> str:
        name = re.sub('(?<!^)(?=[A-Z])', '_', cls.__name__).lower()
        return name