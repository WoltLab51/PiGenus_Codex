from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from pigenus.db.orm import EventActorType, MemoryItem
from pigenus.services.audit import audit


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
    session.flush()
    audit(
        session,
        action="memory.created",
        actor_type=EventActorType.admin,
        actor_id="admin",
        target_type="memory_item",
        target_id=str(item.id),
        details={"namespace": namespace, "key": key, "importance": importance},
    )
    session.commit()
    session.refresh(item)
    return item


def list_memory(
    session: Session,
    *,
    namespace: str | None = None,
    query: str | None = None,
    limit: int = 100,
) -> list[MemoryItem]:
    statement = select(MemoryItem)
    if namespace:
        statement = statement.where(MemoryItem.namespace == namespace)
    if query:
        pattern = f"%{query}%"
        statement = statement.where(MemoryItem.value.like(pattern) | MemoryItem.key.like(pattern))
    statement = statement.order_by(MemoryItem.importance.desc(), MemoryItem.updated_at.desc()).limit(limit)
    return list(session.scalars(statement).all())


def update_memory(
    session: Session,
    *,
    item_id: int,
    value: str | None,
    importance: int | None,
    metadata: dict | None,
) -> MemoryItem:
    item = session.get(MemoryItem, item_id)
    if item is None:
        raise LookupError("memory item not found")
    if value is not None:
        item.value = value
    if importance is not None:
        item.importance = importance
    if metadata is not None:
        item.metadata_json = metadata
    audit(
        session,
        action="memory.updated",
        actor_type=EventActorType.admin,
        actor_id="admin",
        target_type="memory_item",
        target_id=str(item.id),
        details={"namespace": item.namespace, "key": item.key},
    )
    session.commit()
    session.refresh(item)
    return item
