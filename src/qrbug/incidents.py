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

    def dump(self) -> str:
        return f'thing:{self.thing_id} fail:{self.failure_id} ip:{self.ip} comment:{repr(self.comment)}'

    def is_equal(self, other_thing_id, other_failure_id) -> bool:
        return self.thing_id == other_thing_id and self.failure_id == other_failure_id

    @classmethod
    def create(cls, thing_id: str, failure_id: str, ip: str, timestamp: int, comment: Optional[str] = None) -> "Incidents":
        """
        Factory method, creates a new incident and stores it within the incident instances
        """
        new_incident = Incidents(thing_id, failure_id, ip, timestamp, comment)
        cls.active.append(new_incident)
        return new_incident

    @classmethod
    def remove(cls, other_thing_id: str, other_failure_id: str) -> Optional["Incidents"]:
        """
        Deletes any given incident from the list of incidents
        """
        for current_failure in cls.active:
            if current_failure.is_equal(other_thing_id, other_failure_id):
                cls.active.remove(current_failure)
                cls.finished.append(current_failure)
                return current_failure
        return None

    def __class_getitem__(cls, incident_id: str) -> Optional["Incidents"]:
        if incident_id in cls.active:
            return cls.active[incident_id]
        elif incident_id in cls.finished:
            return cls.finished[incident_id]
        else:
            return None


def incident(thing_id: ThingId, failure_id: FailureId, ip: str, timestamp: int, comment: Optional[str] = None) -> "Incidents":
    return Incidents.create(thing_id, failure_id, ip, timestamp, comment)


def incident_del(thing_id: ThingId, failure_id: FailureId, ip: str, timestamp: int) -> Optional["Incidents"]:
    return Incidents.remove(thing_id, failure_id)
