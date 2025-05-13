from typing import Optional

from qrbug.failure import FailureId
from qrbug.thing import ThingId


class Incidents:
    active: list["Incidents"] = []
    finished: list["Incidents"] = []

    def __init__(self, thing_id: str, failure_id: str, ip: str, timestamp: int, comment: Optional[str] = None):
        self.thing_id = thing_id
        self.failure_id = failure_id
        self.ip = ip
        self.timestamp = timestamp
        self.comment = comment

    def is_equal(self, other_thing_id, other_failure_id) -> bool:
        return self.thing_id == other_thing_id and self.failure_id == other_failure_id

    @classmethod
    def create(cls, thing_id: str, failure_id: str, ip: str, timestamp: int, comment: Optional[str] = None) -> None:
        """
        Factory method, creates a new incident and stores it within the incident instances
        """
        cls.active.append(Incidents(thing_id, failure_id, ip, timestamp, comment))

    @classmethod
    def remove(cls, other_thing_id, other_failure_id) -> None:
        """
        Deletes any given incident from the list of incidents
        """
        for current_failure in cls.active:
            if current_failure.is_equal(other_thing_id, other_failure_id):
                cls.active.remove(current_failure)
                cls.finished.append(current_failure)


def incident(thing_id: ThingId, failure_id: FailureId, ip: str, timestamp: int, comment: Optional[str] = None) -> None:
    Incidents.create(thing_id, failure_id, ip, timestamp, comment)


def incident_del(thing_id: ThingId, failure_id: FailureId, ip: str, timestamp: int) -> None:
    Incidents.remove(thing_id, failure_id)
