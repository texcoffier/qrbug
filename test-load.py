#!/usr/bin/python3
"""
Create a big config and incident journal
"""

things = []
with open('TESTS/xxx-testload.conf', 'w') as file:
    file.write(
        'user_update("ROOT")\n'
        'user_add("admin", "ROOT")\n'
        'thing_update("Campus")\n'
        'failure_update("F1")\n'
        'failure_update("F2")\n'
        'failure_update("F3")\n'
        )
    for b in range(30):
        building = f'"Building{b}"'
        file.write(
            f'thing_update({building})\n'
            f'thing_add("Campus",{building})\n'
        )
        for r in range(30):
            room = f'"Room{b}_{r}"'
            file.write(
                f'thing_update({room})\n'
                f'thing_add({building}, {room})\n'
            )
            for host in range(40):
                host = f'"Host{b}_{r}_{host}"'
                file.write(
                    f'thing_update({host})\n'
                    f'thing_add({room}, {host})\n'
                    f'thing_add_failure({host}, "F")\n'
                    )
                things.append(host)

with open('TESTS/xxx-incidents.py', 'w') as file:
    for thing in things:
        for failure in ('F1', 'F2', 'F3'):
            file.write(f"""

# User report
incident_new('{thing}', '{failure}', '127.0.0.1', 1749979950, '', '') # 2025-06-15 11:32:30

# Admin check if something to do
incident_new('admin', 'personnal-for-me', '127.0.0.1', 1749979935, '', 'thierry.excoffier') # 2025-06-15 11:32:15

# Display the incident list
dispatch('personnal-for-me', 'personnal-for-me', 'admin', 'echo', 1749979935) # 2025-06-15 11:32:15 1 incidents

# Close the API incident
incident_del('admin', 'personnal-for-me', 'thierry.excoffier') # 2025-06-15 11:32:15 '127.0.0.1'

# Cleanup needed feedback
dispatch('z-backoffice-close', 'personnal-for-me', 'admin', 'close_auto', 1749979935) # 2025-06-15 11:32:15 1 incidents

# Mark incident as fixed
incident_del('{thing}', '{failure}', 'thierry.excoffier') # 2025-06-15 11:32:15 '127.0.0.1'

# List waiting feedback
incident_new('admin', 'pending-feedback', '127.0.0.1', 1750086416, '', 'thierry.excoffier') # 2025-06-16 17:06:56
dispatch('pending-feedback', 'pending-feedback', 'admin', 'echo', 1750086416) # 2025-06-16 17:06:56 1 incidents
incident_del('admin', 'pending-feedback', 'thierry.excoffier') # 2025-06-16 17:06:56 '127.0.0.1'
dispatch('z-backoffice-close', 'pending-feedback', 'admin', 'close_auto', 1750086416) # 2025-06-16 17:06:56 1 incidents

# Send user feedback (erase list in memory)
incident_new('admin', 'send-pending-feedback', '127.0.0.1', 1750086503, '', 'thierry.excoffier') # 2025-06-16 17:08:23
dispatch('send-pending-feedback', 'send-pending-feedback', 'admin', 'pending_feedback', 1750086503) # 2025-06-16 17:08:23 1 incidents
incident_del('admin', 'send-pending-feedback', 'thierry.excoffier') # 2025-06-16 17:08:23 '127.0.0.1'
dispatch('z-backoffice-close', 'send-pending-feedback', 'admin', 'close_auto', 1750086503) # 2025-06-16 17:08:23 1 incidents

""")



