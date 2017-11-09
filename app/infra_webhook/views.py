import json
from flask import request, jsonify
from app import docker_ext
from . import infra_webhook


@infra_webhook.route('/docker_webhook', methods=['GET'])
def docker_commit():
    payload = json.loads(request.data)
    print(payload)
    return jsonify(payload), 200


@infra_webhook.route('/git_webhook', methods=['POST'])
def git_commit():
    payload = json.loads(request.data)
    print(payload)
    return jsonify(payload), 200
