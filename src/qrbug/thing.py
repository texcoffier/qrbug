import html
from typing import Optional, TypeAlias

import qrbug

ThingId: TypeAlias = str


class Thing(qrbug.Tree):
    """
    A Thing that can fail.
    """
    instances: dict[ThingId, "Thing"] = {}
    comment = ""

    def init(self):
        self.failure_ids:set[qrbug.FailureId] = []

    def _local_dump(self) -> str:
        return f'failures:{self.failure_ids} comment:{repr(self.comment)}'

    def get_failures(self, secret = 0, as_html: bool = True) -> str:
        """
        Returns the representation of the failure of the given thing, as HTML or raw text.
        :param as_html: If True, return an HTML representation of the failure. Otherwise, returns as raw text.
        """
        # Gets the failure for this thing
        if not self.failure_ids:
            return f"""Il n'est pas possible de déclarer de panne pour
            <ul>
            <li> Identifiant : «{self.id}»
            <li> Commentaire : «{self.comment}»
            </ul>"""

        done = set()
        texts = []
        for failure_id in self.failure_ids:
            failure = qrbug.Failure[failure_id]
            if as_html:
                texts.append(failure.get_hierarchy_representation_html(self, secret, use_template=False, done=done))
            else:
                texts.append(failure.get_hierarchy_representation(done))
        if as_html:
            return qrbug.get_template().replace("%REPRESENTATION%", ''.join(texts))
        return ''.join(texts)

    @classmethod
    def add_failure(cls, thing_id, failure_id):
        failures = cls.instances[thing_id].failure_ids
        if failure_id in failures:
            failures.remove(failure_id)
        failures.append(failure_id)

    @classmethod
    def del_failure(cls, thing_id, failure_id):
        cls.instances[thing_id].failure_ids.remove(failure_id)

def thing_del(thing_id: ThingId) -> None:
    """
    Deletes an existing thing.
    :param thing_id: The ID of this thing.
    """
    del Thing.instances[thing_id]

qrbug.Thing = Thing
qrbug.ThingId = ThingId
qrbug.thing_update = Thing.update_attributes
qrbug.thing_del = thing_del
qrbug.thing_remove = Thing.remove_parenting_link
qrbug.thing_add = Thing.add_parenting_link
qrbug.thing_add_failure = Thing.add_failure
qrbug.thing_del_failure = Thing.del_failure
