class SystemTestException(Exception):
    def __init__(self, custom_message, root_cause):
        self.custom_message = custom_message
        self.root_cause = root_cause

    def __str__(self):
        return "%s, root cause: %s" % (self.custom_message, self.root_cause)

