# pylint: disable=undefined-variable,line-too-long

action('none', 'none.py')
action('close', 'close.py')
action('close_auto', 'close_auto.py')
action('generate_qrcode', 'generate_qr.py')
action('echo', 'echo.py')
action('journal', 'show_journals.py')
action('list', 'list.py')
action('pending_feedback', 'pending_feedback.py')
action('report_feedback', 'report_feedback.py')

selector('true', '{"class":"Thing", "attr":"id", "test":"true"}')
selector('list', '{"class":"Failure", "test":"in", "value": "list"}')
selector('journal', '{"class":"Failure", "test":"in", "value": "journal"}')
selector('generate_qr', '{"class":"Failure", "attr":"id", "test":"=", "value": "generate_qr"}')
selector('for-me', '{"class":"SourceUser", "test":"is_concerned"}')
selector('personnal-for-me', '{"class":"Failure", "attr": "id", "test": "=", "value": "personnal-for-me"}')
selector('backoffice', '{"class":"Failure", "test": "in", "value": "toptop"}')
selector('not-backoffice', '{"class":"Selector", "id": "backoffice", "attr": "is_ok", "test": "false"}')
selector('pending-feedback', '{"class":"Failure", "attr": "id", "test": "=", "value": "pending-feedback"}')
selector('send-pending-feedback', '{"class":"Failure", "attr": "id", "test": "=", "value": "send-pending-feedback"}')
selector('with-pending-feedback', '[1, {"test": "pending_feedback"}, {"class":"Selector", "id": "backoffice", "attr": "is_ok", "test": "false"}]')

user_add('admin', 'thierry.excoffier')
user_add('admin', 'p2205989')

failure_update('toptop', value='')

failure_update('top', value='')
failure_add('toptop', 'top')

failure_update('list', value="Lister :", ask_confirm=False, restricted_to_group_id="admin")
failure_add('top', 'list')
failure_update('list-User', value="les utilisateurs", ask_confirm=False, restricted_to_group_id="admin", display_type=DisplayTypes.button)
failure_add('list', 'list-User')
failure_update('list-Failure', value="les pannes", ask_confirm=False, restricted_to_group_id="admin", display_type=DisplayTypes.button)
failure_add('list', 'list-Failure')
failure_update('list-Thing', value="les objets", ask_confirm=False, restricted_to_group_id="admin", display_type=DisplayTypes.button)
failure_add('list', 'list-Thing')
failure_update('list-Selector', value="les conditions", ask_confirm=False, restricted_to_group_id="admin", display_type=DisplayTypes.button)
failure_add('list', 'list-Selector')
failure_update('list-Dispatcher', value="les automatismes", ask_confirm=False, restricted_to_group_id="admin", display_type=DisplayTypes.button)
failure_add('list', 'list-Dispatcher')
failure_update('list-Action', value="les actions", ask_confirm=False, restricted_to_group_id="admin", display_type=DisplayTypes.button)
failure_add('list', 'list-Action')
failure_update('list-Concerned', value="qui est concerné", ask_confirm=False, restricted_to_group_id="admin", display_type=DisplayTypes.button)
failure_add('list', 'list-Concerned')
failure_update('list-Incident', value="les incidents en cours", ask_confirm=False, restricted_to_group_id="admin", display_type=DisplayTypes.button)
failure_add('list', 'list-Incident')

failure_update('journal', value="Afficher journal :", ask_confirm=False, restricted_to_group_id="admin")
failure_add('top', 'journal')
failure_update('journal-config', value="configuration", ask_confirm=False, restricted_to_group_id="admin", display_type=DisplayTypes.button)
failure_add('journal', 'journal-config')
failure_update('journal-incident', value="incidents", ask_confirm=False, restricted_to_group_id="admin", display_type=DisplayTypes.button)
failure_add('journal', 'journal-incident')

failure_update('misc', value="Divers :", ask_confirm=False, restricted_to_group_id="admin")
failure_add('top', 'misc')
failure_update('pending-feedback', value="Feedbacks de réparation en attente d'envoi", ask_confirm=False, restricted_to_group_id="admin", display_type=DisplayTypes.button)
failure_add('misc', 'pending-feedback')
failure_update('send-pending-feedback', value="Envoit le feedback de réparation aux utilisateurs", ask_confirm=False, restricted_to_group_id="admin", display_type=DisplayTypes.button)
failure_add('misc', 'send-pending-feedback')

failure_update('generate_qr_top', value='Générer un QR code :', ask_confirm=False, restricted_to_group_id="admin", display_type=DisplayTypes.text)
failure_add('top', 'generate_qr_top')
failure_update('generate_qr', value='Entrez le nom d\'une Thing', ask_confirm=True, restricted_to_group_id="admin", display_type=DisplayTypes.input)
failure_add('generate_qr_top', 'generate_qr')

failure_update('personnal', value="Ce qui me concerne :", ask_confirm=False, restricted_to_group_id="admin")
failure_add('top', 'personnal')
failure_update('personnal-for-me', value="Les incidents que je dois traiter", ask_confirm=False, restricted_to_group_id="admin", display_type=DisplayTypes.button)
failure_add('personnal', 'personnal-for-me')


thing_update('admin', failure_id="top", comment="Interface d'administration")

dispatcher_update('admin-list', action_id='list', selector_id='list')
dispatcher_update('admin-journal', action_id='journal', selector_id='journal')
dispatcher_update('pending-feedback', action_id='echo', selector_id='pending-feedback', incidents="with-pending-feedback")
dispatcher_update('send-pending-feedback', action_id='pending_feedback', selector_id='send-pending-feedback', incidents="with-pending-feedback")
dispatcher_update('generate-qr', action_id='generate_qrcode', selector_id='generate_qr')
dispatcher_update('personnal-for-me', action_id='echo', selector_id='personnal-for-me', incidents="for-me")

####################
# Edit configuration
####################
failure_add('toptop', 'edit')
failure_update('edit', value="Editeur de configuration :", ask_confirm=False, restricted_to_group_id="admin")

# Edit concerned
action('edit_concerned', 'edit_concerned.py')
selector('edit-concerned', '{"class":"Failure", "test":"in_or_equal", "value": "concerned"}')
failure_update('concerned', value="Concerned :", ask_confirm=False, restricted_to_group_id="admin")
failure_update('concerned-add', value="Add user to concerned", ask_confirm=False, restricted_to_group_id="admin", display_type=DisplayTypes.input)
failure_add('concerned', 'concerned-add')
failure_update('concerned-del', value="Remove user to concerned", ask_confirm=False, restricted_to_group_id="admin", display_type=DisplayTypes.input)
failure_add('concerned', 'concerned-del')
failure_add('edit', 'concerned')

failure_update('selector-update', value="Selector :", ask_confirm=False, restricted_to_group_id="admin", display_type=DisplayTypes.input)
failure_add('edit', 'selector-update')
dispatcher_update('edit-concerned', action_id='edit_concerned', selector_id='edit-concerned')

# Edit dispatcher
action('edit_dispatcher', 'edit_dispatcher.py')
selector('edit-dispatcher', '{"class":"Failure", "test":"in_or_equal", "value": "dispatcher"}')
failure_update('dispatcher', value="Dispatcher :", ask_confirm=False, restricted_to_group_id="admin")
dispatcher_update('edit-dispatcher', action_id='edit_dispatcher', selector_id='edit-dispatcher')

# Edit failure
action('edit_failure', 'edit_failure.py')
selector('edit-failure', '{"class":"Failure", "test":"in_or_equal", "value": "failure"}')
failure_update('failure', value="Dispatcher :", ask_confirm=False, restricted_to_group_id="admin")
dispatcher_update('edit-failure', action_id='edit_failure', selector_id='edit-failure')

# Edit selector
action('edit_selector', 'edit_selector.py')
selector('edit-selector', '{"class":"Failure", "test":"in_or_equal", "value": "selector"}')
failure_update('selector', value="Dispatcher :", ask_confirm=False, restricted_to_group_id="admin")
dispatcher_update('edit-selector', action_id='edit_selector', selector_id='edit-selector')

# Edit user
action('edit_user', 'edit_user.py')
selector('edit-user', '{"class":"Failure", "test":"in_or_equal", "value": "user"}')
failure_update('user', value="Dispatcher :", ask_confirm=False, restricted_to_group_id="admin")
dispatcher_update('edit-user', action_id='edit_user', selector_id='edit-user')

# Edit thing
action('edit_thing', 'edit_thing.py')
selector('edit-thing', '{"class":"Failure", "test":"in_or_equal", "value": "thing"}')
failure_update('thing', value="Dispatcher :", ask_confirm=False, restricted_to_group_id="admin")
dispatcher_update('edit-thing', action_id='edit_thing', selector_id='edit-thing')


# Admin is concerned by all reports. This display the reporting (not fix) feedback
dispatcher_update('report-feedback', action_id='report_feedback', selector_id='not-backoffice')
# 'z' to be the last dispatched
dispatcher_update('z-backoffice-close', action_id='close_auto', selector_id='backoffice')

concerned_add('not-backoffice', 'admin')

# selector('nautibus-hard', '[1, {"class":"Thing", "test": "inside", "value": "DOUA:Nautibus"}, [0, {"class":"Failure", "test": "in", "value": "MOUSE"}, {"class":"Failure", "test": "in", "value": "KEYBOARD"}, {"class":"Failure", "test": "in", "value": "SCREEN"}')
# concerned_add('nautibus-hard', 'admin-Nautibus-hard')
