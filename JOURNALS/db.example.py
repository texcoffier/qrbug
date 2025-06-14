user_add("ROOT", "P123456789")
selector('ROOT', '{"class": "SourceUser", "test": "in_or_equal", "value": "ROOT"}')

failure_update("PC_NO_BOOT", value="Le PC ne démarre pas", display_type=Text, allowed="ROOT")
failure_update("PC_NO_BOOT_BIOS_ERROR",   value="... et affiche un texte blanc sur écran noir", display_type=Button, ask_confirm=True, allowed="ROOT")
failure_update("PC_NO_BOOT_BLACK_SCREEN", value="... et l'écran ne s'allume pas non plus", display_type=Text, ask_confirm=True, allowed="ROOT")
failure_update("PC_NO_BOOT_NO_POWER",     value="... et la diode sur le PC ne clignote pas", display_type=Button, ask_confirm=True, allowed="ROOT")
failure_update("PC_NO_BOOT_OTHER", value="Autre chose ?", display_type=Textarea, ask_confirm=True, allowed="ROOT")
failure_update("PC_NO_BOOT_BLACK_SCREEN_UNPLUGGED_WIRE", value="... et un câble est débranché", display_type=Button, ask_confirm=True, allowed="ROOT")
failure_update("PC_NO_BOOT_BLACK_SCREEN_PLUGGED_WIRE", value="... et je ne peux pas voir les câbles", display_type=Button, ask_confirm=True)
failure_update("UNIV_WEBSITE", value="https://www.univ-lyon1.fr/", display_type=Redirect, allowed="ROOT")
failure_add("PC_NO_BOOT", "PC_NO_BOOT_BIOS_ERROR")
failure_add("PC_NO_BOOT", "PC_NO_BOOT_BLACK_SCREEN")
failure_add("PC_NO_BOOT_BLACK_SCREEN", "PC_NO_BOOT_BLACK_SCREEN_PLUGGED_WIRE")
failure_add("PC_NO_BOOT_BLACK_SCREEN", "PC_NO_BOOT_BLACK_SCREEN_UNPLUGGED_WIRE")
failure_add("PC_NO_BOOT", "PC_NO_BOOT_NO_POWER")
failure_add("PC_NO_BOOT", "PC_NO_BOOT_OTHER")
failure_add("PC_NO_BOOT", "UNIV_WEBSITE")

thing_update("b710pc0101")
thing_add_failure("b710pc0101", ="PC_NO_BOOT")
thing_update("b710pc0101", comment="3ème à gauche")

selector('BASE', 'True')
action('TEST', 'test.py')
action('GENERATE_QR', 'generate_qr.py')
dispatcher_update('TEST', action_id='TEST', selector_id='BASE')

selector('PC_NO_BOOT_BIOS_ERROR', 'failure.id == "PC_NO_BOOT_BIOS_ERROR"')
action('HELLOW', 'hellow.py')
dispatcher_update('PC_NO_BOOT_BIOS_ERROR', action_id='HELLOW', selector_id='PC_NO_BOOT_BIOS_ERROR')


# ---- DEBUG ----
action('SHOW_JOURNALS', 'show_journals.py')
dispatcher_update('DEBUG_SHOW_JOURNALS', action_id='SHOW_JOURNALS')

failure_update('SHOW_JOURNALS', value="Afficher les journeaux", display_type=Text, ask_confirm=True, allowed="ROOT")
failure_update('SHOW_JOURNALS_DB-DEFAULT_DB-INCIDENTS', value="Afficher TOUS les journeaux", display_type=Button, ask_confirm=True, allowed="ROOT")
failure_update('SHOW_JOURNALS_DB', value="Afficher la configuration", display_type=Button, ask_confirm=True, allowed="ROOT")
failure_update('SHOW_JOURNALS_DEFAULT_DB', value="Afficher la configuration par défaut", display_type=Button, ask_confirm=True, allowed="ROOT")
failure_update('SHOW_JOURNALS_INCIDENTS', value="Afficher la liste des incidents", display_type=Button, ask_confirm=True, allowed="ROOT")
failure_add('SHOW_JOURNALS', 'SHOW_JOURNALS_DB-DEFAULT_DB-INCIDENTS')
failure_add('SHOW_JOURNALS', 'SHOW_JOURNALS_DB')
failure_add('SHOW_JOURNALS', 'SHOW_JOURNALS_DEFAULT_DB')
failure_add('SHOW_JOURNALS', 'SHOW_JOURNALS_INCIDENTS')

thing_update('DEBUG', comment='Affiche les journeaux de configuration de qrbug')
thing_add_failure('DEBUG', 'SHOW_JOURNALS')
