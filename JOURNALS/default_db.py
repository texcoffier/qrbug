import pathlib
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

selector('true'     , '{"class":"Thing"     , "test":"true"}')
selector('admin'    , '{"class":"User"      , "test":"in"    , "value": "admin"}')
selector('system'   , '{"class":"SourceUser", "test":"inside", "value": "system"}')
selector('active'   , '[1, {"test":"active"}, {"class":"Selector", "attr": "is_ok", "test":"false", "id":"backoffice"}]', )
selector('for-me'   , '[1, {"test": "active"}, {"class":"SourceUser", "test":"is_for_user"}]')
selector('for-me-all','{"class":"SourceUser", "test":"is_for_user"}')
selector('for-thing', '{                      "test":"is_for_thing"}')
selector('for-thing-active', '[1, {"test": "active"}, {"test":"is_for_thing"}]')

###############################################################################
# General Backoffice
###############################################################################

user_update('admin')

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

failure_update('hours', value='')
failure_update('00:00', value='', allowed="system")
failure_update('01:00', value='', allowed="system")
failure_update('02:00', value='', allowed="system")
failure_update('03:00', value='', allowed="system")
failure_update('04:00', value='', allowed="system")
failure_update('05:00', value='', allowed="system")
failure_update('06:00', value='', allowed="system")
failure_update('07:00', value='', allowed="system")
failure_update('08:00', value='', allowed="system")
failure_update('09:00', value='', allowed="system")
failure_update('10:00', value='', allowed="system")
failure_update('11:00', value='', allowed="system")
failure_update('12:00', value='', allowed="system")
failure_update('13:00', value='', allowed="system")
failure_update('14:00', value='', allowed="system")
failure_update('15:00', value='', allowed="system")
failure_update('16:00', value='', allowed="system")
failure_update('17:00', value='', allowed="system")
failure_update('18:00', value='', allowed="system")
failure_update('19:00', value='', allowed="system")
failure_update('20:00', value='', allowed="system")
failure_update('21:00', value='', allowed="system")
failure_update('22:00', value='', allowed="system")
failure_update('23:00', value='', allowed="system")

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

failure_update('list'           , value="Lister"                , allowed="admin")
failure_update('list-User'      , value="Les utilisateurs"      , allowed="admin", display_type=Button)
failure_update('list-Failure'   , value="Les pannes"            , allowed="admin", display_type=Button)
failure_update('list-Thing'     , value="Les objets"            , allowed="admin", display_type=Button)
failure_update('list-Selector'  , value="Les conditions"        , allowed="admin", display_type=Button)
failure_update('list-Dispatcher', value="Les automatismes"      , allowed="admin", display_type=Button)
failure_update('list-Action'    , value="Les actions"           , allowed="admin", display_type=Button)
failure_update('list-Concerned' , value="Qui est concerné"      , allowed="admin", display_type=Button)
failure_update('list-Incident'  , value="Tous les incidents"    , allowed="admin", display_type=Button)

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

failure_update('journal'         , value="Afficher"                , allowed="admin")
failure_update('journal-config'  , value="Journal de configuration", allowed="admin", display_type=Button)
failure_update('journal-incident', value="Journal des incidents"   , allowed="admin", display_type=Button)

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

failure_update('misc'                 , value="Divers"                            , allowed="admin")
failure_update('pending-feedback'     , value="Feedbacks de réparation en attente", allowed="admin", display_type=Button)
failure_update('send-pending-feedback', value="Envoie le feedback de réparation"  , allowed="admin", display_type=Button)
failure_update('stats'                , value="Statistiques"                      , allowed="admin", display_type=Button)
failure_update('report-mail'          , value="Envoie mails de rappel à tous"     , allowed="admin", display_type=Button)

failure_add('misc', 'pending-feedback')
failure_add('misc', 'send-pending-feedback')
failure_add('misc', 'stats')
failure_add('misc', 'report-mail')
failure_add('top', 'misc')

action('pending_feedback', 'pending_feedback.py')  # Send user feedback for failure fix
action('stats'           , 'stats.py'           )  # Send user feedback for failure fix
action('report_mail'     , 'report_mail.py'     )  # Send mail to remind every active incident

selector('pending-feedback'     ,'{"class":"Failure", "test":"is", "value": "pending-feedback"}')
selector('send-pending-feedback','[0, {"class":"Failure", "test":"in", "value": "hours"}, {"class":"Failure", "test":"is", "value": "send-pending-feedback"}]')
selector('with-pending-feedback', '[1, {"test": "pending_feedback"}, {"class":"Selector", "id": "backoffice", "attr": "is_ok", "test": "false"}]')
selector('stats'                ,'{"class":"Failure", "test":"is", "value": "stats"}')
selector('report-mail'          ,'{"class":"Failure", "test":"is", "value": "report-mail"}')

dispatcher_update('pending-feedback'     , action_id='echo'            , selector_id='pending-feedback'     , incidents="with-pending-feedback")
dispatcher_update('send-pending-feedback', action_id='pending_feedback', selector_id='send-pending-feedback', incidents="with-pending-feedback")
dispatcher_update('stats'                , action_id='stats'           , selector_id='stats')


dispatcher_update('report_mail', action_id='report_mail', selector_id='report-mail', incidents='active')

#------------------------------------------------------------------------------
# Backoffice / personnal
#------------------------------------------------------------------------------

failure_update('personnal', value="Ce qui me concerne", allowed="admin")
failure_update('personnal-for-me', value="Les incidents que je dois traiter", allowed="admin", display_type=Button)
failure_update('personnal-for-me-all', value="Tous les incidents dont je m'occupe", allowed="admin", display_type=Button)

failure_add('personnal', 'personnal-for-me')
failure_add('personnal', 'personnal-for-me-all')
failure_add('top', 'personnal')

selector('personnal-for-me'     ,'{"class":"Failure", "test":"is", "value": "personnal-for-me"}')
selector('personnal-for-me-all' ,'{"class":"Failure", "test":"is", "value": "personnal-for-me-all"}')

dispatcher_update('personnal-for-me', action_id='echo', selector_id='personnal-for-me', incidents="for-me")
dispatcher_update('personnal-for-me-all', action_id='echo', selector_id='personnal-for-me-all', incidents="for-me-all")

###############################################################################
# Edit configuration
###############################################################################

failure_update('edit', value="API de l'éditeur de configuration, elle ne permet aucune modification mais affiche seulement les éléments modifiables pour chacun des types d'objet.", allowed="admin")
failure_add('backoffice', 'edit')

# The 'editor-api' thing displays the editors API
thing_update('editor-api', comment="Les API des éditeurs")
thing_add_failure('editor-api', 'edit')

# ---------------
# Edit concerned
# ---------------
failure_update('concerned'    , value="Concerned"                    , allowed="admin")
failure_update('concerned-add', value="Ajouter un utilisateur/groupe", allowed="admin", display_type=Datalist)
failure_update('concerned-del', value="Enlever un utilisateur/groupe", allowed="admin", display_type=Input)
failure_add('concerned', 'concerned-add')
failure_add('concerned', 'concerned-del')
failure_add('edit', 'concerned')

action('edit_concerned', 'edit_concerned.py')
selector('edit-concerned', '{"class":"Failure", "test":"in_or_equal", "value": "concerned"}')
dispatcher_update('edit-concerned', action_id='edit_concerned', selector_id='edit-concerned')

# ---------------
# Edit dispatcher
# ---------------
failure_update('dispatcher', value="Les dispatchers", allowed="admin")
failure_update('dispatcher-action_id', value="ID de l'action lancée", allowed="admin", display_type=Datalist)
failure_update('dispatcher-selector_id', value="ID du sélecteur", allowed="admin", display_type=Datalist)
failure_update('dispatcher-incidents', value="ID du sélecteur d'incidents", allowed="admin", display_type=Datalist)
failure_add('edit', 'dispatcher')
failure_add('dispatcher', 'dispatcher-action_id')
failure_add('dispatcher', 'dispatcher-selector_id')
failure_add('dispatcher', 'dispatcher-incidents')

action('edit_dispatcher', 'edit_dispatcher.py')
selector('edit-dispatcher', '{"class":"Failure", "test":"in_or_equal", "value": "dispatcher"}')
dispatcher_update('edit-dispatcher', action_id='edit_dispatcher', selector_id='edit-dispatcher')

# ---------------
# Edit failure
# ---------------
failure_update('failure', value="Les pannes", allowed="admin")
failure_update('failure-value', value="Intitulé", allowed="admin", display_type=Input)
failure_update('failure-display_type', value="Type d'affichage", allowed="admin", display_type=Display)
failure_update('failure-ask_confirm', value="Confirmation avant d'envoyer la panne", allowed="admin", display_type=Checkbox)
failure_update('failure-allowed', value="Groupe autorisé à déclaré la panne", allowed="admin", display_type=Input)
failure_add('edit', 'failure')
failure_add('failure', 'failure-value')
failure_add('failure', 'failure-display_type')
failure_add('failure', 'failure-ask_confirm')
failure_add('failure', 'failure-allowed')

action('edit_failure', 'edit_failure.py')
selector('edit-failure', '{"class":"Failure", "test":"in_or_equal", "value": "failure"}')
dispatcher_update('edit-failure', action_id='edit_failure', selector_id='edit-failure')

# ---------------
# Edit selector
# ---------------
failure_update('selector', value="Sélecteur d'incident", allowed="admin")
failure_update('selector-expression', value="Expression", allowed="admin", display_type=Input)
failure_add('edit', 'selector')
failure_add('selector', 'selector-expression')
failure_add('edit', 'selector-expression')

action('edit_selector', 'edit_selector.py')
selector('edit-selector', '{"class":"Failure", "test":"in_or_equal", "value": "selector"}')
dispatcher_update('edit-selector', action_id='edit_selector', selector_id='edit-selector')

# ---------------
# Edit user
# ---------------
failure_update('user', value="Utilisateur", allowed="admin")
failure_update('user-add-child', value="Enfant à ajouter", allowed="admin", display_type=Datalist)
failure_update('user-del-child', value="Enfant à retirer", allowed="admin", display_type=Datalist)
failure_update('user-add-parent', value="Parent à ajouter", allowed="admin", display_type=Datalist)
failure_update('user-del-parent', value="Parent à retirer", allowed="admin", display_type=Datalist)
failure_update('user-rename', value="Renommer", allowed="admin", display_type=Input)
failure_add('edit', 'user')
failure_add('user', 'user-add-child')
failure_add('user', 'user-del-child')
failure_add('user', 'user-add-parent')
failure_add('user', 'user-del-parent')
failure_add('user', 'user-rename')

action('edit_user', 'edit_user.py')
selector('edit-user', '{"class":"Failure", "test":"in_or_equal", "value": "user"}')
dispatcher_update('edit-user', action_id='edit_user', selector_id='edit-user')

# ---------------
# Edit thing
# ---------------
failure_update('thing', value="Chose", allowed="admin")
failure_update('thing-comment', value="Commentaire", allowed="admin", display_type=Input)
failure_update('thing-del-failure', value="Panne à enlever", allowed="admin", display_type=Input)
failure_update('thing-add-failure', value="Panne à ajouter", allowed="admin", display_type=Datalist)
failure_add('edit', 'thing')
failure_add('thing', 'thing-comment')
failure_add('thing', 'thing-del-failure')
failure_add('thing', 'thing-add-failure')

action('edit_thing', 'edit_thing.py')
selector('edit-thing', '{"class":"Failure", "test":"in_or_equal", "value": "thing"}')
dispatcher_update('edit-thing', action_id='edit_thing', selector_id='edit-thing')


failure_update('thing-incidents', value="Tous les incidents", allowed="admin")
failure_update('thing-incidents-active', value="Incidents actifs", allowed="admin")
failure_add('backoffice', 'thing-incidents')
failure_add('backoffice', 'thing-incidents-active')

selector('thing-incidents-active', '{"class":"Failure", "test":"is", "value": "thing-incidents-active"}')
dispatcher_update('incidents-active-for-thing', action_id='echo', selector_id='thing-incidents-active', incidents='for-thing-active')
selector('thing-incidents', '{"class":"Failure", "test":"is", "value": "thing-incidents"}')
dispatcher_update('incidents-for-thing', action_id='echo', selector_id='thing-incidents', incidents='for-thing')

# ---------------
# Edit action
# ---------------
failure_update('action', value="Action", allowed="admin")
failure_update('action-python_script', value="Le script Python à lancer", allowed="admin", display_type=Datalist)
failure_add('action', 'action-python_script')
failure_add('edit', 'action')

action('edit_action', 'edit_action.py')
selector('edit-action', '{"class":"Failure", "test":"in_or_equal", "value": "action"}')
dispatcher_update('edit-action', action_id='edit_action', selector_id='edit-action')

###############################################################################

# ---------------
# QRCode
# ---------------

failure_update('generate_qr', value='Générer un QR code :', allowed="admin", display_type=Text)
failure_add('backoffice', 'generate_qr')
failure_update('generate_qr', value='Entrez le nom d\'une Thing', ask_confirm=True, allowed="admin", display_type=Input)
for rows in (7, 8):
    for cols in (4, 5, 6):
        failure_update(f'generate_qr_{rows}x{cols}', value=f'En {rows}x{cols}', allowed="admin", display_type=Input)
        failure_add('generate_qr', f'generate_qr_{rows}x{cols}')

action('generate_qrcode', 'generate_qr.py')
selector('generate_qr','{"class":"Failure", "attr":"id", "test": "contains", "value": "generate_qr"}')
dispatcher_update('generate-qr', action_id='generate_qrcode', selector_id='generate_qr')

# ----------------------------------------------
# Define QRBug backtrace failure and dispatcher
# ----------------------------------------------

failure_update('backtrace', value='QRBug server backtrace')
selector('backtrace','{"class":"Failure", "test":"is", "value": "backtrace"}')
dispatcher_update('backtrace', action_id='report_mail', selector_id='backtrace')

# ----------------------------------------------
# Define a STATIC file getter
# ----------------------------------------------

action('get_file', 'get_file.py')
failure_update('get_file', value='QRBug server get_file')
failure_add('backoffice', 'get_file')
selector('get_file','{"class":"Failure", "test":"is", "value": "get_file"}')
dispatcher_update('get_file', action_id='get_file', selector_id='get_file')

failure_update('flow.html', value='Présentation de QRBug', display_type=Button)
failure_add('misc', 'flow.html')
selector('flow.html','{"class":"Failure", "test":"is", "value": "flow.html"}')
dispatcher_update('flow.html', action_id='get_file', selector_id='flow.html')

# ----------------------------------------------
# Messages
# ----------------------------------------------

failure_update('messages', value='Modifiez les messages affichés')
failure_add('backoffice', 'messages')

for message in pathlib.Path(MESSAGES).read_text(encoding='utf-8').split('\n'):
    failure_id, value = message.split(' ', 1)
    failure_update(failure_id, value=value)
    failure_add('messages', failure_id)

# selector('nautibus-hard', '[1, {"class":"Thing", "test": "inside", "value": "DOUA:Nautibus"}, [0, {"class":"Failure", "test": "in", "value": "MOUSE"}, {"class":"Failure", "test": "in", "value": "KEYBOARD"}, {"class":"Failure", "test": "in", "value": "SCREEN"}')
# concerned_add('nautibus-hard', 'admin-Nautibus-hard')
