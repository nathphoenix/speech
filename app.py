from flask import Flask, render_template
from flask_restful import Api, Resource
from speech import Audio_Transform
from upload_test import Audio_Analysis
from record_speech import Audio_Record, Page
import glob, os


app = Flask(__name__)
@app.route('/')
def homePage():
	return render_template("index.html")
 
@app.route('/test')
def speech():
	return render_template("speech.html")


app.config["PROPAGATE_EXCEPTIONS"] = True
UPLOAD_FOLDER = '/Tested/'
UPLOAD_FOLDER = os.getcwd() + UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['wav', 'mp3', 'aac', 'flac'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
api = Api(app)


app.secret_key = "nathaniel"
# api.add_resource(homePage, "/")
api.add_resource(Audio_Transform, "/audio")
api.add_resource(Audio_Analysis, "/analyse")
api.add_resource(Audio_Record, "/upload")
api.add_resource(Page, "/404")



if __name__ == "__main__":
    app.run(port=5000, debug=True)
