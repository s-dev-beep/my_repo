"""Phone-Centric Identity Graph.

STEP 17: Core identity management system.

Append-only, phone-anchored agent identity tracking.
"""

from src.identity.graph_resolver import IdentityGraphResolver
from src.identity.phone_identity import PhoneIdentityManager
from src.identity.agent_profile import AgentProfileManager
from src.identity.office_entity import OfficeEntityManager
from src.identity.history_writer import HistoryWriter
from src.identity.evidence_store import EvidenceStore

__all__ = [
    "IdentityGraphResolver",
    "PhoneIdentityManager",
    "AgentProfileManager",
    "OfficeEntityManager",
    "HistoryWriter",
    "EvidenceStore",
]
