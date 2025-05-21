from typing import Optional
import re

from qrbug.failure import FailureId, Failure
from qrbug.thing import ThingId, Thing


class Incidents:
    active: list["Incidents"] = []
    finished: list["Incidents"] = []

    def __init__(self, thing_id: str, failure_id: str, ip: str, timestamp: int, comment: Optional[str] = None, login: str = ''):
        self.thing_id = thing_id
        self.failure_id = failure_id
        self.ip = ip
        self.timestamp = timestamp
        self.comment = comment
        self.login = login

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

    @classmethod
    def filter(
            cls, thing_id: str = None, failure_id: str = None, ip: str = None, login: str = None,
            timestamp_min: int = 0, timestamp_max: int = None, comment: str = None
    ) -> tuple[list["Incidents"], list["Incidents"]]:
        """
        Returns the list of incidents matching the given criteria
        :param thing_id: The thing_id of the incident
        :param failure_id: The failure_id of the incident
        :param ip: The ip of the incident
        :param login: The login of the incident
        :param timestamp_min: The minimum timestamp of the incident
        :param timestamp_max: The maximum timestamp of the incident
        :param comment: A regex matching the given comment
        :return: A tuple of the incidents matching the given criteria ;
            first element is active incidents, second element is finished incidents
        """
        def condition_filter(incident) -> bool:
            if thing_id is not None and thing_id != incident.thing_id:
                return False
            if failure_id is not None and failure_id != incident.failure_id:
                return False
            if ip is not None and ip != incident.ip:
                return False
            if login is not None and login != incident.login:
                return False
            if incident.timestamp < timestamp_min:
                return False
            if timestamp_max is not None and incident.timestamp > timestamp_max:
                return False
            if comment is not None and re.match(comment, incident.comment) is None:
                return False
            return True
        return list(filter(condition_filter, cls.active)), list(filter(condition_filter, cls.finished))

    @classmethod
    def filter_active(cls, *args, **kwargs) -> list["Incidents"]:
        """ Runs the `filter` class method, but only returns active incidents """
        return cls.filter(*args, **kwargs)[0]

    @classmethod
    def filter_finished(cls, *args, **kwargs) -> list["Incidents"]:
        """ Runs the `filter` class method, but only returns finished incidents """
        return cls.filter(*args, **kwargs)[1]

    @classmethod
    def filter_all(cls, *args, **kwargs) -> list["Incidents"]:
        """ Runs the `filter` class method, and returns a flattened list of all incidents """
        filtered_incidents = cls.filter(*args, **kwargs)
        return [*filtered_incidents[0], *filtered_incidents[1]]

    def __class_getitem__(cls, incident_id: str) -> Optional["Incidents"]:
        if incident_id in cls.active:
            return cls.active[incident_id]
        elif incident_id in cls.finished:
            return cls.finished[incident_id]
        else:
            return None

    @property
    def failure(self):
        return Failure[self.failure_id]

    @property
    def thing(self):
        return Thing[self.thing_id]


def incident(thing_id: ThingId, failure_id: FailureId, ip: str, timestamp: int, comment: Optional[str] = None) -> "Incidents":
    return Incidents.create(thing_id, failure_id, ip, timestamp, comment)


def incident_del(thing_id: ThingId, failure_id: FailureId, ip: str, timestamp: int) -> Optional["Incidents"]:
    return Incidents.remove(thing_id, failure_id)
