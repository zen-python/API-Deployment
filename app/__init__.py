import json
from flask import Flask, jsonify, make_response
from app.extensions import celery, aws_ext, dbm_ext, docker_ext, infra_ext, logcfg
from app.config import config
from remote_pdb import RemotePdb


def create_app(config_name):
    """Application Factory"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    with app.app_context():
        register_extensions(app)
        register_blueprints(app)
        register_errorhandlers(app)
        data = {}

        @app.route('/', methods=['GET'])
        def index():
            return jsonify({'error': 'method not allowed'}), 405

        def after_request(after_req):
            data.update(logcfg.get_request_message_data(after_req))
            http_request = data['werkzeug.request'].data

            if http_request:
                parsed = json.loads(http_request)
                print(json.dumps(parsed, indent=4, sort_keys=True))
            return after_req
        app.after_request(after_request)
        logcfg.start_listeners(app)
        return app


def register_extensions(app):
    # Register extensions
    aws_ext.init_app(app)
    dbm_ext.init_app(app)
    infra_ext.init_app(app)
    docker_ext.init_app(app)
    logcfg.init_app(app)
    celery.config_from_object(app.config)


def register_blueprints(app):
    # Register blueprints
    from .webhook import webhook
    from .infra_webhook import infra_webhook
    app.register_blueprint(webhook)
    app.register_blueprint(infra_webhook)


def register_errorhandlers(app):
    # Register error handlers
    def render_error(e):
        return make_response(jsonify({'error': e.name}), e.code)

    for e in [401, 405, 404, 500]:
        app.errorhandler(e)(render_error)
