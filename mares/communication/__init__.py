"""Inter-agent communication: message queue, schemas, event bus."""

from mares.communication.event_bus import EventBus
from mares.communication.message import Message
from mares.communication.message_queue import MessageQueue

__all__ = [
    "Message",
    "MessageQueue",
    "EventBus",
]
