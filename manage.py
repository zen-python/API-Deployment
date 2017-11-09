import os
from flask_script import Manager, Shell, Server
from app import create_app
#

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)


def make_shell_context():
    return dict(app=app)


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('runserver', Server(host='0.0.0.0', port=9000))
manager.add_default_commands

if __name__ == '__main__':
    manager.run()
