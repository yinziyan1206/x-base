__author__ = 'ziyan.yin'
__describe__ = 'config template'

import os

from dynaconf import Dynaconf

settings = Dynaconf(
    settings_file=["application.yaml", ".secrets.yaml"],  # location of config file
    environments=["default", "development", "test", "staging", "qa", "production"],  # available modes/environments
    envvar_prefix="TEFLO",  # prefix for exporting env vars
    env_switcher="TEFLO_MODE",  # Variable that controls mode switch
    env=os.environ.get("DEFAULT_DEPLOY_STAGE", default="default")  # Initial env/mode
)
