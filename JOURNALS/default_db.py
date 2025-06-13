# pylint: disable=undefined-variable,line-too-long

# Link the action ID to the filename containing the action.
# The Python file containing the action is reloaded on any usage.
# So modification on the file are instantly taken into account.
action('none'            ,'none.py')              # Do nothing
action('close'           ,'close.py')             # The failure was fixed
action('echo'            ,'echo.py')              # Display incidents in user friendly form

# -----------------
# Common selectors
# -----------------

selector('true'  , '{"class":"Thing"     , "test":"true"}')
selector('for-me', '{"class":"SourceUser", "test":"is_concerned"}')

###############################################################################
# General Backoffice
###############################################################################

user_add('admin', 'thierry.excoffier')
user_add('admin', 'p2205989')

failure_update('backoffice', value='')
selector('backoffice'    ,'{"class":"Failure" ,                  "test":"in"   , "value":"backoffice"}')
selector('not-backoffice','{"class":"Selector", "attr": "is_ok", "test":"false", "id"   :"backoffice"}')

failure_update('top', value='')
failure_add('backoffice', 'top')

# The 'admin' thing displays the backoffice user interface
thing_update('admin', comment="Interface d'administration")
thing_add_failure('admin', "top")

# Display the reporting (not fix) feedback
action('report_feedback' ,'report_feedback.py')   # Send the report feedback to users
dispatcher_update('report-feedback', action_id='report_feedback', selector_id='not-backoffice')

# 'z' to be the last dispatched. It closes the API fake incident
action('close_auto', 'close_auto.py')
dispatcher_update('z-backoffice-close', action_id='close_auto', selector_id='backoffice')

# 'admin' is concerned by every incident
concerned_add('not-backoffice', 'admin')

###############################################################################
# Planified tasks
###############################################################################

failure_update('hours')
failure_update('00:00', restricted_to_group_id="system")
failure_update('01:00', restricted_to_group_id="system")
failure_update('02:00', restricted_to_group_id="system")
failure_update('03:00', restricted_to_group_id="system")
failure_update('04:00', restricted_to_group_id="system")
failure_update('05:00', restricted_to_group_id="system")
failure_update('06:00', restricted_to_group_id="system")
failure_update('07:00', restricted_to_group_id="system")
failure_update('08:00', restricted_to_group_id="system")
failure_update('09:00', restricted_to_group_id="system")
failure_update('10:00', restricted_to_group_id="system")
failure_update('11:00', restricted_to_group_id="system")
failure_update('12:00', restricted_to_group_id="system")
failure_update('13:00', restricted_to_group_id="system")
failure_update('14:00', restricted_to_group_id="system")
failure_update('15:00', restricted_to_group_id="system")
failure_update('16:00', restricted_to_group_id="system")
failure_update('17:00', restricted_to_group_id="system")
failure_update('18:00', restricted_to_group_id="system")
failure_update('19:00', restricted_to_group_id="system")
failure_update('20:00', restricted_to_group_id="system")
failure_update('21:00', restricted_to_group_id="system")
failure_update('22:00', restricted_to_group_id="system")
failure_update('23:00', restricted_to_group_id="system")

failure_add('hours', '00:00')
failure_add('hours', '01:00')
failure_add('hours', '02:00')
failure_add('hours', '03:00')
failure_add('hours', '04:00')
failure_add('hours', '05:00')
failure_add('hours', '06:00')
failure_add('hours', '07:00')
failure_add('hours', '08:00')
failure_add('hours', '09:00')
failure_add('hours', '10:00')
failure_add('hours', '11:00')
failure_add('hours', '12:00')
failure_add('hours', '13:00')
failure_add('hours', '14:00')
failure_add('hours', '15:00')
failure_add('hours', '16:00')
failure_add('hours', '17:00')
failure_add('hours', '18:00')
failure_add('hours', '19:00')
failure_add('hours', '20:00')
failure_add('hours', '21:00')
failure_add('hours', '22:00')
failure_add('hours', '23:00')
failure_add('backoffice', 'hours') # To receive auto-close

#------------------------------------------------------------------------------
# Backoffice / lists
#------------------------------------------------------------------------------

failure_update('list'           , value="Lister"                , restricted_to_group_id="admin")
failure_update('list-User'      , value="Les utilisateurs"      , restricted_to_group_id="admin", display_type=Button)
failure_update('list-Failure'   , value="Les pannes"            , restricted_to_group_id="admin", display_type=Button)
failure_update('list-Thing'     , value="Les objets"            , restricted_to_group_id="admin", display_type=Button)
failure_update('list-Selector'  , value="Les conditions"        , restricted_to_group_id="admin", display_type=Button)
failure_update('list-Dispatcher', value="Les automatismes"      , restricted_to_group_id="admin", display_type=Button)
failure_update('list-Action'    , value="Les actions"           , restricted_to_group_id="admin", display_type=Button)
failure_update('list-Concerned' , value="Qui est concerné"      , restricted_to_group_id="admin", display_type=Button)
failure_update('list-Incident'  , value="Les incidents en cours", restricted_to_group_id="admin", display_type=Button)

failure_add('list', 'list-User')
failure_add('list', 'list-Failure')
failure_add('list', 'list-Thing')
failure_add('list', 'list-Selector')
failure_add('list', 'list-Dispatcher')
failure_add('list', 'list-Action')
failure_add('list', 'list-Concerned')
failure_add('list', 'list-Incident')
failure_add('top', 'list')

# Use the same selector and dispatcher for all the failure in 'list'
# The 'list' action will check the failure ID to to the right thing.
action('list', 'list.py')
selector('list', '{"class":"Failure", "test":"in", "value": "list"}')
dispatcher_update('admin-list', action_id='list', selector_id='list')

#------------------------------------------------------------------------------
# Backoffice / journals
#------------------------------------------------------------------------------

failure_update('journal'         , value="Afficher"                , restricted_to_group_id="admin")
failure_update('journal-config'  , value="Journal de configuration", restricted_to_group_id="admin", display_type=Button)
failure_update('journal-incident', value="Journal des incidents"   , restricted_to_group_id="admin", display_type=Button)

failure_add('journal', 'journal-config')
failure_add('journal', 'journal-incident')
failure_add('top', 'journal')

# Use the same selector and dispatcher for all the journal in 'journal'
# The 'journal' action will check the failure ID to to the right thing.
action('journal', 'show_journals.py')
selector('journal', '{"class":"Failure", "test":"in", "value": "journal"}')
dispatcher_update('admin-journal', action_id='journal', selector_id='journal')

#------------------------------------------------------------------------------
# Backoffice / misc
#------------------------------------------------------------------------------

failure_update('misc'                 , value="Divers"                            , restricted_to_group_id="admin")
failure_update('pending-feedback'     , value="Feedbacks de réparation en attente", restricted_to_group_id="admin", display_type=Button)
failure_update('send-pending-feedback', value="Envoie le feedback de réparation"  , restricted_to_group_id="admin", display_type=Button)

failure_add('misc', 'pending-feedback')
failure_add('misc', 'send-pending-feedback')
failure_add('top', 'misc')

action('pending_feedback', 'pending_feedback.py')  # Send user feedback for failure fix
selector('pending-feedback'     ,'{"class":"Failure", "test":"is", "value": "pending-feedback"}')
selector('send-pending-feedback','[0, {"class":"Failure", "test":"in", "value": "hours"}, {"class":"Failure", "test":"is", "value": "send-pending-feedback"}]')
selector('with-pending-feedback', '[1, {"test": "pending_feedback"}, {"class":"Selector", "id": "backoffice", "attr": "is_ok", "test": "false"}]')
dispatcher_update('pending-feedback'     , action_id='echo'            , selector_id='pending-feedback'     , incidents="with-pending-feedback")
dispatcher_update('send-pending-feedback', action_id='pending_feedback', selector_id='send-pending-feedback', incidents="with-pending-feedback")

#------------------------------------------------------------------------------
# Backoffice / personnal
#------------------------------------------------------------------------------

failure_update('personnal', value="Ce qui me concerne", restricted_to_group_id="admin")
failure_update('personnal-for-me', value="Les incidents que je dois traiter", restricted_to_group_id="admin", display_type=Button)

failure_add('personnal', 'personnal-for-me')
failure_add('top', 'personnal')

selector('personnal-for-me'     ,'{"class":"Failure", "test":"is", "value": "personnal-for-me"}')
dispatcher_update('personnal-for-me', action_id='echo', selector_id='personnal-for-me', incidents="for-me")

###############################################################################
# Edit configuration
###############################################################################

failure_update('edit', value="API de l'éditeur de configuration, elle ne permet aucune modification mais affiche seulement les éléments modifiables pour chacun des types d'objet.", restricted_to_group_id="admin")
failure_add('backoffice', 'edit')

# The 'editor-api' thing displays the editors API
thing_update('editor-api', comment="Les API des éditeurs")
thing_add_failure('editor-api', 'edit')

# ---------------
# Edit concerned
# ---------------
failure_update('concerned'    , value="Concerned"                    , restricted_to_group_id="admin")
failure_update('concerned-add', value="Ajouter un utilisateur/groupe", restricted_to_group_id="admin", display_type=Input)
failure_update('concerned-del', value="Enlever un utilisateur/groupe", restricted_to_group_id="admin", display_type=Input)
failure_add('concerned', 'concerned-add')
failure_add('concerned', 'concerned-del')
failure_add('edit', 'concerned')

action('edit_concerned', 'edit_concerned.py')
selector('edit-concerned', '{"class":"Failure", "test":"in_or_equal", "value": "concerned"}')
dispatcher_update('edit-concerned', action_id='edit_concerned', selector_id='edit-concerned')

# ---------------
# Edit dispatcher
# ---------------
failure_update('dispatcher', value="Les dispatchers", restricted_to_group_id="admin")
failure_add('edit', 'dispatcher')

action('edit_dispatcher', 'edit_dispatcher.py')
selector('edit-dispatcher', '{"class":"Failure", "test":"in_or_equal", "value": "dispatcher"}')
dispatcher_update('edit-dispatcher', action_id='edit_dispatcher', selector_id='edit-dispatcher')

# ---------------
# Edit failure
# ---------------
failure_update('failure', value="Les pannes", restricted_to_group_id="admin")
failure_add('edit', 'failure')

action('edit_failure', 'edit_failure.py')
selector('edit-failure', '{"class":"Failure", "test":"in_or_equal", "value": "failure"}')
dispatcher_update('edit-failure', action_id='edit_failure', selector_id='edit-failure')

# ---------------
# Edit selector
# ---------------
failure_update('selector', value="Sélecteur d'incident", restricted_to_group_id="admin")
failure_add('edit', 'selector')

action('edit_selector', 'edit_selector.py')
selector('edit-selector', '{"class":"Failure", "test":"in_or_equal", "value": "selector"}')
dispatcher_update('edit-selector', action_id='edit_selector', selector_id='edit-selector')

# ---------------
# Edit user
# ---------------
failure_update('user', value="Utilisateur", restricted_to_group_id="admin")
failure_add('edit', 'user')

action('edit_user', 'edit_user.py')
selector('edit-user', '{"class":"Failure", "test":"in_or_equal", "value": "user"}')
dispatcher_update('edit-user', action_id='edit_user', selector_id='edit-user')

# ---------------
# Edit thing
# ---------------
failure_update('thing', value="Chose", restricted_to_group_id="admin")
failure_add('edit', 'thing')

action('edit_thing', 'edit_thing.py')
selector('edit-thing', '{"class":"Failure", "test":"in_or_equal", "value": "thing"}')
dispatcher_update('edit-thing', action_id='edit_thing', selector_id='edit-thing')

# ---------------
# Edit action
# ---------------
failure_update('action', value="Action", restricted_to_group_id="admin")
failure_update('action-python_script', value="Le script Python à lancer", restricted_to_group_id="admin", display_type=Input)
failure_add('action', 'action-python_script')
failure_add('edit', 'action')

action('edit_action', 'edit_action.py')
selector('edit-action', '{"class":"Failure", "test":"in_or_equal", "value": "action"}')
dispatcher_update('edit-action', action_id='edit_action', selector_id='edit-action')

###############################################################################

# ---------------
# QRCode
# ---------------

failure_update('generate_qr_top', value='Générer un QR code :', ask_confirm=False, restricted_to_group_id="admin", display_type=Text)
failure_add('top', 'generate_qr_top')
failure_update('generate_qr', value='Entrez le nom d\'une Thing', ask_confirm=True, restricted_to_group_id="admin", display_type=Input)
failure_add('generate_qr_top', 'generate_qr')
for rows in range(4, 9):
    for cols in range(4, 9):
        failure_update(f'generate_qr_{rows}x{cols}', value=f'En {rows}x{cols}', ask_confirm=True, restricted_to_group_id="admin", display_type=Input)
        failure_add('generate_qr_top', f'generate_qr_{rows}x{cols}')
thing_update('QR_GEN')
thing_add_failure('QR_GEN', 'generate_qr_top')

action('generate_qrcode', 'generate_qr.py')
selector('generate_qr','{"class":"Failure", "attr":"id", "test": "contains", "value": "generate_qr"}')
dispatcher_update('generate-qr', action_id='generate_qrcode', selector_id='generate_qr')



# selector('nautibus-hard', '[1, {"class":"Thing", "test": "inside", "value": "DOUA:Nautibus"}, [0, {"class":"Failure", "test": "in", "value": "MOUSE"}, {"class":"Failure", "test": "in", "value": "KEYBOARD"}, {"class":"Failure", "test": "in", "value": "SCREEN"}')
# concerned_add('nautibus-hard', 'admin-Nautibus-hard')
