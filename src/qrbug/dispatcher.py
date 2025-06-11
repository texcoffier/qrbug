import os
import time
import traceback
from typing import Optional, TypeAlias

import qrbug


DispatcherId: TypeAlias = str


class Dispatcher(qrbug.Tree):
    instances: dict[DispatcherId, "Dispatcher"] = {}

    # Default values
    action_id   : str = 'none'  # By default, an action that does nothing
    selector_id : str = 'true'  # By default, a selector that is always true
    incidents   : str = ''      # Selector ID to compute incidents list. If empty : current incident

    def init(self):
        pass  # TODO: Gérer le cas d'usage d'un déclenchement après plusieurs signalements de pannes dans une même salle

    def _local_dump(self) -> str:
        return f'action:{self.action_id} selector:{self.selector_id} incidents:{self.incidents}'

    async def run(self, incident: qrbug.Incident, request) -> Optional[qrbug.action_helpers.ActionReturnValue]:
        """
        Returns a dict with keys being the thing_id and failure_id of an incident, and values being the returned HTML.
        """
        # TODO: ! DOCUMENTATION !

        if not qrbug.Selector[self.selector_id].is_ok(incident):
            return None

        if self.incidents:
            selector = qrbug.Selector[self.incidents]
            incidents = [i
                         for i in qrbug.Incident.instances.values()
                         if selector.is_ok(i, incident, request.report)
                        ]
        else:
            incidents = [incident]

        if not incidents:
            return

        ################################################
        # NO «await» ARE ALLOWED BEFORE THIS LINE
        # It is done in order to get the last «Report»
        ################################################

        try:
            return_value = await qrbug.Action[self.action_id].run(incidents, request)
        except Exception as e:
            retrieved_traceback = '\n'.join(traceback.format_exception(e))
            return_value = qrbug.action_helpers.ActionReturnValue(
                error_msg=(
                        '<pre style="background-color: rgba(255, 0, 0, 0.4); padding: 4px; border-radius: 2px;">' +
                        retrieved_traceback +
                        '</pre>'
                )
            )
            qrbug.log_error(retrieved_traceback)

        # 'dispatch' erase 'pending_feedback' and it is needed by the action
        qrbug.append_line_to_journal(f'dispatch({repr(self.id)}, {repr(incident.failure_id)}, {repr(incident.thing_id)}, {repr(self.action_id)}, {int(time.time())})  # {time.strftime("%Y-%m-%d %H:%M:%S")} {len(incidents)} incidents\n')

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
        timestamp: int
) -> None:
    """
    The parameters (besides dispatch_id, thing_id, and failure_id) are useless, they only store information in the log file.
    This functions marks a dispatcher as running and that it should not be run for these incidents only.
    """
    #Dispatcher[dispatch_id].running_incidents.add((failure_id, thing_id))
    if dispatch_id == 'send-pending-feedback': # Not nice
        for incident in qrbug.Incident.instances.values():
            incident.pending_feedback = []


def dispatch_del(
        dispatch_id: DispatcherId,
        failure_id: qrbug.FailureId,
        thing_id: qrbug.ThingId,
        action_id: qrbug.ActionId,
        timestamp: int
) -> None:
    """
    The parameters (besides dispatch_id, thing_id, and failure_id) are useless, they only store information in the log file.
    This functions marks a dispatcher as running and that it should not be run for these incidents only.
    """
    pass
    #Dispatcher[dispatch_id].running_incidents.remove((failure_id, thing_id))


qrbug.Dispatcher = Dispatcher
qrbug.DispatcherId = DispatcherId
qrbug.dispatcher_update = dispatcher_update
qrbug.dispatcher_del = dispatcher_del
qrbug.dispatch = dispatch
qrbug.dispatch_del = dispatch_del

if __name__ == "__main__":
    dispatcher_update("0", selector_id="0")
    print(Dispatcher.get("0").dump())
