# PIGENUS_PHASE_0_CORE_KERNEL_SPEC_v0.1.md

> Status: baunahe Spezifikation / Diskussionsentwurf  
> Datum: 2026-05-10  
> Bezug: `PIGENUS_BLUEPRINT_v1.2_SYSTEMFORM_INTEGRATED.md`  
> Ziel: Phase 0 so konkret machen, dass daraus direkt ein erster Codex-/Implementierungsauftrag entstehen kann.

---

## 0. Kurzfassung

Phase 0 baut **keinen Agenten**, **keinen Charakter**, **keine LLM-Magie** und **keine Evolution**.

Phase 0 baut den **Systemform Kernel**:

```text
MeaningObject
CellContract
ActorIdentity
Room
Event
AuditRecord
GovernanceDecision
ResourceGrant
```

Damit wird PiGenus nicht als wilde Agenten-App gestartet, sondern als kleine, prüfbare Runtime mit klaren Grenzen.

Der Kernauftrag lautet:

```text
Erst verfassungssichere Grundobjekte.
Dann Eventbus.
Dann Zellen.
Dann Memory.
Dann LLMs.
```

Das ist bewusst trocken. Genau deshalb ist es gut. Betonfundament ist selten sexy, aber ohne Fundament tanzt später das ganze Haus Polka. 😄

---

## 1. Phase-0-Ziele

### 1.1 Muss-Ziele

Phase 0 muss liefern:

1. Domain-Modelle für die Kernobjekte.
2. JSON-Serialisierung für alle Kernobjekte.
3. SQLite-Schema mit Storage-Abstraktion.
4. Contract Validator.
5. Guard Pipeline.
6. Einfacher `asyncio` Eventbus.
7. Meaning Store MVP.
8. Room Flow Rules MVP.
9. Audit-Logging.
10. CLI für Minimaltests.

### 1.2 Nicht-Ziele

Phase 0 baut ausdrücklich nicht:

- keine LLM-Provider,
- keine externe API,
- kein Dashboard,
- keine automatische Mutation,
- keine echten Finanzaktionen,
- keine produktiven Charaktere,
- keine Föderation,
- keine Blockchain,
- keine Multi-Node-Verteilung.

### 1.3 Erfolgskriterium

Phase 0 ist erfolgreich, wenn folgende Mini-Kette funktioniert:

```text
ActorIdentity anlegen
→ Room anlegen
→ CellContract anlegen
→ MeaningObject erzeugen
→ Event veröffentlichen
→ Guard Pipeline prüfen
→ AuditRecord schreiben
→ MeaningObject abrufen
```

---

## 2. Kernprinzipien

### Prinzip 1: Kein Event ohne Kontext

Jedes Event braucht:

```text
actor_id
room_id
event_type
created_at
```

Optional, aber für sicherheitsrelevante Events faktisch Pflicht:

```text
contract_id
payload_ref
decision_trace
```

### Prinzip 2: Keine Ausführung ohne Vertrag

Eine Zelle darf nur laufen, wenn:

```text
Actor aktiv
Contract aktiv
Room erlaubt
Capability erlaubt
Permission erlaubt
ResourceGrant ausreichend
Guard Pipeline nicht blockiert
```

### Prinzip 3: MeaningObject vor Memory

Memory speichert keine losen Texte als Wahrheit.

```text
Rohtext → MeaningObject → MemoryRecord
```

### Prinzip 4: Governance ist ausführbar

Governance ist keine PDF-Deko.

```text
GovernanceRule → GuardDecision → AuditRecord
```

### Prinzip 5: PiGenus bleibt lokal und klein

Für Phase 0 gilt:

```text
SQLite
asyncio
CLI
keine Cloud-Pflicht
```

---

## 3. Python-Zielstruktur

```text
pigenus/
  pyproject.toml
  README.md
  docs/
    PIGENUS_BLUEPRINT_v1.2_SYSTEMFORM_INTEGRATED.md
    PIGENUS_PHASE_0_CORE_KERNEL_SPEC_v0.1.md
  src/
    pigenus/
      __init__.py
      core/
        ids.py
        enums.py
        time.py
        errors.py
      identity/
        models.py
        registry.py
      rooms/
        models.py
        flow_rules.py
      contracts/
        models.py
        validator.py
        registry.py
      meaning/
        models.py
        store.py
        truth.py
      governance/
        models.py
        guards.py
        pipeline.py
        audit.py
      runtime/
        events.py
        eventbus.py
      resources/
        models.py
        grants.py
      storage/
        base.py
        sqlite.py
        migrations.py
      cli/
        main.py
  tests/
    test_models.py
    test_storage_sqlite.py
    test_contract_validator.py
    test_guard_pipeline.py
    test_eventbus.py
    test_room_flow_rules.py
    test_meaning_store.py
```

---

## 4. ID-Konventionen

PiGenus nutzt sprechende IDs mit Prefix.

| Objekt | Prefix | Beispiel |
|---|---|---|
| HumanIdentity | `human_` | `human_ronny` |
| CellType | `celltype_` | `celltype_risk_guard` |
| CellInstance | `cell_` | `cell_risk_guard_private_v1` |
| Organ | `organ_` | `organ_memory_local_v1` |
| Agent | `agent_` | `agent_pigenus_assistant_v1` |
| Character | `char_` | `char_ava_v1` |
| Room | `room_` | `room_private` |
| Contract | `contract_` | `contract_risk_guard_v1` |
| MeaningObject | `bo_` | `bo_01hx...` |
| Event | `evt_` | `evt_01hx...` |
| AuditRecord | `audit_` | `audit_01hx...` |
| GovernanceRule | `rule_` | `rule_private_export_block_v1` |
| ResourceGrant | `rg_` | `rg_memory_writer_v1` |

Regel:

```text
IDs sind stabil.
Namen sind änderbar.
Versionen sind explizit.
```

---

## 5. Enums

### 5.1 ActorType

```python
class ActorType(str, Enum):
    HUMAN = "human"
    CELL = "cell"
    ORGAN = "organ"
    AGENT = "agent"
    CHARACTER = "character"
    SYSTEM = "system"
```

### 5.2 ActorStatus

```python
class ActorStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    REVOKED = "revoked"
    FOSSIL = "fossil"
```

### 5.3 TruthStatus

```python
class TruthStatus(str, Enum):
    VERIFIED = "verified"
    BELIEVED = "believed"
    CONTESTED = "contested"
    DEPRECATED = "deprecated"
    SIMULATED = "simulated"
    UNSAFE = "unsafe"
    HISTORICAL = "historical"
```

### 5.4 Sensitivity

```python
class Sensitivity(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    PRIVATE = "private"
    FAMILY = "family"
    FINANCIAL = "financial"
    CHILD_RELATED = "child_related"
    SECRET = "secret"
```

### 5.5 ContractStatus

```python
class ContractStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    DEPRECATED = "deprecated"
```

### 5.6 GuardDecisionType

```python
class GuardDecisionType(str, Enum):
    ALLOW = "allow"
    WARN = "warn"
    BLOCK = "block"
    ESCALATE = "escalate"
    QUARANTINE = "quarantine"
    REVOKE = "revoke"
    ARCHIVE = "archive"
```

### 5.7 RoomProtectionLevel

```python
class RoomProtectionLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"
    ISOLATED = "isolated"
```

---

## 6. Domain-Modelle

Die Modelle können mit `pydantic` oder `dataclasses` umgesetzt werden. Empfehlung: **Pydantic v2**, weil Validierung und JSON-Schema später direkt nützlich werden.

### 6.1 ActorIdentity

```python
class ActorIdentity(BaseModel):
    id: str
    actor_type: ActorType
    name: str
    version: str | None = None
    parent_id: str | None = None
    status: ActorStatus = ActorStatus.DRAFT
    public_key: str | None = None
    reputation_id: str | None = None
    created_by: str | None = None
    created_at: datetime
```

Pflichtregel:

```text
active actor braucht created_at und actor_type.
revoked actor darf keine neuen Events erzeugen.
```

### 6.2 Room

```python
class Room(BaseModel):
    id: str
    name: str
    protection_level: RoomProtectionLevel
    default_policy_id: str | None = None
    description: str | None = None
    created_at: datetime
```

Standardräume:

```text
room_private
room_family
room_trading
room_developer
room_public
room_sandbox
```

### 6.3 MeaningObject

```python
class MeaningObject(BaseModel):
    id: str
    type: str
    content: dict[str, Any]
    source: str | None = None
    provenance: list[dict[str, Any]] = Field(default_factory=list)
    room_id: str
    truth_status: TruthStatus
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    sensitivity: Sensitivity
    revision: int = 1
    parent_ids: list[str] = Field(default_factory=list)
    valid_from: datetime | None = None
    valid_until: datetime | None = None
    created_by: str
    created_at: datetime
```

Regel:

```text
MeaningObject ohne room_id ist ungültig.
MeaningObject ohne truth_status ist ungültig.
MeaningObject mit sensitivity private/family/financial darf nicht direkt in public exportiert werden.
```

### 6.4 CellContract

```python
class CellContract(BaseModel):
    id: str
    actor_id: str
    version: str
    status: ContractStatus
    room_scope: list[str]
    capabilities: list[str]
    permissions: dict[str, Any]
    obligations: list[str]
    resource_limits: dict[str, Any]
    risk_profile: dict[str, Any]
    human_approval_required: list[str] = Field(default_factory=list)
    mutation_policy: dict[str, Any] = Field(default_factory=dict)
    governance_policy_id: str
    expires_at: datetime | None = None
    created_at: datetime
```

Regel:

```text
Contract ohne governance_policy_id ist ungültig.
Contract ohne room_scope ist ungültig.
Contract ohne permissions ist ungültig.
```

### 6.5 ResourceGrant

```python
class ResourceGrant(BaseModel):
    id: str
    actor_id: str
    room_id: str
    limits: dict[str, Any]
    granted_by: str
    expires_at: datetime | None = None
    created_at: datetime
```

MVP-Limits:

```text
cpu_ms_per_minute
memory_mb
storage_write_mb_per_day
token_budget_per_day
attention_slots_per_hour
max_events_per_minute
```

### 6.6 Event

```python
class Event(BaseModel):
    id: str
    event_type: str
    actor_id: str
    room_id: str
    contract_id: str | None = None
    payload_ref: str | None = None
    payload: dict[str, Any] | None = None
    decision_trace: list[str] = Field(default_factory=list)
    audit_required: bool = False
    created_at: datetime
```

Regel:

```text
security.* events brauchen audit_required=true.
external_* events brauchen contract_id.
```

### 6.7 GovernanceRule

```python
class GovernanceRule(BaseModel):
    id: str
    scope: dict[str, Any]
    condition: dict[str, Any]
    decision: GuardDecisionType
    audit_required: bool = True
    reason: str
    priority: int = 100
    active: bool = True
    created_at: datetime
```

### 6.8 GuardDecision

```python
class GuardDecision(BaseModel):
    decision: GuardDecisionType
    rule_id: str | None = None
    reason: str
    requires_human: bool = False
    audit_required: bool = True
```

### 6.9 AuditRecord

```python
class AuditRecord(BaseModel):
    id: str
    event_id: str
    actor_id: str
    room_id: str
    rule_id: str | None = None
    decision: GuardDecisionType
    reason: str | None = None
    created_at: datetime
```

---

## 7. SQLite-Schema MVP

### 7.1 Migration 0001

```sql
CREATE TABLE IF NOT EXISTS actors (
  id TEXT PRIMARY KEY,
  actor_type TEXT NOT NULL,
  name TEXT NOT NULL,
  version TEXT,
  parent_id TEXT,
  status TEXT NOT NULL,
  public_key TEXT,
  reputation_id TEXT,
  created_by TEXT,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS rooms (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  protection_level TEXT NOT NULL,
  default_policy_id TEXT,
  description TEXT,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS contracts (
  id TEXT PRIMARY KEY,
  actor_id TEXT NOT NULL,
  version TEXT NOT NULL,
  status TEXT NOT NULL,
  room_scope_json TEXT NOT NULL,
  capabilities_json TEXT NOT NULL,
  permissions_json TEXT NOT NULL,
  obligations_json TEXT NOT NULL,
  resource_limits_json TEXT NOT NULL,
  risk_profile_json TEXT NOT NULL,
  human_approval_required_json TEXT NOT NULL,
  mutation_policy_json TEXT NOT NULL,
  governance_policy_id TEXT NOT NULL,
  expires_at TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY(actor_id) REFERENCES actors(id)
);

CREATE TABLE IF NOT EXISTS resource_grants (
  id TEXT PRIMARY KEY,
  actor_id TEXT NOT NULL,
  room_id TEXT NOT NULL,
  limits_json TEXT NOT NULL,
  granted_by TEXT NOT NULL,
  expires_at TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY(actor_id) REFERENCES actors(id),
  FOREIGN KEY(room_id) REFERENCES rooms(id)
);

CREATE TABLE IF NOT EXISTS meaning_objects (
  id TEXT PRIMARY KEY,
  type TEXT NOT NULL,
  content_json TEXT NOT NULL,
  source TEXT,
  provenance_json TEXT NOT NULL,
  room_id TEXT NOT NULL,
  truth_status TEXT NOT NULL,
  confidence REAL,
  sensitivity TEXT NOT NULL,
  revision INTEGER NOT NULL,
  parent_ids_json TEXT NOT NULL,
  valid_from TEXT,
  valid_until TEXT,
  created_by TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(room_id) REFERENCES rooms(id),
  FOREIGN KEY(created_by) REFERENCES actors(id)
);

CREATE TABLE IF NOT EXISTS governance_rules (
  id TEXT PRIMARY KEY,
  scope_json TEXT NOT NULL,
  condition_json TEXT NOT NULL,
  decision TEXT NOT NULL,
  audit_required INTEGER NOT NULL,
  reason TEXT NOT NULL,
  priority INTEGER NOT NULL,
  active INTEGER NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS events (
  id TEXT PRIMARY KEY,
  event_type TEXT NOT NULL,
  actor_id TEXT NOT NULL,
  room_id TEXT NOT NULL,
  contract_id TEXT,
  payload_ref TEXT,
  payload_json TEXT,
  decision_trace_json TEXT NOT NULL,
  audit_required INTEGER NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(actor_id) REFERENCES actors(id),
  FOREIGN KEY(room_id) REFERENCES rooms(id),
  FOREIGN KEY(contract_id) REFERENCES contracts(id)
);

CREATE TABLE IF NOT EXISTS audits (
  id TEXT PRIMARY KEY,
  event_id TEXT NOT NULL,
  actor_id TEXT NOT NULL,
  room_id TEXT NOT NULL,
  rule_id TEXT,
  decision TEXT NOT NULL,
  reason TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY(event_id) REFERENCES events(id),
  FOREIGN KEY(actor_id) REFERENCES actors(id),
  FOREIGN KEY(room_id) REFERENCES rooms(id)
);
```

### 7.2 Indexe

```sql
CREATE INDEX IF NOT EXISTS idx_events_actor_id ON events(actor_id);
CREATE INDEX IF NOT EXISTS idx_events_room_id ON events(room_id);
CREATE INDEX IF NOT EXISTS idx_events_created_at ON events(created_at);

CREATE INDEX IF NOT EXISTS idx_meaning_room_id ON meaning_objects(room_id);
CREATE INDEX IF NOT EXISTS idx_meaning_truth_status ON meaning_objects(truth_status);
CREATE INDEX IF NOT EXISTS idx_meaning_created_by ON meaning_objects(created_by);

CREATE INDEX IF NOT EXISTS idx_audits_actor_id ON audits(actor_id);
CREATE INDEX IF NOT EXISTS idx_audits_created_at ON audits(created_at);
```

---

## 8. Storage-Abstraktion

### 8.1 Interface

```python
class StorageAdapter(Protocol):
    def init(self) -> None: ...
    def save_actor(self, actor: ActorIdentity) -> None: ...
    def get_actor(self, actor_id: str) -> ActorIdentity | None: ...
    def save_room(self, room: Room) -> None: ...
    def get_room(self, room_id: str) -> Room | None: ...
    def save_contract(self, contract: CellContract) -> None: ...
    def get_contract(self, contract_id: str) -> CellContract | None: ...
    def save_meaning_object(self, obj: MeaningObject) -> None: ...
    def get_meaning_object(self, obj_id: str) -> MeaningObject | None: ...
    def save_event(self, event: Event) -> None: ...
    def save_audit(self, audit: AuditRecord) -> None: ...
    def list_active_rules(self) -> list[GovernanceRule]: ...
```

### 8.2 Regel

```text
Domain-Code spricht nur mit StorageAdapter.
SQLiteAdapter ist austauschbar.
```

---

## 9. Contract Validator

### 9.1 Input

```text
actor_id
contract_id
room_id
capability
action
resource_request
```

### 9.2 Ablauf

```text
1. Actor laden.
2. Actor muss active sein.
3. Contract laden.
4. Contract muss active sein.
5. Contract darf nicht abgelaufen sein.
6. actor_id muss zum contract.actor_id passen.
7. room_id muss in contract.room_scope liegen.
8. capability muss in contract.capabilities liegen.
9. action muss durch contract.permissions erlaubt sein.
10. resource_request muss innerhalb contract.resource_limits liegen.
11. Falls action in human_approval_required liegt: ESCALATE.
12. Sonst ALLOW.
```

### 9.3 Rückgabe

```python
class ContractValidationResult(BaseModel):
    allowed: bool
    decision: GuardDecisionType
    reason: str
    requires_human: bool = False
```

### 9.4 Blockgründe

| Grund | Entscheidung |
|---|---|
| Actor fehlt | `BLOCK` |
| Actor revoked | `BLOCK` |
| Contract fehlt | `BLOCK` |
| Contract revoked | `BLOCK` |
| Room nicht erlaubt | `BLOCK` |
| Capability nicht erlaubt | `BLOCK` |
| Resource Limit überschritten | `BLOCK` |
| Human Approval nötig | `ESCALATE` |

---

## 10. Room Flow Rules

### 10.1 Matrix

| Von | Nach | Default |
|---|---|---|
| private | family | review |
| private | public | block |
| private | external | block |
| family | public | block |
| family | external | review |
| trading | public | block |
| trading | external | review |
| developer | sandbox | allow |
| sandbox | developer | review |
| sandbox | production | block |
| public | private | allow_read |
| public | family | review |

### 10.2 Algorithmus

```text
1. Prüfe source_room.
2. Prüfe target_room.
3. Prüfe sensitivity.
4. Falls private/family/financial/child_related und target public/external: BLOCK.
5. Falls sandbox → production: BLOCK.
6. Falls review nötig: ESCALATE.
7. Sonst ALLOW.
```

### 10.3 Redaction-Regel

```text
Redaction kann block nicht automatisch in allow verwandeln.
Redaction erzeugt review.
Human/Governance entscheidet danach.
```

---

## 11. Guard Pipeline

### 11.1 Pipeline-Reihenfolge

```text
IdentityGuard
→ ContractGuard
→ RoomGuard
→ ResourceGuard
→ PrivacyGuard
→ GovernanceRuleGuard
→ AuditGuard
```

### 11.2 Entscheidungslogik

```text
BLOCK gewinnt immer.
QUARANTINE gewinnt über BLOCK, wenn Isolation nötig ist.
ESCALATE stoppt Ausführung bis Freigabe.
WARN erlaubt Ausführung, schreibt aber Audit.
ALLOW erlaubt Ausführung.
```

### 11.3 Minimalcode-Skizze

```python
async def run_guard_pipeline(event: Event, storage: StorageAdapter) -> list[GuardDecision]:
    decisions = []

    for guard in [
        IdentityGuard(storage),
        ContractGuard(storage),
        RoomGuard(storage),
        ResourceGuard(storage),
        PrivacyGuard(storage),
        GovernanceRuleGuard(storage),
    ]:
        decision = await guard.check(event)
        decisions.append(decision)
        if decision.decision in {
            GuardDecisionType.BLOCK,
            GuardDecisionType.ESCALATE,
            GuardDecisionType.QUARANTINE,
            GuardDecisionType.REVOKE,
        }:
            break

    return decisions
```

---

## 12. Eventbus MVP

### 12.1 Aufgaben

Der Eventbus soll:

1. Events entgegennehmen.
2. Events validieren.
3. Guard Pipeline ausführen.
4. Events persistieren.
5. AuditRecords schreiben.
6. Handler aufrufen, wenn erlaubt.

### 12.2 Minimal-API

```python
class EventBus:
    def __init__(self, storage: StorageAdapter): ...
    def subscribe(self, event_type: str, handler: Callable[[Event], Awaitable[None]]) -> None: ...
    async def publish(self, event: Event) -> list[GuardDecision]: ...
```

### 12.3 Publish-Ablauf

```text
1. Event formal validieren.
2. Guard Pipeline ausführen.
3. Decision Trace in Event schreiben.
4. Event speichern.
5. AuditRecords speichern.
6. Wenn BLOCK/ESCALATE/QUARANTINE: keine Handler-Ausführung.
7. Wenn ALLOW/WARN: passende Handler ausführen.
```

---

## 13. Meaning Store MVP

### 13.1 Funktionen

```python
class MeaningStore:
    def create(self, obj: MeaningObject) -> MeaningObject: ...
    def get(self, obj_id: str) -> MeaningObject | None: ...
    def revise(self, obj_id: str, patch: dict[str, Any], actor_id: str) -> MeaningObject: ...
    def deprecate(self, obj_id: str, actor_id: str, reason: str) -> MeaningObject: ...
    def list_by_room(self, room_id: str) -> list[MeaningObject]: ...
    def list_by_truth_status(self, status: TruthStatus) -> list[MeaningObject]: ...
```

### 13.2 Revision-Regel

```text
Revision überschreibt nicht.
Revision erzeugt neues MeaningObject mit parent_ids=[alter_id].
Altes Objekt wird deprecated oder historical.
```

### 13.3 Wahrheit-Regel

```text
contested darf nicht automatisch als Entscheidungsgrundlage genutzt werden.
unsafe darf keine Aktion auslösen.
simulated darf nie als reale Erinnerung gespeichert werden, ohne Statusbeibehaltung.
```

---

## 14. CLI MVP

### 14.1 Commands

```bash
pigenus init
pigenus rooms list
pigenus actors create --id cell_demo_v1 --type cell --name DemoCell
pigenus contracts add ./examples/contract_demo.yaml
pigenus meaning add ./examples/meaning_object.json
pigenus events publish ./examples/event_demo.json
pigenus audits tail
pigenus kernel health
```

### 14.2 CLI-Regel

```text
CLI ist Testwerkzeug.
CLI ist nicht Governance-Ersatz.
```

---

## 15. Beispiele

### 15.1 Demo Actor

```json
{
  "id": "cell_demo_private_v1",
  "actor_type": "cell",
  "name": "Demo Private Cell",
  "version": "1.0",
  "status": "active",
  "created_at": "2026-05-10T10:00:00+02:00"
}
```

### 15.2 Demo Room

```json
{
  "id": "room_private",
  "name": "Private",
  "protection_level": "very_high",
  "default_policy_id": "rule_private_export_block_v1",
  "created_at": "2026-05-10T10:00:00+02:00"
}
```

### 15.3 Demo Contract

```yaml
id: contract_demo_private_v1
actor_id: cell_demo_private_v1
version: "1.0"
status: active
room_scope:
  - room_private
capabilities:
  - create_meaning_object
  - emit_event
permissions:
  read:
    - MeaningObject
  write:
    - MeaningObject
    - Event
obligations:
  - log_every_event
resource_limits:
  cpu_ms_per_minute: 5000
  memory_mb: 128
  max_events_per_minute: 30
risk_profile:
  class: low
human_approval_required:
  - external_export
mutation_policy:
  allowed: false
governance_policy_id: rule_private_export_block_v1
expires_at: null
created_at: "2026-05-10T10:00:00+02:00"
```

### 15.4 Demo MeaningObject

```json
{
  "id": "bo_demo_preference_001",
  "type": "UserPreference",
  "content": {
    "subject": "ronny",
    "preference": "direkte Antworten mit Plausibilitätscheck"
  },
  "source": "conversation",
  "provenance": [],
  "room_id": "room_private",
  "truth_status": "believed",
  "confidence": 0.82,
  "sensitivity": "private",
  "revision": 1,
  "parent_ids": [],
  "valid_from": "2026-05-10T10:00:00+02:00",
  "valid_until": null,
  "created_by": "cell_demo_private_v1",
  "created_at": "2026-05-10T10:00:00+02:00"
}
```

---

## 16. Tests

### 16.1 Model Tests

Muss prüfen:

- Enums validieren.
- MeaningObject ohne room_id schlägt fehl.
- Contract ohne governance_policy_id schlägt fehl.
- Confidence außerhalb `0..1` schlägt fehl.

### 16.2 Storage Tests

Muss prüfen:

- SQLite init erzeugt Tabellen.
- Actor speichern/laden.
- Room speichern/laden.
- Contract speichern/laden.
- MeaningObject speichern/laden.
- Event + Audit speichern.

### 16.3 Contract Validator Tests

Muss prüfen:

- active contract erlaubt passende capability.
- revoked contract blockiert.
- falscher room blockiert.
- fehlende capability blockiert.
- human approval erzeugt ESCALATE.

### 16.4 Room Flow Tests

Muss prüfen:

- private → public block.
- family → public block.
- trading → public block.
- sandbox → production block.
- public → private allow_read.

### 16.5 Eventbus Tests

Muss prüfen:

- publish speichert Event.
- BLOCK verhindert Handler.
- ALLOW ruft Handler.
- WARN ruft Handler und schreibt Audit.
- ESCALATE ruft keinen Handler.

---

## 17. Definition of Done

Phase 0 ist fertig, wenn:

```text
[ ] alle Kernmodelle existieren
[ ] alle Modelle JSON-serialisierbar sind
[ ] SQLiteAdapter funktioniert
[ ] Migration 0001 läuft
[ ] Contract Validator funktioniert
[ ] Guard Pipeline funktioniert
[ ] Eventbus MVP funktioniert
[ ] Meaning Store MVP funktioniert
[ ] Room Flow Rules funktionieren
[ ] CLI init/list/add/publish/tail funktioniert
[ ] Tests laufen grün
[ ] README erklärt lokalen Start
```

---

## 18. Codex-Bauprompt für Phase 0

```text
Du bist Codex und implementierst PiGenus Phase 0: Core Kernel.

Ziel:
Baue eine kleine Python-Library namens pigenus, die die GENUS-Systemform-Primitives als lauffähigen lokalen MVP-Kernel implementiert.

Keine LLMs.
Keine externe API.
Keine automatische Mutation.
Keine Cloud.

Implementiere:
1. Kernmodelle:
   - ActorIdentity
   - Room
   - MeaningObject
   - CellContract
   - ResourceGrant
   - Event
   - GovernanceRule
   - GuardDecision
   - AuditRecord

2. Enums:
   - ActorType
   - ActorStatus
   - TruthStatus
   - Sensitivity
   - ContractStatus
   - GuardDecisionType
   - RoomProtectionLevel

3. Storage:
   - StorageAdapter Interface
   - SQLiteAdapter
   - Migration 0001 für actors, rooms, contracts, resource_grants, meaning_objects, governance_rules, events, audits

4. Contract Validator:
   - prüft actor active
   - contract active
   - contract nicht abgelaufen
   - actor_id passt
   - room erlaubt
   - capability erlaubt
   - permission erlaubt
   - resources innerhalb limits
   - human approval erzeugt ESCALATE

5. Guard Pipeline:
   - IdentityGuard
   - ContractGuard
   - RoomGuard
   - ResourceGuard
   - PrivacyGuard
   - GovernanceRuleGuard
   - Audit-Erzeugung für jede relevante Entscheidung

6. Eventbus:
   - asyncio EventBus
   - subscribe(event_type, handler)
   - publish(event)
   - guard pipeline vor handler execution
   - event persistence
   - audit persistence

7. Meaning Store:
   - create
   - get
   - revise
   - deprecate
   - list_by_room
   - list_by_truth_status

8. CLI:
   - pigenus init
   - pigenus rooms list
   - pigenus actors create
   - pigenus contracts add
   - pigenus meaning add
   - pigenus events publish
   - pigenus audits tail
   - pigenus kernel health

Technische Vorgaben:
- Python 3.11+
- Pydantic v2 bevorzugt
- SQLite standard library oder aiosqlite
- pytest
- keine direkten SQLite-Aufrufe im Domain-Code
- alle JSON-Felder robust serialisieren/deserialisieren

Tests:
Schreibe Tests für Modelle, SQLite Storage, Contract Validator, Guard Pipeline, Eventbus, Meaning Store und Room Flow Rules.

Akzeptanz:
Alle Tests grün.
Ein Demo-Event von einer Demo-Zelle im privaten Raum kann veröffentlicht werden.
Bei private → public wird BLOCK erzeugt und ein AuditRecord geschrieben.
```

---

## 19. Kurzurteil

**Plausibel:** ja. Phase 0 ist klein genug, um real gebaut zu werden, und groß genug, um die GENUS-Systemform sauber zu tragen.

**Konsistent:** ja. Sie setzt v1.2 direkt um: Bedeutungsobjekte, Zellverträge, Identität, Räume, Governance, Eventbus und Audit werden als Kernel-Primitives behandelt.

**Vollständig:** als Phase-0-Spezifikation solide. Noch nicht vollständig für Reputation, Föderation, Charakterpsychologie oder Evolution. Diese Themen gehören in Phase 1+ oder Blueprint v1.3/v1.4.
