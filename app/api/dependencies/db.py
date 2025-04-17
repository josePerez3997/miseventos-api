from typing import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db

def get_database(db: Session = Depends(get_db)) -> Generator[Session, None, None]:
    """
    Dependency for getting a database session
    """
    return db