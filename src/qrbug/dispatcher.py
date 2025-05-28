import time
from typing import Optional, TypeAlias

import qrbug


DispatcherId: TypeAlias = str


class Dispatcher(qrbug.Tree):
    instances: dict[DispatcherId, "Dispatcher"] = {}

    # Default values
    action_id   : str = 'none'  # By default, an action that does nothing
    selector_id : str = 'true'  # By default, a selector that is always true
    group_id    : str = 'nobody'  # Group of people to warn upon dispatch, default is user group 'nobody'
    when        : str = 'synchro'

    def init(self):
        self.running_incidents: set[tuple[str, str]] = set()

    def _local_dump(self) -> str:
        # short_names = {
        #     'action_id': 'action',
        #     'selector_id': 'selector',
        #     'group_id': 'group',
        # }
        # return self.get_representation(attributes_short=short_names)
        return f'action:{self.action_id} selector:{self.selector_id} group:{self.group_id} when:{self.when}'

    async def run(self, incidents: list[qrbug.Incidents], request) -> dict[tuple[str, str], str]:
        """
        Returns a dict with keys being the thing_id and failure_id of an incident, and values being the returned HTML.
        """
        selector = qrbug.Selector[self.selector_id]
        action = qrbug.Action[self.action_id]

        return_value: dict[tuple[str, str], Optional[str]] = {}
        for incident in incidents:
            if selector.is_ok(
                    qrbug.User[self.group_id], qrbug.Thing[incident.thing_id], qrbug.Failure[incident.failure_id]
            ) and (incident.failure_id, incident.thing_id) not in self.running_incidents:  # The dispatcher doesn't run because it is already active
                qrbug.append_line_to_journal(f'dispatch({repr(self.id)}, {repr(incident.failure_id)}, {repr(incident.thing_id)}, {repr(self.action_id)}, {repr(self.group_id)}, {int(time.time())})\n')
                return_value[incident.thing_id, incident.failure_id] = await action.run(incident, request)

                if (incident.failure_id, incident.thing_id) in self.running_incidents:
                    qrbug.append_line_to_journal(f'dispatch_del({repr(self.id)}, {repr(incident.failure_id)}, {repr(incident.thing_id)}, {repr(self.action_id)}, {repr(self.group_id)}, {int(time.time())})\n')

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


def dispatch(
        dispatch_id: DispatcherId,
        failure_id: qrbug.FailureId,
        thing_id: qrbug.ThingId,
        action_id: qrbug.ActionId,
        group_id: qrbug.UserId,
        timestamp: int
) -> None:
    """
    The parameters (besides dispatch_id, thing_id, and failure_id) are useless, they only store information in the log file.
    This functions marks a dispatcher as running and that it should not be run for these incidents only.
    """
    Dispatcher[dispatch_id].running_incidents.add((failure_id, thing_id))


def dispatch_del(
        dispatch_id: DispatcherId,
        failure_id: qrbug.FailureId,
        thing_id: qrbug.ThingId,
        action_id: qrbug.ActionId,
        group_id: qrbug.UserId,
        timestamp: int
) -> None:
    """
    The parameters (besides dispatch_id, thing_id, and failure_id) are useless, they only store information in the log file.
    This functions marks a dispatcher as running and that it should not be run for these incidents only.
    """
    Dispatcher[dispatch_id].running_incidents.remove((failure_id, thing_id))


qrbug.Dispatcher = Dispatcher
qrbug.DispatcherId = DispatcherId
qrbug.dispatcher_update = dispatcher_update
qrbug.dispatcher_del = dispatcher_del
qrbug.dispatch = dispatch
qrbug.dispatch_del = dispatch_del

if __name__ == "__main__":
    dispatcher_update("0", when="Test", selector_id="0")
    print(Dispatcher.get("0").dump())
