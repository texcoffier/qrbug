import qrbug

class ActionReturnValue:
    """
    What is returned by an action.
    """
    def __init__(self, error_msg: str = '', info_msg: str = ''):
        self.error_msg = error_msg
        self.info_msg = info_msg

    def is_empty(self):
        return self.error_msg == '' and self.info_msg == ''

    def __bool__(self):
        return not self.is_empty()

def get_template():
    """The file containing JS helpers and style."""
    return qrbug.REPORT_FAILURE_TEMPLATE.read_text()
qrbug.get_template = get_template