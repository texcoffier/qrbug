"""
Reloads config journals
"""
import time
from typing import Optional, List

import qrbug

async def run(_incidents: List[qrbug.Incident], request: qrbug.Request) -> Optional[qrbug.action_helpers.ActionReturnValue]:
    # Deletes all instances from each data structure
    for data_structure in (qrbug.Action, qrbug.Concerned, qrbug.Dispatcher, qrbug.Failure, qrbug.Incident, qrbug.Selector, qrbug.Thing, qrbug.User):
        data_structure.instances.clear()
        if hasattr(data_structure, 'sorted_instances') and data_structure.sorted_instances is not None:
            data_structure.sorted_instances.clear()

    # Reloads the journals
    start = time.time()
    qrbug.load_config()
    qrbug.load_incidents()
    stop = time.time()
    duration = stop - start
    print(f'Load journals : {duration:.2f} seconds')

    await request.write(f'Journaux rechargés en <b>{duration:.2f} secondes.</b>')
