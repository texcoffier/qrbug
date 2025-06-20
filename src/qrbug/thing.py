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

    # @property
    # def failure(self) -> Optional[qrbug.Failure]:
    #     return qrbug.Failure[self.failure_id]

    def get_html(self, is_full_page: bool = False) -> str:
        """
        Returns an HTML representation of this Thing and its linked Failure.
        :param is_full_page: If true, will return a full page based on 'STATIC/report_failure.html'
        :return: The HTML representation of this Thing.
        """
        if is_full_page:
            with qrbug.REPORT_FAILURE_TEMPLATE as template_file:
                html_template = template_file.read_text()

        done = set()
        representation: list[str] = [
            '<div>',
            '  <ul>',
            f'    <li>Commentaire : {html.escape(self.comment) if self.comment else "[NON REMPLI]"}</li>',
            f'    <li>ID : {html.escape(self.id) if self.id is not None else "[NON REMPLI]"}</li>',
            f'    <li>ID des pannes : {html.escape(repr(self.failure_ids))}</li>',
            '  </ul>',
            '</div>',
            '<div>',
            *(
              qrbug.Failure[failure].get_hierarchy_representation_html(
                    self.id, use_template=False, done=done)
              for failure_id in self.failures_ids
             ),
            '</div>',
            '<div>',
        ]
        if is_full_page:
            representation.append(
                f'  <div failureid="generate_qr" thingid="{self.id}" class="button" onclick="register_incident(this)"><BOX>Générer un QR code pour cet objet</BOX></div>'
            )
        else:
            representation.append(
                f'  <a href="/?thing-id={self.id}&failure-id=generate_qr&additional-info={self.id}">Générer un QR code pour cet objet</a>'
            )
        representation.append('</div>')

        if is_full_page:
            return html_template.replace("%REPRESENTATION%", ''.join(representation))
        else:
            return ''.join(representation)

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

if __name__ == "__main__":
    thing_update("0", comment="This is a comment")
    print(Thing["0"].dump())
