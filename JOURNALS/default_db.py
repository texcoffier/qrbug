from qrbug.user import User

action('none', 'none.py')
selector('true', 'True')
User.get('nobody')
failure_update('debug', value="Toutes les failures", ask_confirm=False)
thing_update('debug', failure_id="debug", comment="Every available failure")