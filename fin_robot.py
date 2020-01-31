import yaml
import logging.config
import os
import logging

def set_log_cfg(default_path="log_cfg.yaml", default_level=logging.INFO, env_key="LOG_CFG"):
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, "r") as f:
            config = yaml.load(f)
            logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

if __name__ == '__main__':
    import reload
    set_log_cfg(default_path='conf/logging.yaml')
    reload.fetch()