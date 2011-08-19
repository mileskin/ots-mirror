from configobj import ConfigObj

common_cfg = ConfigObj("log_tests.conf")
# This file optional and not in version control. Put your local changes there!
local_cfg = ConfigObj("log_tests.local.conf")
common_cfg.merge(local_cfg)
CONFIG = common_cfg.get("log_tests")

def global_log_url():
    return "http://" + CONFIG["server"] + "/logger/view"

