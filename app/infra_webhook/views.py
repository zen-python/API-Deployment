import json
from flask import request, jsonify
from app import infra_ext
from . import infra_webhook


@infra_webhook.route('/git_webhook', methods=['POST'])
def git_commit():
    payload = json.loads(request.data)
    infra_ext.run_rsync(payload)
    return jsonify(payload), 200


@infra_webhook.route('/docker_webhook', methods=['POST'])
def docker_commit():
    payload = json.loads(request.data)
    infra_ext.update_docker(payload)
    return jsonify(payload), 200
