#!/usr/bin/env python3

import os
import uuid
import boto3
import urllib3

from flask import Flask, render_template, request, redirect, send_file, url_for, logging
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.logger = logging.create_logger(app)
app.config["PREFERRED_URL_SCHEME"] = "https"
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", str(uuid.uuid4()))
app.config["EXCLUDE_PREFIX"] = os.environ.get("EXCLUDE_PREFIX", "prefix")
app.config["UPLOAD_FOLDER"] = os.environ.get("UPLOAD_FOLDER", "/tmp")
app.config["AWS_DEFAULT_REGION"] = os.environ.get("AWS_DEFAULT_REGION", None)
app.config["AWS_ACCESS_KEY_ID"] = os.environ.get("AWS_ACCESS_KEY_ID", None)
app.config["AWS_SECRET_ACCESS_KEY"] = os.environ.get("AWS_SECRET_ACCESS_KEY", None)
app.config["BUCKET_NAME"] = os.environ.get("BUCKET_NAME", None)
app.config["BUCKET_HOST"] = os.environ.get("BUCKET_HOST", None)
app.config["BUCKET_PORT"] = os.environ.get("BUCKET_PORT", None)
app.config["BUCKET_SCHEMA"] = "http" if app.config["BUCKET_PORT"] == "80" else "https"
app.config["ENDPOINT_URL"] = "{}://{}".format(
    app.config["BUCKET_SCHEMA"], app.config["BUCKET_HOST"]
)

urllib3.disable_warnings()
app.logger.info("Initializing…")

if not os.path.isdir(app.config["UPLOAD_FOLDER"]):
    app.logger.info("UPLOAD_FOLDER does not exist.")
    os.makedirs(app.config["UPLOAD_FOLDER"])

s3 = boto3.client(
    "s3",
    endpoint_url=app.config["ENDPOINT_URL"],
    use_ssl=False,
    verify=False
)
app.static_folder = "static"

app.logger.info("Serving files from s3://{}".format(app.config["BUCKET_NAME"]))
app.logger.info("Ignoring files from {}".format(app.config["EXCLUDE_PREFIX"]))


@app.route("/")
def index():
    contents = list_files(s3, app.config["BUCKET_NAME"])
    return render_template("index.html", contents=contents)


@app.route("/favicon.ico", methods=["GET"])
def favicon():
    """
    Return an empty favicon
    """
    return ""

@app.route("/upload", methods=["POST"])
def upload():
    if request.method == "POST":
        app.logger.info("Trying to upload file")
        f = request.files["file"]
        sfname = os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(f.filename))
        f.save(sfname)
        upload_file(s3, sfname, app.config["BUCKET_NAME"])
        # Return an external redirect on the HTTPS scheme
        return redirect(url_for("index", _external=True, _scheme="https"))

@app.route("/download/<filename>", methods=["GET"])
def download(filename):
    if request.method == "GET":
        sfname = os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(filename))
        output = s3.download_file(app.config["BUCKET_NAME"], sfname, sfname)
        return send_file(sfname)

def upload_file(s3,file_name, bucket):
    """
    Function to upload a file to an S3 bucket
    """
    object_name = file_name
    response = s3.upload_file(file_name, bucket, object_name)
    return response


def download_file(s3, file_name, bucket):
    """
    Function to download a given file from an S3 bucket
    """
    output = "downloads/{file_name}"
    s3.Bucket(bucket).download_file(file_name, output)
    return output


def list_files(s3, bucket):
    """
    Function to list files in a given S3 bucket
    """
    contents = []
    signed_url = {}
    try:
        for item in s3.list_objects(Bucket=bucket)["Contents"]:
            object_key = item["Key"]
            # Don't display items in EXCLUDE_PREFIX
            if not str(item["Key"]).startswith("{}".format(app.config["EXCLUDE_PREFIX"])):
                response = s3.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": bucket, "Key": object_key},
                    ExpiresIn=3600
                )
                signed_url = {
                    "url": response,
                    "name": object_key,
                    "path": os.path.basename(object_key),
                }
                # signed_url.update(signed_url)
                # app.logger.debug(response)
                contents.append(signed_url)

    except Exception as e:
        pass
    return contents

if __name__ == "__main__":
    app.logger.debug("__main__")
    app.run()
