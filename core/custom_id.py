from sqlalchemy.orm import Session
from api.user.models import TBL_ID_COUNTER

def generate_prefixed_id(db: Session, model, prefix: str) -> str:
    """
    Generate an ID like PRO0000001, CAT0000001, etc.

    :param db: SQLAlchemy session
    :param model: SQLAlchemy model class (unused here, but kept for consistency)
    :param prefix: Short uppercase prefix, e.g. "PRO", "CAT"
    :return: Formatted ID string
    """
    counter = (
        db.query(TBL_ID_COUNTER)
        .filter_by(prefix=prefix)
        .with_for_update()
        .first()
    )

    if counter:
        counter.sequence += 1
    else:
        counter = TBL_ID_COUNTER(
            prefix=prefix,
            sequence=1
        )
        db.add(counter)
        db.flush()

    new_sequence = str(counter.sequence).zfill(7)  # 7 digits → PRO0000001

    return f"{prefix}{new_sequence}"