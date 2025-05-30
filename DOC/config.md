# QRbug Configuration

QRbug uses multiple journal files as config.  
You can find them in the `JOURNALS/` directory.

## Journals
Please note that every journal file contains valid Python code.  
The following code is thus valid in a journal :
```py
for i in range(5):
    print('*' * i)
```
And will print the following characters to the console every time the given journal is reloaded :
```

*
**
***
****
```

### Default DB
The `default_db.py` is always run first, and defines base users, selectors, and failures.  
It is not meant to be edited by the end user, but rather by the developer of QRbug.

### DB
The `db.py` file contains the end user's QRbug configuration.  
It defines user groups, failures, things, selectors, dispatchers, actions... And parents them so they form a hierarchy.

#### User groups
You can parent a user group to another through the `user_add(parent_id, child_id)` method.  
Doing so will make sure that the child group benefits from the parent group's privileges, with slight modification if wanted.

#### Failures
A failure defines a type of failure that can happen to a piece of equipment.  
It is what will be presented to the user when scanning some equipment's QR code.

You can create/update a failure with the following code :
```py
failure_update(failure_id, value, display_type, ask_confirm, restricted_to_group_id)
```
Each of these parameters *(besides `failure_id`)* is optional if you want to modify a failure.

- **Value** (string) : The written value that will be displayed when presenting the failure.
- **Display type** (DisplayType) : One of 4 available display types when presenting the failure to the user
  - `DisplayType.text` : Just some text. _This failure type cannot be manually triggered by a user._
  - `DisplayType.button` : A button the user can click to report an incident.
  - `DisplayType.redirect` : A link to something the user might want to know about. _This failure type cannot be manually triggered by a user._
  - `DisplayType.input` : An input box the user can write into to report an incident.
- **Ask confirm** (bool) : Whether to present the user with a confirmation box before submitting the incident report for this failure.
- **Restricted to group ID** (string) : Only the given group of users or their children can report this failure.

You can parent a failure with `failure_add(parent_id, child_id)`.
Parenting failures allows to create a hierarchy of failures that can be attached to a single object, so the users can report exactly what went wrong.

Here is such an example :
```py
failure_update("PC_NO_BOOT", value="Le PC ne démarre pas", display_type=DisplayTypes.text, ask_confirm=False, restricted_to_group_id="ROOT")
failure_update("PC_NO_BOOT_BIOS_ERROR",   value="... et affiche un texte blanc sur écran noir", display_type=DisplayTypes.button, ask_confirm=True, restricted_to_group_id="ROOT")
failure_update("PC_NO_BOOT_BLACK_SCREEN", value="... et l'écran ne s'allume pas non plus",      display_type=DisplayTypes.text, ask_confirm=True, restricted_to_group_id="ROOT")
failure_update("PC_NO_BOOT_NO_POWER",     value="... et la diode sur le PC ne clignote pas",    display_type=DisplayTypes.button, ask_confirm=True, restricted_to_group_id="ROOT")
failure_update("PC_NO_BOOT_OTHER", value="Autre chose ?", display_type=DisplayTypes.input, ask_confirm=True, restricted_to_group_id="ROOT")
failure_update("PC_NO_BOOT_BLACK_SCREEN_UNPLUGGED_WIRE", value="... et un câble est débranché", display_type=DisplayTypes.button, ask_confirm=True, restricted_to_group_id="ROOT")
failure_update("PC_NO_BOOT_BLACK_SCREEN_PLUGGED_WIRE", value="... et je ne peux pas voir les câbles", display_type=DisplayTypes.button, ask_confirm=True, restricted_to_group_id=None)
failure_update("UNIV_WEBSITE", value="https://www.univ-lyon1.fr/", display_type=DisplayTypes.redirect, ask_confirm=False, restricted_to_group_id="ROOT")
failure_add("PC_NO_BOOT", "PC_NO_BOOT_BIOS_ERROR")
failure_add("PC_NO_BOOT", "PC_NO_BOOT_BLACK_SCREEN")
failure_add("PC_NO_BOOT_BLACK_SCREEN", "PC_NO_BOOT_BLACK_SCREEN_PLUGGED_WIRE")
failure_add("PC_NO_BOOT_BLACK_SCREEN", "PC_NO_BOOT_BLACK_SCREEN_UNPLUGGED_WIRE")
failure_add("PC_NO_BOOT", "PC_NO_BOOT_NO_POWER")
failure_add("PC_NO_BOOT", "PC_NO_BOOT_OTHER")
failure_add("PC_NO_BOOT", "UNIV_WEBSITE")
```

And the result :  
![Failures List Screen](./img/failures_list_screen.png)

