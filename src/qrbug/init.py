import qrbug.logging_system
import qrbug.editable
import qrbug.tree
import qrbug.user
import qrbug.failure
import qrbug.thing
import qrbug.selector
import qrbug.concerned
import qrbug.incident
import qrbug.notifications
import qrbug.get_mail
import qrbug.action_helpers
import qrbug.action
import qrbug.dispatcher

import qrbug.config
import qrbug.test_framework
import qrbug.authentication
import qrbug.journals

# Caches in memory the webpage template
import time
start = time.time()
qrbug.get_template(force_load=True)
print(f'Load template : {time.time() - start:.4f} seconds')
