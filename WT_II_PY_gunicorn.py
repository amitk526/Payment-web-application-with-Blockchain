from configuration import DevelopmentConfig
from flask_script import Manager
from WT_II_PY_MAIN import application
from configuration import DevelopmentConfig
import gunicorn.app.base

class StandaloneApplication(gunicorn.app.base.BaseApplication):
    options = {
        'bind': '%s:%s' % ('127.0.0.1', '9999'),
        'workers': 4,
    }

    def __init__(self, app):
        self.application = app
        super().__init__()


    def load_config(self):
        config = {key: value for key, value in self.options.items()
                  if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application

application.config.from_object(DevelopmentConfig)
manager = Manager(application)
manager.add_command('dpsserver',StandaloneApplication(application).run())

if __name__ == '__main__':
    manager.run()
