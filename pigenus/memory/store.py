from __future__ import annotations

from sqlalchemy.orm import Session

from pigenus.db.orm import MemoryItem


def remember(
    session: Session,
    *,
    namespace: str,
    key: str,
    value: str,
    importance: int = 50,
    metadata: dict | None = None,
) -> MemoryItem:
    item = MemoryItem(
        namespace=namespace,
        key=key,
        value=value,
        importance=importance,
        metadata_json=metadata or {},
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

