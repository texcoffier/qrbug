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
    instances: dict["ThingID", dict["FailureID", "Incident"]] = {}
    pending_feedback:list[Report] = []
    def __init__(self, thing_id: str, failure_id: str):
        self.thing_id = thing_id
        self.failure_id = failure_id
        self.active: list[Report] = []
        self.finished: list[Report] = []

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
        for concerned in qrbug.Concerned.instances.values():
            for u in concerned.users:
                if user.inside_or_equal(u):
                    if qrbug.Selector[concerned.id].is_ok(self):
                        return True
        return False

    @classmethod
    def create(cls, thing_id: str, failure_id: str, ip: str, timestamp: int,
               comment: Optional[str] = None, login: Optional[str] = None) -> "Incident":
        """
        Factory method, creates a new incident and stores it within the incident instances
        """
        key = (thing_id, failure_id)
        if thing_id not in cls.instances:
            cls.instances[thing_id] = {}
        if failure_id not in cls.instances[thing_id]:
            cls.instances[thing_id][failure_id] = Incident(thing_id, failure_id)
        incident = cls.instances[thing_id][failure_id]
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
            f"incident_new({repr(thing_id)}, {repr(failure_id)}, {repr(ip)}, {int(time.time())}, ",
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
        incident = cls.instances[other_thing_id][other_failure_id]
        for report in incident.active:
            report.remover_login = login
            incident.finished.append(report)
        # Pending feedback is cleared on 'send-pending-feedback' failure dispatch
        incident.pending_feedback = incident.active
        incident.active = []

    @property
    def failure(self):
        return qrbug.Failure[self.failure_id]

    @property
    def thing(self):
        return qrbug.Thing[self.thing_id]

    @property
    def concerned(self):
        return qrbug.Concerned[self.thing_id]


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
