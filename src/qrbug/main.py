from qrbug.user import user_add, user_remove
from qrbug.failure import failure_update, failure_add, failure_remove, DisplayTypes
from qrbug.thing import thing_update, thing_del
from qrbug.action import action
from qrbug.selector import selector
from qrbug.dispatcher import dispatcher_update, dispatcher_del


DB_FILE_PATH = "JOURNALS/db.py"


def load_config() -> None:
    with open(DB_FILE_PATH, 'r', encoding='utf-8') as f:
        db_file_contents = f.read()
    db_file_code = compile(db_file_contents, DB_FILE_PATH, 'exec')
    exec(db_file_code, {
        "user_add": user_add,
        "user_remove": user_remove,
        "failure_update": failure_update,
        "failure_add": failure_add,
        "failure_remove": failure_remove,
        "DisplayTypes": DisplayTypes,
        "thing_update": thing_update,
        "thing_del": thing_del,
        "action": action,
        "selector": selector,
        "dispatcher_update": dispatcher_update,
        "dispatcher_del": dispatcher_del,
    })


if __name__ == "__main__":
    load_config()
