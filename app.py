from collections import ChainMap
import json
import os
from flask import abort, render_template, request, send_from_directory
from flask import Flask
import base64
import uuid
# import logging
from flask_limiter import HEADERS, Limiter  
from flask_limiter.util import get_remote_address
import yaml
from security import check_payload, is_base64
def load_yaml(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def merge_yml(config1, config2):
    if config2 == None:
        config2 = {}
    merged = ChainMap(config1, config2)
    return dict(merged)

first_config = load_yaml('./base/config.yaml')

second_config = load_yaml('./config.yaml')


config = merge_yml(first_config, second_config)

app = Flask("app")
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=config["limiter_default_limits"],
    header_name_mapping={
        HEADERS.LIMIT : "X-My-Limit",
        HEADERS.RESET : "X-My-Reset",
        HEADERS.REMAINING: "X-My-Remaining"
  }
)
UPLOADS_DIR = config["UPLOADS_DIR"]
accepted_ext = config["accepted_ext"]
ip_ban_list = config["ip_ban_list"]

if not os.path.exists(UPLOADS_DIR):
    os.makedirs(UPLOADS_DIR)


@app.before_request
def block_method():
    ip = request.environ.get('REMOTE_ADDR')
    if ip in ip_ban_list:
        abort(403)

@app.route('/upload', methods=['GET', 'POST'])
def handle_upload():
    if request.method == "POST":
        if check_payload(request.data):
            file = json.loads(request.data.decode("utf-8"))
        else:
            return "Invalid payload schema!\n", 400
        
        if "name" not in file.keys():
            file["name"] = str(uuid.uuid4())+".png"

        if is_base64(file["content"]):
            content = base64.b64decode(file["content"])
        else:
            return "Invalid content\n", 400
        
        with open(UPLOADS_DIR+file["name"], "wb") as fh:
            fh.write(content)
            return f"File {file['name']}, created!\n", 201
        

    return render_template("upload.html")

@app.route("/proceed/<ID>")
def proceed(ID):
    file_path = os.path.join(UPLOADS_DIR, f"{ID}.png")
    if os.path.exists(file_path):
        return send_from_directory(UPLOADS_DIR, f"{ID}.png", as_attachment=False)
    else:
        return "File not found!\n", 404


if __name__ == "__main__":
    app.run()



