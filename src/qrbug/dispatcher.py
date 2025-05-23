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

    def _local_dump(self) -> str:
        # short_names = {
        #     'action_id': 'action',
        #     'selector_id': 'selector',
        #     'group_id': 'group',
        # }
        # return self.get_representation(attributes_short=short_names)
        return f'action:{self.action_id} selector:{self.selector_id} group:{self.group_id} when:{self.when}'

    async def run(self, incidents: list[qrbug.Incidents], group_id: str, request) -> dict[tuple[str, str], str]:
        """
        Returns a dict with keys being the thing_id and failure_id of an incident, and values being the returned HTML.
        """
        selector = qrbug.Selector[self.selector_id]
        action = qrbug.Action[self.action_id]
        return_value: dict[tuple[str, str], Optional[str]] = {}
        for incident in incidents:
            if selector.is_ok(qrbug.User[group_id], qrbug.Thing[incident.thing_id], qrbug.Failure[incident.failure_id]):
                # TODO: Retirer de la liste si pas is_ok()
                # TODO : Garder en mémoire que le dispatcher a été activé - fonction dispatch dans le journal qui indique l'activation d'un dispatcher
                return_value[incident.thing_id, incident.failure_id] = await action.run(incident, request)
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


async def dispatch(
        dispatch_id: DispatcherId,
        failure_ids: list[qrbug.FailureId],
        action_id: qrbug.ActionId,
        group_id: qrbug.UserId,
        timestamp: int
) -> None:
    dispatcher = qrbug.Dispatcher[dispatch_id]
    if dispatcher is None:
        return

    # Looks for every incident with the given failure ids
    dispatched_incidents = []
    for failure_id in failure_ids:
        for current_incident in qrbug.Incidents.filter_active(failure_id=failure_id):
            dispatched_incidents.append(current_incident)

    await dispatcher.run(dispatched_incidents, group_id, None)  # TODO: Virer le run pour le journal
    # TODO: Garder dispatched_incidents


qrbug.Dispatcher = Dispatcher
qrbug.DispatcherId = DispatcherId
qrbug.dispatcher_update = dispatcher_update
qrbug.dispatcher_del = dispatcher_del
qrbug.dispatch = dispatch

if __name__ == "__main__":
    dispatcher_update("0", when="Test", selector_id="0")
    print(Dispatcher.get("0").dump())
