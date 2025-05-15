from typing import Optional, TypeAlias

import qrbug.incidents
from qrbug.tree import Tree


DispatcherId: TypeAlias = str


class Dispatcher(Tree):
    instances: dict[DispatcherId, "Dispatcher"] = {}

    # Default values
    action_id   : str = 'none'  # By default, an action that does nothing
    selector_id : str = 'true'  # By default, a selector that is always true
    group_id    : str = 'nobody'  # Group of people to warn upon dispatch, default is user group 'nobody'
    when        : str = 'synchro'

    def _local_dump(self) -> str:
        # short_names = {
        #     'action_id': 'action',
        #     'selector_id': 'selector',
        #     'group_id': 'group',
        # }
        # return self.get_representation(attributes_short=short_names)
        return f'action:{self.action_id} selector:{self.selector_id} group:{self.group_id} when:{self.when}'

    def run(self, incidents: list[qrbug.incidents.Incidents]) -> None:
        import qrbug
        if self.selector_id is None or self.action_id is None:
            return

        selector = qrbug.Selector[self.selector_id]
        action = qrbug.Action[self.action_id]
        for incident in incidents:
            # TODO: Add the user
            if selector.is_ok(None, qrbug.Thing[incident.thing_id], qrbug.Failure[incident.failure_id]):
                action.run(incident)


def dispatcher_update(dispatch_id: str, **kwargs) -> Dispatcher:
    """
    Creates a new dispatcher, or modifies an existing one.
    :param dispatch_id: The ID of this dispatcher.
    """
    return Dispatcher.update_attributes(dispatch_id, **kwargs)


def dispatcher_del(dispatch_id: str) -> None:
    """
    Deletes an existing dispatcher.
    :param dispatch_id: The ID of this dispatcher.
    """
    del Dispatcher.instances[dispatch_id]


if __name__ == "__main__":
    dispatcher_update("0", when="Test", selector_id="0")
    print(Dispatcher.get("0").dump())
