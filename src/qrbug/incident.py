import time
from typing import Optional
import re

import qrbug


def safe(string: str) -> str:
    return (string.replace('\n', '\\n')
                  .replace('\r', '\\r')
            )


class Incident:  # TODO: Séparer en deux classes, une avec les parties individuelles te une avec les parties communes
    active: list["Incident"] = []
    finished: list["Incident"] = []

    # TODO: Un dico avec (thing_id, failure_id) contenant la liste d'incidents

    def __init__(self, thing_id: str, failure_id: str, ip: str, timestamp: int, comment: Optional[str] = None, login: str = ''):
        self.thing_id = thing_id
        self.failure_id = failure_id
        self.ip = ip
        self.timestamp = timestamp
        self.comment = comment
        self.login = login
        self.remover_login = None

    def dump(self) -> str:
        return f'thing:{self.thing_id} fail:{self.failure_id} ip:{self.ip} comment:{repr(self.comment)}'

    def is_equal(self, other_thing_id, other_failure_id) -> bool:
        return self.thing_id == other_thing_id and self.failure_id == other_failure_id

    @classmethod
    def create(cls, thing_id: str, failure_id: str, ip: str, timestamp: int, comment: Optional[str] = None) -> "Incident":
        """
        Factory method, creates a new incident and stores it within the incident instances
        """
        new_incident = Incident(thing_id, failure_id, ip, timestamp, comment)
        cls.active.append(new_incident)
        return new_incident

    @classmethod
    def close(cls, thing_id: qrbug.ThingId, failure_id: qrbug.FailureId, ip: str, login: str) -> "Incident":
        """
        Closes the given incident AND writes it into the journal
        """
        return qrbug.append_line_to_journal(
            f"incident_del({repr(thing_id)}, {repr(failure_id)}, {repr(ip)}, {int(time.time())}, {repr(login)})"
            f"  # {time.strftime('%Y-%m-%d %H:%M:%S')} {safe(login)}\n"
        )

    def incident_del(self):
        return self.close(self.thing_id, self.failure_id, self.ip, self.login)

    @classmethod
    def open(cls, thing_id: qrbug.ThingId, failure_id: qrbug.FailureId, ip: str, login: str, additional_info: Optional[str] = None) -> "Incident":
        """
        Opens a new incident based on the parameters AND writes it into the journal
        """
        final_string = [
            f"incident_new({repr(thing_id)}, {repr(failure_id)}, {repr(ip)}, {int(time.time())}",
            '',
            f")  # {time.strftime('%Y-%m-%d %H:%M:%S')} {safe(login)}\n",
        ]
        if additional_info is not None:
            final_string[1] = f", {repr(additional_info)}"
        return qrbug.append_line_to_journal(''.join(final_string))

    @classmethod
    def remove(cls, other_thing_id: str, other_failure_id: str, login: str) -> list["Incident"]:
        """
        Deletes any given incident from the list of incidents
        :param login: The login of the user who removed the incident.
        """
        filtered_incidents = cls.filter_active(thing_id=other_thing_id, failure_id=other_failure_id)
        for failure_to_remove in filtered_incidents:
            failure_to_remove.remover_login = login
            cls.active.remove(failure_to_remove)
            cls.finished.append(failure_to_remove)
        return filtered_incidents

    @classmethod
    def filter(
            cls, incidents: list["Incident"], *, thing_id: str = None, failure_id: str = None, ip: str = None,
            login: str = None, timestamp_min: int = 0, timestamp_max: int = None, comment: str = None
    ) -> list["Incident"]:
        """
        Returns the list of incidents matching the given criteria
        :param incidents: The list of incidents to filter.
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
        return list(filter(condition_filter, incidents))

    @classmethod
    def filter_both(cls, *args, **kwargs) -> tuple[list["Incident"], list["Incident"]]:
        """
        Filters both lsts of incidents (active and finished) separately
        :return: A tuple of the incidents matching the given criteria ;
            first element is active incidents, second element is finished incidents
        """
        return list(cls.filter(cls.active, *args, **kwargs)), list(cls.filter(cls.finished, *args, **kwargs))

    @classmethod
    def filter_active(cls, *args, **kwargs) -> list["Incident"]:
        """ Runs the `filter` class method, but only returns active incidents """
        return cls.filter(cls.active, *args, **kwargs)

    @classmethod
    def filter_finished(cls, *args, **kwargs) -> list["Incident"]:
        """ Runs the `filter` class method, but only returns finished incidents """
        return cls.filter(cls.finished, *args, **kwargs)

    @classmethod
    def filter_all(cls, *args, **kwargs) -> list["Incident"]:
        """ Runs the `filter` class method, and returns a flattened list of all incidents """
        filtered_incidents = cls.filter_both(*args, **kwargs)
        return [*filtered_incidents[0], *filtered_incidents[1]]

    @property
    def failure(self):
        return qrbug.Failure[self.failure_id]

    @property
    def thing(self):
        return qrbug.Thing[self.thing_id]


def incident_new(thing_id: qrbug.ThingId, failure_id: qrbug.FailureId, ip: str, timestamp: int, comment: Optional[str] = None) -> "Incident":
    return Incident.create(thing_id, failure_id, ip, timestamp, comment)


def incident_del(thing_id: qrbug.ThingId, failure_id: qrbug.FailureId, ip: str, timestamp: int, login: str) -> list["Incident"]:
    return Incident.remove(thing_id, failure_id, login)


qrbug.Incident = Incident
qrbug.incident_new = incident_new
qrbug.incident_del = incident_del
