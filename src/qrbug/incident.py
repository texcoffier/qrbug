import time
from typing import Optional, Tuple
import re
import html

import qrbug


def safe(string: str) -> str:
    return (string.replace('\n', '\\n')
                  .replace('\r', '\\r')
            )

class Report:
    remover_login:Optional[str] = None
    def __init__(self, ip: str, timestamp: int, comment: Optional[str] = None, login: str = ''):
        self.ip = ip
        self.timestamp = timestamp
        self.comment = comment
        self.login = login
        self.remover_login = None
    def __str__(self):
        return f'Report({repr(self.ip)}, {self.timestamp}, {repr(self.comment)}, {repr(self.login)}, {repr(self.remover_login)})'

class Incident:
    instances: dict[Tuple["ThingID", "FailureID"], "Incident"] = {}
    pending_feedback:list[Report] = []
    def __init__(self, thing_id: str, failure_id: str):
        self.thing_id = thing_id
        self.failure_id = failure_id
        self.active: list[Report] = []
        self.finished: list[Report] = []
        self.dispatchers: set["Dispatcher"] = set()

    def dump(self) -> str:
        active = ''.join(f'    Active {report.ip} {report.login} {report.comment}\n'
                           for report in self.active)
        finished = ''.join(f'   Finished {report.ip} {report.login} {report.comment} {report.remover_login}\n'
                           for report in self.finished)
        return f'thing: «{self.thing_id}» failure: «{self.failure_id}»\n{active}{finished}'

    def is_equal(self, other_thing_id, other_failure_id) -> bool:
        return self.thing_id == other_thing_id and self.failure_id == other_failure_id

    def is_for(self, user: "User") -> bool:
        """A dispatcher has been triggered for this user."""
        for dispatcher in self.dispatchers:
            if user.inside_or_equal(qrbug.Dispatcher[dispatcher].group_id):
                return True
        return False

    @classmethod
    def create(cls, thing_id: str, failure_id: str, ip: str, timestamp: int,
               comment: Optional[str] = None, login: Optional[str] = None) -> "Incident":
        """
        Factory method, creates a new incident and stores it within the incident instances
        """
        key = (thing_id, failure_id)
        if key not in cls.instances:
            cls.instances[key] = Incident(thing_id, failure_id)
        incident = cls.instances[key]
        incident.active.append(Report(ip, timestamp, comment, login))
        return incident

    @classmethod
    def close(cls, thing_id: qrbug.ThingId, failure_id: qrbug.FailureId, ip: str, login: str) -> "Incident":
        """
        Closes the given incident AND writes it into the journal
        """
        return qrbug.append_line_to_journal(
            f"incident_del({repr(thing_id)}, {repr(failure_id)}, {repr(ip)}, {int(time.time())}, {repr(login)})"
            f" # {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        )

    def incident_del(self):
        """
        This function is called only to delete the created incident
        because it is an API incident.
        Not called on journal loading.
        """
        return self.close(self.thing_id, self.failure_id,
                          self.active[-1].ip, self.active[-1].login)

    @classmethod
    def open(cls, thing_id: qrbug.ThingId, failure_id: qrbug.FailureId, ip: str, login: str, additional_info: Optional[str] = None) -> "Incident":
        """
        Opens a new incident based on the parameters AND writes it into the journal
        """
        final_string = [
            f"incident_new({repr(thing_id)}, {repr(failure_id)}, {repr(ip)}, {int(time.time())},",
            '""',
            f", {repr(login)})  # {time.strftime('%Y-%m-%d %H:%M:%S')}\n",
        ]
        if additional_info is not None:
            final_string[1] = f"{repr(additional_info)}"
        return qrbug.append_line_to_journal(''.join(final_string))

    @classmethod
    def remove(cls, other_thing_id: str, other_failure_id: str, login: str) -> None:
        """
        Deletes any given incident from the list of incidents
        :param login: The login of the user who removed the incident.
        """
        incident = cls.instances[other_thing_id, other_failure_id]
        for report in incident.active:
            report.remover_login = login
            incident.finished.append(report)
        incident.pending_feedback = incident.active
        incident.active = []
        incident.dispatchers.clear()

    @classmethod
    def filter(
            cls, incidents: list["Incident"], *, thing_id: str = None, failure_id: str = None, ip: str = None,
            login: str = None, timestamp_min: int = 0, timestamp_max: int = None, comment: str = None,
            active: bool = True
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
            for report in incident.active if active else incident.finished:
                if ip is not None and ip != incident.ip:
                    continue
                if login is not None and login != incident.login:
                    continue
                if incident.timestamp < timestamp_min:
                    continue
                if timestamp_max is not None and incident.timestamp > timestamp_max:
                    continue
                if comment is not None and re.match(comment, incident.comment) is None:
                    continue
                return True
            return False
        return list(filter(condition_filter, incidents))

    @classmethod
    def filter_both(cls, *args, **kwargs) -> tuple[list["Incident"], list["Incident"]]:
        """
        Filters both lsts of incidents (active and finished) separately
        :return: A tuple of the incidents matching the given criteria ;
            first element is active incidents, second element is finished incidents
        """
        return (list(cls.filter(cls.instances, *args, **kwargs, active=True)),
                list(cls.filter(cls.instances, *args, **kwargs, active=False)))

    @classmethod
    def filter_active(cls, *args, **kwargs) -> list["Incident"]:
        """ Runs the `filter` class method, but only returns active incidents """
        return cls.filter(cls.instances, *args, **kwargs, active=True)

    @classmethod
    def filter_finished(cls, *args, **kwargs) -> list["Incident"]:
        """ Runs the `filter` class method, but only returns finished incidents """
        return cls.filter(cls.instances, *args, **kwargs, active=False)

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


def incident_new(thing_id: qrbug.ThingId, failure_id: qrbug.FailureId, ip: str,
        timestamp: int, comment: Optional[str] = None, login: Optional[str] = None) -> "Incident":
    return Incident.create(thing_id, failure_id, ip, timestamp, comment, login)


def incident_del(thing_id: qrbug.ThingId, failure_id: qrbug.FailureId, ip: str, timestamp: int, login: str) -> list["Incident"]:
    Incident.remove(thing_id, failure_id, login)


def get_incident_email_contents(incident: Incident) -> str:
    email_body = [
        f'QRBUG: Un incident s\'est produit sur la machine {repr(incident.thing_id)} avec la panne {repr(incident.failure_id)}.'
    ]
    if len(incident.active) > 0:
        email_body.append('\n\n')
        email_body.append(f'Cet incident a été signalé un total de {len(incident.active)} fois par :\n')
        for report in incident.active:
            email_body.append(f'- {report.login} (IP: {report.ip}) le {time.strftime("%d/%m/%Y à %H:%M:%S")}\n')
            if report.comment:
                email_body.append(f'  - Avec le commentaire: {html.escape(report.comment)}\n')
    return ''.join(email_body)


qrbug.Incident = Incident
qrbug.incident_new = incident_new
qrbug.incident_del = incident_del
qrbug.get_incident_email_contents = get_incident_email_contents
