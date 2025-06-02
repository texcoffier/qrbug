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
        pass  # TODO: Gérer le cas d'usage d'un déclenchement après plusieurs signalements de pannes dans une même salle

    def _local_dump(self) -> str:
        # short_names = {
        #     'action_id': 'action',
        #     'selector_id': 'selector',
        #     'group_id': 'group',
        # }
        # return self.get_representation(attributes_short=short_names)
        return f'action:{self.action_id} selector:{self.selector_id} group:{self.group_id} when:{self.when}'

    async def run(self, incident: qrbug.Incident, request) -> Optional[str]:
        """
        Returns a dict with keys being the thing_id and failure_id of an incident, and values being the returned HTML.
        """
        selector = qrbug.Selector[self.selector_id]
        action = qrbug.Action[self.action_id]

        # TODO: ! DOCUMENTATION !

        # TODO : Action renvoie un dictionnaire
        # - Champs avec message d'erreur
        # - Champs avec 'auto-repair' (incident_del, defaults False)

        if not selector.is_ok(qrbug.User[self.group_id], qrbug.Thing[incident.thing_id], qrbug.Failure[incident.failure_id]):
            # TODO: Dans le sélecteur - teste si 3 incidents dans 1 salle, si pour un d'entre eux le dispatcheur est lancé, il n'est pas relancé
            return None

        #if (incident.failure_id, incident.thing_id) in self.running_incidents:
        #    # The dispatcher doesn't run because it is already active
        #    return None

        # dispatch() updates the running_incidents set (increases size)
        qrbug.append_line_to_journal(f'dispatch({repr(self.id)}, {repr(incident.failure_id)}, {repr(incident.thing_id)}, {repr(self.action_id)}, {repr(self.group_id)}, {int(time.time())})  # {time.strftime("%Y-%m-%d %H:%M:%S")}\n')

        return_value = await action.run(incident, request)
        # Action.run décide de la liste des incidents sur lesquels ont veut dire 'les dispatcheurs ont pris ceux-là en comlpte'
        # `A ce moment-là, on rajoute au journal la liste de ces incidents
        # On ajoute incident_update, on lui passe le (thing_id, failure_id) et le dispatcher_id
        # Quand le serveur edémarre, on va remettre à jour la liste des dispatchers qui ont été lancés.

        #if (incident.failure_id, incident.thing_id) in self.running_incidents:
            # dispatch_del() updates the running_incidents set (reduces size)
        #    qrbug.append_line_to_journal(f'dispatch_del({repr(self.id)}, {repr(incident.failure_id)}, {repr(incident.thing_id)}, {repr(self.action_id)}, {repr(self.group_id)}, {int(time.time())})  # {time.strftime("%Y-%m-%d %H:%M:%S")}\n')

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
    #Dispatcher[dispatch_id].running_incidents.add((failure_id, thing_id))
    pass


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
    pass
    #Dispatcher[dispatch_id].running_incidents.remove((failure_id, thing_id))


qrbug.Dispatcher = Dispatcher
qrbug.DispatcherId = DispatcherId
qrbug.dispatcher_update = dispatcher_update
qrbug.dispatcher_del = dispatcher_del
qrbug.dispatch = dispatch
qrbug.dispatch_del = dispatch_del

if __name__ == "__main__":
    dispatcher_update("0", when="Test", selector_id="0")
    print(Dispatcher.get("0").dump())
