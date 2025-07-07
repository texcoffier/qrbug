import pathlib
# pylint: disable=undefined-variable,line-too-long

# Link the action ID to the filename containing the action.
# The Python file containing the action is reloaded on any usage.
# So modification on the file are instantly taken into account.
action('none'            ,'none.py')              # Do nothing
action('close'           ,'close.py')             # The failure was fixed
action('echo'            ,'echo.py')              # Display incidents in user friendly form

# -----------------
# Default User tree
# -----------------

# Group for users with all the rights, for developper
user_update('root')
user_update('nobody')

user_update('admin') # Allowed all administrative rights
user_add('admin', 'root')

user_update('admin-backtrace') # Concerned by backtraces
user_add('admin-backtrace', 'root')

user_update('admin-user') # Allowed to edit all users
user_add('admin-user', 'root')
user_add('admin-user', 'admin')

user_update('admin-thing') # Allowed to edit things
user_add('admin-thing', 'root')
user_add('admin-thing', 'admin')

# -----------------
# Common selectors
# -----------------

selector('true'            , '{                      "test":"True"}')
selector('root'            , '{"class":"SourceUser", "test":"in"    , "value": "root"}')
selector('admin'           , '{"class":"SourceUser", "test":"in"    , "value": "admin"}')
selector('admin-backtrace' , '{"class":"SourceUser", "test":"in"    , "value": "admin-backtrace"}')
selector('admin-user'      , '{"class":"SourceUser", "test":"in_or_equal", "value": "admin-user"}')
selector('admin-thing'     , '{"class":"SourceUser", "test":"in_or_equal", "value": "admin-thing"}')
selector('system'          , '{"class":"SourceUser", "test":"in"    , "value": "system"}')
selector('active'          , '[1, {"test":"active"}, {"class":"Selector", "attr": "is_ok", "test":"false", "id":"backoffice"}]', )
selector('for-me'          , '[1, {"test": "active"}, {"class":"SourceUser", "test":"is_for_user"}]')
selector('for-me-all'      , '{"class":"SourceUser", "test":"is_for_user"}')
selector('for-thing'       , '{                      "test":"is_for_thing"}')
selector('for-thing-active', '[1, {"test": "active"}, {"test":"is_for_thing"}]')

###############################################################################
# General Backoffice
###############################################################################

failure_update('backoffice', value='')
selector('backoffice'    ,'{"class":"SourceFailure",             "test":"in_or_equal", "value":"backoffice"}')
selector('not-backoffice','{"class":"Selector", "attr": "is_ok", "test":"false", "id"   :"backoffice"}')

failure_update('top', value='')
failure_add('backoffice', 'top')

# The 'GUI' thing displays the backoffice user interface
thing_update('GUI', comment="Interface d'administration")
thing_add_failure('GUI', "top")

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
failure_update('00:00', value='')
failure_update('01:00', value='')
failure_update('02:00', value='')
failure_update('03:00', value='')
failure_update('04:00', value='')
failure_update('05:00', value='')
failure_update('06:00', value='')
failure_update('07:00', value='')
failure_update('08:00', value='')
failure_update('09:00', value='')
failure_update('10:00', value='')
failure_update('11:00', value='')
failure_update('12:00', value='')
failure_update('13:00', value='')
failure_update('14:00', value='')
failure_update('15:00', value='')
failure_update('16:00', value='')
failure_update('17:00', value='')
failure_update('18:00', value='')
failure_update('19:00', value='')
failure_update('20:00', value='')
failure_update('21:00', value='')
failure_update('22:00', value='')
failure_update('23:00', value='')

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

failure_update('list'           , value="Lister"            )
failure_update('list-User'      , value="Les utilisateurs"  , display_type=Button)
failure_update('list-Failure'   , value="Les pannes"        , display_type=Button)
failure_update('list-Thing'     , value="Les objets"        , display_type=Button)
failure_update('list-Selector'  , value="Les conditions"    , display_type=Button)
failure_update('list-Dispatcher', value="Les automatismes"  , display_type=Button)
failure_update('list-Action'    , value="Les actions"       , display_type=Button)
failure_update('list-Concerned' , value="Qui est concerné"  , display_type=Button)
failure_update('list-Incident'  , value="Tous les incidents", display_type=Button)

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
selector('list', '''[1,
    {"class":"SourceFailure", "test":"in", "value": "list"},
    {"class":"SourceUser"   , "test":"in_or_equal", "value": "admin"}
    ]''')
dispatcher_update('admin-list', action_id='list', selector_id='list')

#------------------------------------------------------------------------------
# Backoffice / journals
#------------------------------------------------------------------------------

failure_update('journal'         , value="Afficher"                )
failure_update('journal-config'  , value="Journal de configuration", display_type=Button)
failure_update('journal-incident', value="Journal des incidents"   , display_type=Button)

failure_add('journal', 'journal-config')
failure_add('journal', 'journal-incident')
failure_add('top', 'journal')

# Use the same selector and dispatcher for all the journal in 'journal'
# The 'journal' action will check the failure ID to to the right thing.
action('journal', 'show_journals.py')
selector('journal', '''[1,
    {"class":"SourceFailure", "test":"in", "value": "journal"},
    {"class":"SourceUser"   , "test":"in_or_equal", "value": "admin"}
    ]''')
dispatcher_update('admin-journal', action_id='journal', selector_id='journal')

#------------------------------------------------------------------------------
# Backoffice / misc
#------------------------------------------------------------------------------

failure_update('misc'                 , value="Divers"                            )
failure_update('pending-feedback'     , value="Feedbacks de réparation en attente", display_type=Button)
failure_update('send-pending-feedback', value="Envoie le feedback de réparation"  , display_type=Button)
failure_update('stats'                , value="Statistiques"                      , display_type=Button)
failure_update('report-mail'          , value="Envoie mails de rappel à tous"     , display_type=Button)
failure_update('check-selectors'      , value="Vérifie les sélecteurs"            , display_type=Button)

failure_add('misc', 'pending-feedback')
failure_add('misc', 'send-pending-feedback')
failure_add('misc', 'stats')
failure_add('misc', 'check-selectors')
failure_add('misc', 'report-mail')
failure_add('top', 'misc')

action('pending_feedback', 'pending_feedback.py')  # Send user feedback for failure fix
action('stats'           , 'stats.py'           )
action('check-selectors' , 'check_selectors.py' )
action('report_mail'     , 'report_mail.py'     )  # Send mail to remind every active incident


selector('hours', '''[1,
    {"class":"SourceFailure", "test":"in", "value": "hours"},
    {"class":"SourceUser"   , "test":"is", "value": "system"}
    ]''')

selector('send-feedback', '''[1,
    {"class":"SourceFailure", "test":"is"         , "value": "send-pending-feedback"},
    {"class":"SourceUser"   , "test":"in_or_equal", "value": "root"}
    ]''')

selector('send-pending-feedback','''[0,
    {"class":"Selector", "id": "hours"        , "attr":"is_ok", "test": "true"},
    {"class":"Selector", "id": "send-feedback", "attr":"is_ok", "test": "true"}
    ]''')
selector('with-pending-feedback', '[1, {"test": "pending_feedback"}, {"class":"Selector", "id": "backoffice", "attr": "is_ok", "test": "false"}]')

selector('pending-feedback', '''[1,
    {"class":"SourceFailure", "test":"is", "value": "pending-feedback"},
    {"class":"SourceUser"   , "test":"in_or_equal", "value": "admin"}
    ]''')
selector('stats', '''[1,
    {"class":"SourceFailure", "test":"is", "value": "stats"},
    {"class":"SourceUser"   , "test":"in_or_equal", "value": "admin"}
    ]''')
selector('check-selectors', '''[1,
    {"class":"SourceFailure", "test":"is", "value": "check-selectors"},
    {"class":"SourceUser"   , "test":"in_or_equal", "value": "admin"}
    ]''')
selector('report-mail', '''[1,
    {"class":"SourceFailure", "test":"is", "value": "report-mail"},
    {"class":"SourceUser"   , "test":"in_or_equal", "value": "admin"}
    ]''')


dispatcher_update('pending-feedback'     , action_id='echo'            , selector_id='pending-feedback'     , incidents="with-pending-feedback")
dispatcher_update('send-pending-feedback', action_id='pending_feedback', selector_id='send-pending-feedback', incidents="with-pending-feedback")
dispatcher_update('stats'                , action_id='stats'           , selector_id='stats')
dispatcher_update('check-selectors'      , action_id='check-selectors' , selector_id='check-selectors')


dispatcher_update('report_mail', action_id='report_mail', selector_id='report-mail', incidents='active')

#------------------------------------------------------------------------------
# Backoffice / personnal
#------------------------------------------------------------------------------

failure_update('personnal'           , value="Ce qui me concerne")
failure_update('personnal-for-me'    , value="Les incidents que je dois traiter"  , display_type=Button)
failure_update('personnal-for-me-all', value="Tous les incidents dont je m'occupe", display_type=Button)

failure_add('personnal', 'personnal-for-me')
failure_add('personnal', 'personnal-for-me-all')
failure_add('top', 'personnal')

# Anybody can see its 'incidents'.

selector('personnal-for-me'     ,'{"class":"SourceFailure", "test":"is", "value": "personnal-for-me"}')
selector('personnal-for-me-all' ,'{"class":"SourceFailure", "test":"is", "value": "personnal-for-me-all"}')

dispatcher_update('personnal-for-me'    , action_id='echo', selector_id='personnal-for-me'    , incidents="for-me")
dispatcher_update('personnal-for-me-all', action_id='echo', selector_id='personnal-for-me-all', incidents="for-me-all")

###############################################################################
# Edit configuration
###############################################################################

failure_update('edit', value="API de l'éditeur de configuration, elle ne permet aucune modification mais affiche seulement les éléments modifiables pour chacun des types d'objet.")
failure_add('backoffice', 'edit')

# ---------------
# Edit concerned
# ---------------
failure_update('concerned'    , value="Concerned"                    )
failure_update('concerned-add', value="Ajouter un utilisateur/groupe", display_type=Datalist)
failure_update('concerned-del', value="Enlever un utilisateur/groupe", display_type=Input)
failure_add('concerned', 'concerned-add')
failure_add('concerned', 'concerned-del')
failure_add('edit', 'concerned')

action('edit_concerned', 'edit_concerned.py')
selector('edit-concerned', '''[1,
    {"class":"SourceFailure", "test":"in_or_equal", "value": "concerned"},
    {"class":"SourceUser"   , "test":"in_or_equal", "value": "admin"}
    ]''')
dispatcher_update('edit-concerned', action_id='edit_concerned', selector_id='edit-concerned')

# ---------------
# Edit dispatcher
# ---------------
failure_update('dispatcher', value="Les dispatchers")
failure_update('dispatcher-action_id', value="ID de l'action lancée", display_type=Datalist)
failure_update('dispatcher-selector_id', value="ID du sélecteur", display_type=Datalist)
failure_update('dispatcher-incidents', value="ID du sélecteur d'incidents", display_type=Datalist)
failure_add('edit', 'dispatcher')
failure_add('dispatcher', 'dispatcher-action_id')
failure_add('dispatcher', 'dispatcher-selector_id')
failure_add('dispatcher', 'dispatcher-incidents')

action('edit_dispatcher', 'edit_dispatcher.py')
selector('edit-dispatcher', '''[1,
    {"class":"SourceFailure", "test":"in_or_equal", "value": "dispatcher"},
    {"class":"SourceUser"   , "test":"in_or_equal", "value": "admin"}
    ]''')
dispatcher_update('edit-dispatcher', action_id='edit_dispatcher', selector_id='edit-dispatcher')

# ---------------
# Edit failure
# ---------------
failure_update('failure'             , value="Les pannes"                           )
failure_update('failure-value'       , value="Intitulé"                             , display_type=Input)
failure_update('failure-display_type', value="Type d'affichage"                     , display_type=Display)
failure_update('failure-ask_confirm' , value="Confirmation avant d'envoyer la panne", display_type=Checkbox)
failure_add('edit', 'failure')
failure_add('failure', 'failure-value')
failure_add('failure', 'failure-display_type')
failure_add('failure', 'failure-ask_confirm')

action('edit_failure', 'edit_failure.py')
selector('edit-failure', '''[1,
    {"class":"SourceFailure", "test":"in_or_equal", "value": "failure"},
    {"class":"SourceUser"   , "test":"in_or_equal", "value": "admin"}
    ]''')
dispatcher_update('edit-failure', action_id='edit_failure', selector_id='edit-failure')

# ---------------
# Edit selector
# ---------------
failure_update('selector', value="Sélecteur d'incident")
failure_update('selector-expression', value="Expression", display_type=Input)
failure_add('edit', 'selector')
failure_add('selector', 'selector-expression')
failure_add('edit', 'selector-expression')

action('edit_selector', 'edit_selector.py')
selector('edit-selector', '''[1,
    {"class":"SourceFailure", "test":"in_or_equal", "value": "selector"},
    {"class":"SourceUser"   , "test":"in_or_equal", "value": "admin"}
    ]''')
dispatcher_update('edit-selector', action_id='edit_selector', selector_id='edit-selector')

# ---------------
# Edit user
# ---------------
failure_update('user', value="Utilisateur")
failure_update('user-add-child' , value="Ajouter un enfant", display_type=Datalist)
failure_update('user-del-child' , value="Enlever d'ici"    , display_type=Button)
failure_add('edit', 'user')
failure_add('user', 'user-add-child')
failure_add('user', 'user-del-child')

action('edit_user', 'edit_user.py')
selector('edit-user', '''[1,
    {"class":"SourceFailure", "test":"in_or_equal", "value": "user"},
    {"class":"SourceUser"   , "test":"in_or_equal", "value": "admin-user"}
    ]''')
dispatcher_update('edit-user', action_id='edit_user', selector_id='edit-user')

# ---------------
# Edit thing
# ---------------
failure_update('thing'            , value="Chose"          )
failure_update('thing-comment'    , value="Commentaire"    , display_type=Input)
failure_update('thing-del-failure', value="Panne à enlever", display_type=Input)
failure_update('thing-add-failure', value="Panne à ajouter", display_type=Datalist)
failure_add('edit', 'thing')
failure_add('thing', 'thing-comment')
failure_add('thing', 'thing-del-failure')
failure_add('thing', 'thing-add-failure')

action('edit_thing', 'edit_thing.py')
selector('edit-thing', '''[1,
    {"class":"SourceFailure", "test":"in_or_equal", "value": "thing"},
    {"class":"SourceUser"   , "test":"in_or_equal", "value": "admin-thing"}
    ]''')
dispatcher_update('edit-thing', action_id='edit_thing', selector_id='edit-thing')


failure_update('thing-incidents'       , value="Tous les incidents")
failure_update('thing-incidents-active', value="Incidents actifs")
failure_add('backoffice', 'thing-incidents')
failure_add('backoffice', 'thing-incidents-active')

selector('thing-incidents-active', '''[1,
    {"class":"SourceFailure", "test":"is", "value": "thing-incidents-active"},
    {"class":"SourceUser"   , "test":"in_or_equal", "value": "admin-thing"}
    ]''')
dispatcher_update('incidents-active-for-thing', action_id='echo', selector_id='thing-incidents-active', incidents='for-thing-active')
selector('thing-incidents', '''[1,
    {"class":"SourceFailure", "test":"is", "value": "thing-incidents"},
    {"class":"SourceUser"   , "test":"in_or_equal", "value": "admin-thing"}
    ]''')
dispatcher_update('incidents-for-thing', action_id='echo', selector_id='thing-incidents', incidents='for-thing')

# ---------------
# Edit action
# ---------------
failure_update('action', value="Action")
failure_update('action-python_script', value="Le script Python à lancer", display_type=Datalist)
failure_add('action', 'action-python_script')
failure_add('edit', 'action')

action('edit_action', 'edit_action.py')
selector('edit-action', '''[1,
    {"class":"SourceFailure", "test":"in_or_equal", "value": "action"},
    {"class":"SourceUser"   , "test":"in_or_equal", "value": "admin"}
    ]''')
dispatcher_update('edit-action', action_id='edit_action', selector_id='edit-action')

###############################################################################

# ---------------
# QRCode
# ---------------

failure_update('generate_qr', value='Générer un QR code de la taille indiquée')
failure_add('backoffice', 'generate_qr')
for rows in (7, 8):
    for cols in (4, 5, 6):
        failure_update(f'generate_qr_{rows}x{cols}', value=f'En {rows}x{cols}', display_type=Input)
        failure_add('generate_qr', f'generate_qr_{rows}x{cols}')

action('generate_qrcode', 'generate_qr.py')
selector('generate_qr', '''[1,
    {"class":"SourceFailure", "test":"in_or_equal", "value": "generate_qr"},
    {"class":"SourceUser"   , "test":"in_or_equal", "value": "admin"}
    ]''')
dispatcher_update('generate-qr', action_id='generate_qrcode', selector_id='generate_qr')

# ----------------------------------------------
# Define QRBug backtrace failure and dispatcher
# ----------------------------------------------

failure_update('backtrace', value='QRBug server backtrace')
selector('backtrace', '''[1,
    {"class":"SourceFailure", "test":"is", "value": "backtrace"},
    {"class":"SourceUser"   , "test":"is", "value": ""}
    ]''')
concerned_add('backtrace', 'admin-backtrace')
dispatcher_update('backtrace', action_id='report_mail', selector_id='backtrace')

# ----------------------------------------------
# Define a STATIC file getter
# ----------------------------------------------

action('get_file', 'get_file.py')
failure_update('get_file', value='QRBug server get_file')
failure_add('backoffice', 'get_file')
selector('get_file','{"class":"SourceFailure", "test":"is", "value": "get_file"}')
dispatcher_update('get_file', action_id='get_file', selector_id='get_file')

failure_update('flow.html', value='Présentation de QRBug', display_type=Button)
failure_add('misc', 'flow.html')
selector('flow.html','{"class":"SourceFailure", "test":"is", "value": "flow.html"}')
dispatcher_update('flow.html', action_id='get_file', selector_id='flow.html')

# ----------------------------------------------
# Journals reload
# ----------------------------------------------
failure_update('reload_journals', value='Recharger les journaux de configuration', display_type=Button)
failure_add('misc', 'reload_journals')
selector('reload_journals', '{"class":"SourceFailure", "test":"is", "value": "reload_journals"}')
selector('reload_journals', '''[1,
    {"class":"SourceFailure", "test":"is", "value": "reload_journals"},
    {"class":"SourceUser"   , "test":"in_or_equal", "value": "root"}
    ]''')
action('reload_journals', 'reload_journals.py')
dispatcher_update('reload_journals', action_id='reload_journals', selector_id='reload_journals')

# ----------------------------------------------
# Require logins
# ----------------------------------------------

selector('require-login', '''[0,
    {"class":"SourceFailure", "test":"in_or_equal", "value": "backoffice"}
]''')

# ----------------------------------------------
# Messages
# ----------------------------------------------

failure_update('messages', value='Modifiez les messages affichés')
failure_add('backoffice', 'messages')

for message in pathlib.Path(MESSAGES).read_text(encoding='utf-8').split('\n'):
    failure_id, value = message.split(' ', 1)
    failure_update(failure_id, value=value)
    failure_add('messages', failure_id)
