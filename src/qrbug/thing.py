import html
from typing import Optional, TypeAlias

import qrbug

ThingId: TypeAlias = str


class Thing(qrbug.Tree):
    """
    A Thing that can fail.
    """
    instances: dict[ThingId, "Thing"] = {}

    # Default values
    location:   Optional[str]             = None
    failure_id: Optional[qrbug.FailureId] = None
    comment:    Optional[str]             = ""

    def _local_dump(self) -> str:
        # short_names = {
        #     'location': 'loc',
        #     'failure_id': 'failure',
        # }
        # return self.get_representation(attributes_short=short_names)
        return f'loc:{self.location} failure:{self.failure_id} comment:{repr(self.comment)}'


    def get_failures(self, as_html: bool = True) -> str:
        """
        Returns the representation of the failure of the given thing, as HTML or raw text.
        :param as_html: If True, return an HTML representation of the failure. Otherwise, returns as raw text.
        """
        # Gets the failure for this thing
        root_failure = self.failure
        if root_failure is None:
            return f"""Il n'est possible de déclarer aucun panne pour
            <ul>
            <li> Identifiant : «{self.id}»
            <li> Emplacement : «{self.location}»
            <li> Commentaire : «{self.comment}»
            </ul>"""

        if as_html:
            return root_failure.get_hierarchy_representation_html(self.id)
        else:
            return root_failure.get_hierarchy_representation()

    @property
    def failure(self) -> Optional[qrbug.Failure]:
        return qrbug.Failure[self.failure_id]

    def get_html(self, is_full_page: bool = False) -> str:
        """
        Returns an HTML representation of this Thing and its linked Failure.
        :param is_full_page: If true, will return a full page based on 'STATIC/report_failure.html'
        :return: The HTML representation of this Thing.
        """
        if is_full_page:
            with qrbug.REPORT_FAILURE_TEMPLATE as template_file:
                html_template = template_file.read_text()

        representation: list[str] = [
            '<div>',
            '  <ul>',
            f'    <li>Emplacement : {html.escape(self.location) if self.location is not None else "[NON REMPLI]"}</li>',
            f'    <li>Commentaire : {html.escape(self.comment) if self.comment else "[NON REMPLI]"}</li>',
            f'    <li>ID : {html.escape(self.id) if self.id is not None else "[NON REMPLI]"}</li>',
            f'    <li>ID de la Failure : {html.escape(self.failure_id) if self.failure_id is not None else "[NON REMPLI]"}</li>',
            '  </ul>',
            '</div>',
            '<div>',
            self.failure.get_hierarchy_representation_html(self.id, False),
            '</div>',
            '<div>',
        ]
        if is_full_page:
            representation.append(
                f'  <div failureid="generate_qr" thingid="{self.id}" class="button" onclick="register_incident(this)"><BOX>Générer un QR code pour cet objet</BOX></div>'
            )
        else:
            representation.append(
                f'  <a href="/?thing-id={self.id}&failure-id=generate_qr&is-repaired=0&additional-info={self.id}">Générer un QR code pour cet objet</a>'
            )
        representation.append('</div>')

        if is_full_page:
            return html_template.replace("%REPRESENTATION%", ''.join(representation))
        else:
            return ''.join(representation)


def thing_update(thing_id: ThingId, **kwargs) -> Thing:
    """
    Creates a new thing that can fail, or modifies an existing one.
    :param thing_id: The ID of this thing.
    :param location: Where this thing is located.
    :param failure_id: Which is the root failure for this thing ?
    :param comment: Any comment on the thing.
    """
    return Thing.update_attributes(thing_id, **kwargs)

def thing_add(parent: ThingId, child: ThingId) -> None:
    """
    Adds a ting inside a thing.
    :param parent: The ID of the thing to add the child to.
    :param child: The ID of the child failure.
    """
    Thing.add_parenting_link(parent, child)

def thing_remove(parent: ThingId, child: ThingId) -> None:
    """
    Removes the parenting link from a Thing to another.
    :param parent: The ID of the Thing to remove the child from.
    :param child: The ID of the Thing to be removed.
    """
    Thing.remove_parenting_link(parent, child)


def thing_del(thing_id: ThingId) -> None:
    """
    Deletes an existing thing.
    :param thing_id: The ID of this thing.
    """
    del Thing.instances[thing_id]


qrbug.Thing = Thing
qrbug.ThingId = ThingId
qrbug.thing_update = thing_update
qrbug.thing_del = thing_del
qrbug.thing_remove = thing_remove
qrbug.thing_add = thing_add

if __name__ == "__main__":
    thing_update("0", location="Testing location", comment="This is a comment")
    print(Thing.get("0").dump())
