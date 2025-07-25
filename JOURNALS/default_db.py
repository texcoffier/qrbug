import pathlib
# pylint: disable=undefined-variable,line-too-long

# To prevent name collision et intuitive reading,
# the predefined ID are prefixed by:
#    * «|» if Selector is an incident filter.
#    * «?» for Selector
#    * «#» for Thing
#    * «!» for Dispatcher
#    * «$» for Failure
#    * «@» for User


# Link the action ID to the filename containing the action.
# The Python file containing the action is reloaded on any usage.
# So modification on the file are instantly taken into account.
action('close'           ,'close.py')             # The failure was fixed
action('echo'            ,'echo.py')              # Display incidents in user friendly form

# -----------------
# Default User tree
# -----------------

# Group for users with all the rights, for developper
user_update('@root')
user_update('@nobody')

user_update('@admin') # Allowed all administrative rights
user_add('@admin', '@root')

user_update('@admin-backtrace') # Concerned by backtraces
user_add('@admin-backtrace', '@root')

user_update('@admin-user') # Allowed to edit all users
user_add('@admin-user', '@root')
user_add('@admin-user', '@admin')

user_update('@admin-thing') # Allowed to edit things
user_add('@admin-thing', '@root')
user_add('@admin-thing', '@admin')

user_update('@fixer') # Allowed to fix things
user_update('@admin-or-fixer')
user_add('@admin-or-fixer', '@admin')
user_add('@admin-or-fixer', '@fixer')

# -----------------
# Common selectors
# -----------------

selector('?true'           , '{                      "test":"True"}')
selector('?false'          , '{                      "test":"False"}')
selector('?root'           , '{"class":"SourceUser", "test":"in_or_equal", "value": "@root"}')
selector('?admin'          , '{"class":"SourceUser", "test":"in_or_equal", "value": "@admin"}')
selector('?admin-backtrace', '{"class":"SourceUser", "test":"in_or_equal", "value": "@admin-backtrace"}')
selector('?admin-user'     , '{"class":"SourceUser", "test":"in_or_equal", "value": "@admin-user"}')
selector('?admin-thing'    , '{"class":"SourceUser", "test":"in_or_equal", "value": "@admin-thing"}')
selector('?system'         , '{"class":"SourceUser", "test":"in_or_equal", "value": "@system"}')
selector('|active'         , '[1, {"test":"active"}, {"class":"Selector", "attr": "is_ok", "test":"false", "id":"|backoffice"}]', )
selector('|for-me'         , '[1, {"test":"active"}, {"class":"SourceUser", "test":"is_for_user"}]')
selector('|for-me-all'     , '{"class":"SourceUser", "test":"is_for_user"}')
selector('|for-thing'      , '{                      "test":"is_for_thing"}')
selector('|for-thing-active','[1, {"test": "active"}, {"test":"is_for_thing"}]')

###############################################################################
# General Backoffice
###############################################################################

failure_update('$backoffice', value='Actions (not incidents)')
failure_update('$backoffice-login', value='Actions requiring a login')
failure_add('$backoffice', '$backoffice-login')
failure_update('$backoffice-nologin', value='Actions anonymous')
failure_add('$backoffice', '$backoffice-nologin')

selector('?backoffice'    ,'{"class":"SourceFailure",             "test":"in_or_equal", "value":"$backoffice"}')
selector('|backoffice'    ,'{"class":"FilterFailure",             "test":"in_or_equal", "value":"$backoffice"}')
selector('|not-backoffice','{"class":"Selector", "attr": "is_ok", "test":"false", "id":"|backoffice"}')

failure_update('$top', value='')
failure_add('$backoffice-login', '$top')

# The 'GUI' thing displays the backoffice user interface
thing_update('GUI', comment="Interface d'administration")
thing_add_failure('GUI', "$top")

# Display the reporting (not fix) feedback
action('report_feedback' ,'report_feedback.py')   # Send the report feedback to users
dispatcher_update('!report-feedback', action_id='report_feedback', selector_id='|not-backoffice')

# 'z' to be the last dispatched. It closes the API fake incident
action('close_auto', 'close_auto.py')
dispatcher_update('!z-backoffice-close', action_id='close_auto', selector_id='?backoffice')

# 'admin' is concerned by every incident
selector_concerned_add('|not-backoffice', '@admin')

# ----------------------------------------------
# Define a STATIC file getter
# ----------------------------------------------

action('get_file', 'get_file.py')

failure_update('$get_file', value='QRBug server get_file')
failure_update('flow.html', value='Présentation de QRBug', display_type=Button)
failure_add('$backoffice-nologin', '$get_file')
failure_add('$get_file', 'flow.html')
failure_add('$top', 'flow.html')

selector('?get_file','{"class":"SourceFailure", "test":"in_or_equal", "value": "$get_file"}')
dispatcher_update('!get_file', action_id='get_file', selector_id='?get_file')

###############################################################################
# Planified tasks
###############################################################################

failure_update('$hours', value='')
failure_update('$00:00', value='')
failure_update('$01:00', value='')
failure_update('$02:00', value='')
failure_update('$03:00', value='')
failure_update('$04:00', value='')
failure_update('$05:00', value='')
failure_update('$06:00', value='')
failure_update('$07:00', value='')
failure_update('$08:00', value='')
failure_update('$09:00', value='')
failure_update('$10:00', value='')
failure_update('$11:00', value='')
failure_update('$12:00', value='')
failure_update('$13:00', value='')
failure_update('$14:00', value='')
failure_update('$15:00', value='')
failure_update('$16:00', value='')
failure_update('$17:00', value='')
failure_update('$18:00', value='')
failure_update('$19:00', value='')
failure_update('$20:00', value='')
failure_update('$21:00', value='')
failure_update('$22:00', value='')
failure_update('$23:00', value='')

failure_add('$hours', '$00:00')
failure_add('$hours', '$01:00')
failure_add('$hours', '$02:00')
failure_add('$hours', '$03:00')
failure_add('$hours', '$04:00')
failure_add('$hours', '$05:00')
failure_add('$hours', '$06:00')
failure_add('$hours', '$07:00')
failure_add('$hours', '$08:00')
failure_add('$hours', '$09:00')
failure_add('$hours', '$10:00')
failure_add('$hours', '$11:00')
failure_add('$hours', '$12:00')
failure_add('$hours', '$13:00')
failure_add('$hours', '$14:00')
failure_add('$hours', '$15:00')
failure_add('$hours', '$16:00')
failure_add('$hours', '$17:00')
failure_add('$hours', '$18:00')
failure_add('$hours', '$19:00')
failure_add('$hours', '$20:00')
failure_add('$hours', '$21:00')
failure_add('$hours', '$22:00')
failure_add('$hours', '$23:00')
failure_add('$backoffice-login', '$hours') # To receive auto-close

#------------------------------------------------------------------------------
# Backoffice / lists
#------------------------------------------------------------------------------

failure_update('$list'           , value="Lister"            )
failure_update('$list-User'      , value="Les utilisateurs"  , display_type=Button)
failure_update('$list-Failure'   , value="Les pannes"        , display_type=Button)
failure_update('$list-Thing'     , value="Les objets"        , display_type=Button)
failure_update('$list-Selector'  , value="Les sélecteurs"    , display_type=Button)
failure_update('$list-Dispatcher', value="Les automatismes"  , display_type=Button)
failure_update('$list-Action'    , value="Les actions"       , display_type=Button)
failure_update('$list-Incident'  , value="Tous les incidents", display_type=Button)

failure_add('$list', '$list-User')
failure_add('$list', '$list-Failure')
failure_add('$list', '$list-Thing')
failure_add('$list', '$list-Selector')
failure_add('$list', '$list-Dispatcher')
failure_add('$list', '$list-Action')
failure_add('$list', '$list-Incident')
failure_add('$top', '$list')

# Use the same selector and dispatcher for all the failure in 'list'
# The 'list' action will check the failure ID to to the right thing.
action('list', 'list.py')
selector('?list', '''[1,
    {"class":"SourceFailure", "test":"in_or_equal", "value": "$list"},
    {"class":"SourceUser"   , "test":"in_or_equal", "value": "@admin-or-fixer"}
    ]''')
dispatcher_update('!admin-list', action_id='list', selector_id='?list')

#------------------------------------------------------------------------------
# Backoffice / journals
#------------------------------------------------------------------------------

failure_update('$journal'         , value="Afficher"                )
failure_update('$journal-config'  , value="Journal de configuration", display_type=Button)
failure_update('$journal-incident', value="Journal des incidents"   , display_type=Button)

failure_add('$journal', '$journal-config')
failure_add('$journal', '$journal-incident')
failure_add('$top', '$journal')

# Use the same selector and dispatcher for all the journal in 'journal'
# The 'journal' action will check the failure ID to to the right thing.
action('journal', 'show_journals.py')
selector('?journal', '''[1,
    {"class":"SourceFailure", "test":"in_or_equal", "value": "$journal"},
    {"class":"SourceUser"   , "test":"in_or_equal", "value": "@admin"}
    ]''')
dispatcher_update('!admin-journal', action_id='journal', selector_id='?journal')

#------------------------------------------------------------------------------
# Backoffice / misc
#------------------------------------------------------------------------------

failure_update('$misc'                 , value="Divers"                            )
failure_update('$pending-feedback'     , value="Feedbacks de réparation en attente", display_type=Button)
failure_update('$send-pending-feedback', value="Envoie le feedback de réparation"  , display_type=Button)
failure_update('$stats'                , value="Statistiques"                      , display_type=Button)
failure_update('$report-mail'          , value="Envoie mails de rappel à tous"     , display_type=Button)
failure_update('$check-selectors'      , value="Vérifie les sélecteurs"            , display_type=Button)

failure_add('$misc', '$pending-feedback')
failure_add('$misc', '$send-pending-feedback')
failure_add('$misc', '$stats')
failure_add('$misc', '$check-selectors')
failure_add('$misc', '$report-mail')
failure_add('$top' , '$misc')

action('pending_feedback', 'pending_feedback.py')  # Send user feedback for failure fix
action('stats'           , 'stats.py'           )
action('check-selectors' , 'check_selectors.py' )
action('report_mail'     , 'report_mail.py'     )  # Send mail to remind every active incident


selector('?hours', '''[1,
    {"class":"SourceFailure", "test":"in_or_equal", "value": "$hours"},
    {"class":"SourceUser"   , "test":"in_or_equal", "value": "@system"}
    ]''')

selector('?send-feedback', '''[1,
    {"class":"SourceFailure", "test":"is"         , "value": "$send-pending-feedback"},
    {"class":"SourceUser"   , "test":"in_or_equal", "value": "@root"}
    ]''')

selector('?send-pending-feedback','''[0,
    {"class":"Selector", "id": "?hours"        , "attr":"is_ok", "test": "true"},
    {"class":"Selector", "id": "?send-feedback", "attr":"is_ok", "test": "true"}
    ]''')
selector('|with-pending-feedback', '''[1,
    {"test": "pending_feedback"},
    {"class":"Selector", "id": "|backoffice", "attr": "is_ok", "test": "false"}
    ]''')

selector('?pending-feedback', '''[1,
    {"class":"SourceFailure", "test":"is", "value": "$pending-feedback"},
    {"class":"SourceUser"   , "test":"in_or_equal", "value": "@admin"}
    ]''')
selector('?stats', '''[1,
    {"class":"SourceFailure", "test":"is", "value": "$stats"},
    {"class":"SourceUser"   , "test":"in_or_equal", "value": "@admin"}
    ]''')
selector('?check-selectors', '''[1,
    {"class":"SourceFailure", "test":"is", "value": "$check-selectors"},
    {"class":"SourceUser"   , "test":"in_or_equal", "value": "@admin"}
    ]''')
selector('?report-mail', '''[1,
    {"class":"SourceFailure", "test":"is", "value": "$report-mail"},
    {"class":"SourceUser"   , "test":"in_or_equal", "value": "@admin"}
    ]''')


dispatcher_update('!pending-feedback'     , action_id='echo'            , selector_id='?pending-feedback'     , incidents="|with-pending-feedback")
dispatcher_update('!send-pending-feedback', action_id='pending_feedback', selector_id='?send-pending-feedback', incidents="|with-pending-feedback")
dispatcher_update('!stats'                , action_id='stats'           , selector_id='?stats')
dispatcher_update('!check-selectors'      , action_id='check-selectors' , selector_id='?check-selectors')


dispatcher_update('!report_mail', action_id='report_mail', selector_id='?report-mail', incidents='|active')

#------------------------------------------------------------------------------
# Backoffice / personnal
#------------------------------------------------------------------------------

failure_update('$personnal'           , value="Ce qui me concerne")
failure_update('$personnal-for-me'    , value="Les incidents que je dois traiter"  , display_type=Button)
failure_update('$personnal-for-me-all', value="Tous les incidents dont je m'occupe", display_type=Button)

failure_add('$personnal', '$personnal-for-me')
failure_add('$personnal', '$personnal-for-me-all')
failure_add('$top', '$personnal')

# Anybody can see its 'incidents'.

selector('?personnal-for-me'     ,'{"class":"SourceFailure", "test":"is", "value": "$personnal-for-me"}')
selector('?personnal-for-me-all' ,'{"class":"SourceFailure", "test":"is", "value": "$personnal-for-me-all"}')

dispatcher_update('!personnal-for-me'    , action_id='echo', selector_id='?personnal-for-me'    , incidents="|for-me")
dispatcher_update('!personnal-for-me-all', action_id='echo', selector_id='?personnal-for-me-all', incidents="|for-me-all")

###############################################################################
# Edit configuration
###############################################################################

failure_update('$edit', value="API de l'éditeur de configuration, elle ne permet aucune modification mais affiche seulement les éléments modifiables pour chacun des types d'objet.")
failure_add('$backoffice-login', '$edit')

# ---------------
# Edit dispatcher
# ---------------
failure_update('$dispatcher', value="Les dispatchers")
failure_update('$dispatcher-selector_id',
    value='Condition déclenchante<div style="font-weight:normal">Si le sélecteur est vrai.<br>Ordre lancement alphabétique.</div>',
    display_type=Datalist)
failure_update('$dispatcher-incidents',
    value='Sélecteur d\'incidents<div style="font-weight:normal">Si vide : seulement celui<br>qui a déclenché.</div>',
    display_type=Datalist)
failure_update('$dispatcher-action_id',
    value='Action à lancer<div style="font-weight:normal">Traite tous les<br>incidents sélectionnés.</div>',
    display_type=Datalist)
failure_update('$dispatcher-new', value="Créer l'automatisme : ", display_type=Input)
failure_add('$edit', '$dispatcher')
failure_add('$dispatcher', '$dispatcher-action_id')
failure_add('$dispatcher', '$dispatcher-selector_id')
failure_add('$dispatcher', '$dispatcher-incidents')
failure_add('$dispatcher', '$dispatcher-new')

action('edit_dispatcher', 'edit_dispatcher.py')
selector('?edit-dispatcher', '''[1,
    {"class":"SourceFailure", "test":"in_or_equal", "value": "$dispatcher"},
    {"class":"SourceUser"   , "test":"in_or_equal", "value": "@admin"}
    ]''')
dispatcher_update('!edit-dispatcher', action_id='edit_dispatcher', selector_id='?edit-dispatcher')

# ---------------
# Edit failure
# ---------------
failure_update('$failure'             , value="Les pannes")
failure_update('$failure-value'       , value="Intitulé"              , display_type=Input)
failure_update('$failure-display_type', value="Affichage"             , display_type=Display)
failure_update('$failure-ask_confirm' , value='Message de confirmation<div style="font-weight: normal">Laisser vide pour ne pas<br>demander la confirmation</div>', display_type=Input)
failure_update('$failure-add'         , value="Ajouter une sous-panne", display_type=Datalist)
failure_update('$failure-remove'      , value="Enlever d'ici"         , display_type=Button)
failure_add('$edit', '$failure')
failure_add('$failure', '$failure-value')
failure_add('$failure', '$failure-display_type')
failure_add('$failure', '$failure-ask_confirm')
failure_add('$failure', '$failure-add')
failure_add('$failure', '$failure-remove')

action('edit_failure', 'edit_failure.py')
selector('?edit-failure', '''[1,
    {"class":"SourceFailure", "test":"in_or_equal", "value": "$failure"},
    {"class":"SourceUser"   , "test":"in_or_equal", "value": "@admin"}
    ]''')
dispatcher_update('!edit-failure', action_id='edit_failure', selector_id='?edit-failure')

# ---------------
# Edit selector
# ---------------
failure_update('$selector', value="Sélecteur d'incident")
failure_update('$selector-expression', value="Expression", display_type=Input)
failure_update('$selector-concerned-add', value="Ajouter un<br>utilisateur concerné", display_type=Datalist)
failure_update('$selector-concerned-del', value="Utilisateurs concernés", display_type=Input)
failure_update('$selector-new', value="Créer le sélecteur", display_type=Input)
failure_add('$edit', '$selector')
failure_add('$selector', '$selector-expression')
failure_add('$selector', '$selector-concerned-add')
failure_add('$selector', '$selector-concerned-del')
failure_add('$selector', '$selector-new')

action('edit_selector', 'edit_selector.py')
selector('?edit-selector', '''[1,
    {"class":"SourceFailure", "test":"in_or_equal", "value": "$selector"},
    {"class":"SourceUser"   , "test":"in_or_equal", "value": "@admin"}
    ]''')
dispatcher_update('!edit-selector', action_id='edit_selector', selector_id='?edit-selector')

# ---------------
# Edit user
# ---------------
failure_update('$user', value="Utilisateur")
failure_update('$user-add'   , value="Ajouter un utilisateur<br>dans le groupe", display_type=Datalist)
failure_update('$user-remove', value="Enlever d'ici"                           , display_type=Button)
failure_update('$user-new'   , value="Créer l'utilisateur"                     , display_type=Input)
failure_add('$edit', '$user')
failure_add('$user', '$user-add')
failure_add('$user', '$user-remove')
failure_add('$user', '$user-new')

action('edit_user', 'edit_user.py')
selector('?edit-user', '''[1,
    {"class":"SourceFailure", "test":"in_or_equal", "value": "$user"},
    {"class":"SourceUser"   , "test":"in_or_equal", "value": "@admin-user"}
    ]''')
dispatcher_update('!edit-user', action_id='edit_user', selector_id='?edit-user')

# ---------------
# Edit thing
# ---------------
failure_update('$thing'            , value="Chose"          )
failure_update('$thing-comment'    , value="Commentaire"          , display_type=Input)
failure_update('$thing-del-failure', value="Pannes"               , display_type=Input)
failure_update('$thing-add-failure', value="Panne à ajouter"      , display_type=Datalist)
failure_update('$thing-add'        , value="Ajouter un objet fils", display_type=Datalist)
failure_update('$thing-remove'     , value="Enlever d'ici"        , display_type=Button)
failure_add('$edit', '$thing')
failure_add('$thing', '$thing-comment')
failure_add('$thing', '$thing-del-failure')
failure_add('$thing', '$thing-add-failure')
failure_add('$thing', '$thing-add')
failure_add('$thing', '$thing-remove')

action('edit_thing', 'edit_thing.py')
selector('?edit-thing', '''[1,
    {"class":"SourceFailure", "test":"in_or_equal", "value": "$thing"},
    {"class":"SourceUser"   , "test":"in_or_equal", "value": "@admin-thing"}
    ]''')
dispatcher_update('!edit-thing', action_id='edit_thing', selector_id='?edit-thing')


failure_update('$thing-incidents'       , value="Tous les incidents")
failure_update('$thing-incidents-active', value="Incidents actifs")
failure_add('$backoffice-login', '$thing-incidents')
failure_add('$backoffice-login', '$thing-incidents-active')

selector('?thing-incidents-active', '''[1,
    {"class":"SourceFailure", "test":"is", "value": "$thing-incidents-active"},
    {"class":"SourceUser"   , "test":"in_or_equal", "value": "@admin-thing"}
    ]''')
dispatcher_update('!incidents-active-for-thing', action_id='echo', selector_id='?thing-incidents-active', incidents='|for-thing-active')
selector('?thing-incidents', '''[1,
    {"class":"SourceFailure", "test":"is", "value": "$thing-incidents"},
    {"class":"SourceUser"   , "test":"in_or_equal", "value": "@admin-thing"}
    ]''')
dispatcher_update('!incidents-for-thing', action_id='echo', selector_id='?thing-incidents', incidents='|for-thing')

# ---------------
# Edit action
# ---------------
failure_update('$action', value="Action")
failure_update('$action-python_script', value="Le script Python à lancer", display_type=Datalist)
failure_add('$action', '$action-python_script')
failure_add('$edit', '$action')

action('edit_action', 'edit_action.py')
selector('?edit-action', '''[1,
    {"class":"SourceFailure", "test":"in_or_equal", "value": "$action"},
    {"class":"SourceUser"   , "test":"in_or_equal", "value": "@admin"}
    ]''')
dispatcher_update('!edit-action', action_id='edit_action', selector_id='?edit-action')

###############################################################################

# ---------------
# QRCode
# ---------------

failure_update('$generate_qr', value='Générer un QR code de la taille indiquée')
failure_add('$backoffice-login', '$generate_qr')
for rows in (7, 8):
    for cols in (4, 5, 6):
        failure_update(f'$generate_qr_{rows}×{cols}', value=f'En {rows}×{cols}', display_type=Input)
        failure_add('$generate_qr', f'$generate_qr_{rows}×{cols}')

action('generate_qrcode', 'generate_qr.py')
selector('?generate_qr', '''[1,
    {"class":"SourceFailure", "test":"in_or_equal", "value": "$generate_qr"},
    {"class":"SourceUser"   , "test":"in_or_equal", "value": "@admin-or-fixer"}
    ]''')
dispatcher_update('!generate-qr', action_id='generate_qrcode', selector_id='?generate_qr')

# ----------------------------------------------
# Define QRBug backtrace failure and dispatcher
# ----------------------------------------------

failure_update('$backtrace', value='QRBug server backtrace')
selector('?backtrace', '''[1,
    {"class":"SourceFailure", "test":"is"         , "value": "$backtrace"},
    {"class":"SourceUser"   , "test":"in_or_equal", "value": "@system"}
    ]''')
selector_concerned_add('?backtrace', '@admin-backtrace')
dispatcher_update('!backtrace', action_id='report_mail', selector_id='?backtrace')

# ----------------------------------------------
# Journals reload
# ----------------------------------------------
failure_update('$reload_journals', value='Recharger les journaux de configuration', display_type=Button)
failure_add('$misc', '$reload_journals')
selector('?reload_journals', '''[1,
    {"class":"SourceFailure", "test":"is", "value": "$reload_journals"},
    {"class":"SourceUser"   , "test":"in_or_equal", "value": "@root"}
    ]''')
action('reload_journals', 'reload_journals.py')
dispatcher_update('!reload_journals', action_id='reload_journals', selector_id='?reload_journals')

# ----------------------------------------------
# Require logins
# ----------------------------------------------

selector('?require-login', '''[0,
    {"class":"SourceFailure", "test":"in_or_equal", "value": "$backoffice-login"}
]''')

# ----------------------------------------------
# Messages
# ----------------------------------------------

failure_update('$messages', value='Modifiez les messages affichés')
failure_add('$backoffice-login', '$messages')

for message in pathlib.Path(MESSAGES).read_text(encoding='utf-8').strip().split('\n'):
    failure_id, value = message.split(' ', 1)
    failure_update(failure_id, value=value)
    failure_add('$messages', failure_id)

# ----------------------------------------------
# User interface for fixers
# ----------------------------------------------

failure_update('$fixer', value="Interface du réparateur de panne")
failure_add('$backoffice-login', '$fixer')
failure_add('$fixer', '$list-Thing')
failure_add('$fixer', '$personnal')

thing_update('GUI-fixer', comment="Interface du réparateur de panne")
thing_add_failure('GUI-fixer', '$fixer')

# ----------------------------------------------
# Old incidents
# ----------------------------------------------

failure_update('$older-than-a-week', value="Incidents non réparés depuis 7 jours", display_type=Button)
selector('|older-than-a-week', '{"test": "older_than", "value": "7"}')
selector('?older-than-a-week', '''[1,
    {"class":"SourceFailure", "test":"is", "value": "$older-than-a-week"},
    {"class":"SourceUser"   , "test":"in_or_equal", "value": "@admin-or-fixer"}
    ]''')
failure_add('$misc', '$older-than-a-week')
dispatcher_update('!older-than-a-week', action_id='echo', selector_id='?older-than-a-week', incidents='|older-than-a-week')

