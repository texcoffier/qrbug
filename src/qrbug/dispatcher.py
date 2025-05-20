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

    def run(self, incidents: list[qrbug.incidents.Incidents], group_id: str, request) -> dict[tuple[str, str], str]:
        """
        Returns a dict with keys being the thing_id and failure_id of an incident, and values being the returned HTML.
        """
        import qrbug
        if self.selector_id is None or self.action_id is None:
            return {}

        selector = qrbug.Selector[self.selector_id]
        action = qrbug.Action[self.action_id]
        return_value: dict[tuple[str, str], Optional[str]] = {}
        for incident in incidents:
            if selector.is_ok(qrbug.User[group_id], qrbug.Thing[incident.thing_id], qrbug.Failure[incident.failure_id]):
                return_value[incident.thing_id, incident.failure_id] = action.run(incident, request)
        return return_value


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
