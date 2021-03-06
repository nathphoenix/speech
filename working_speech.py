import os, glob, shutil
from flask import Flask, request, redirect, url_for, jsonify, render_template
# from werkzeug import secure_filename
from werkzeug.utils import secure_filename
import glob, os
import librosa
import pprint
import json
from matplotlib import pyplot as plt
from librosa import display
import seaborn as sns
import numpy as np
import pandas as pd
import time
from datetime import datetime
from google.cloud import speech_v1 as speech
from tqdm import tqdm
from flask_restful import Api, Resource
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "nath.json"

UPLOAD_FOLDER = '/Tested/'
UPLOAD_FOLDER = os.getcwd() + UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['wav', 'mp3', 'aac', 'flac'])

# folder = UPLOAD_FOLDER
# for file_name in os.listdir(folder):
#     file_path = os.path.join(folder, file_name)
#     try:
#         if os.path.isfile(file_path) or os.path.islink(file_path):
#             os.unlink(file_path)
#         elif os.path.isdir(file_path):
#             shutil.rmtree(file_path)
#     except Exception as e:
#         print('Failed to delete %s. Reason: %s' % (file_path, e))

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route("/upload", methods=['GET', 'POST'])
def index():
    client = speech.SpeechClient()
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            files = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], files))
            client = speech.SpeechClient()
        # https://storage.cloud.google.com/audiofilex/sample.wav
        conversation = list()
        taco = "/Tested"
        parent_dir = os.getcwd() + taco
        files = [pdf_file for pdf_file in glob.glob(os.path.join(parent_dir, '*'))]
        for file in tqdm(sorted(files)):
            with open(file, 'rb') as audio_file:
                content = audio_file.read()
            audio = speech.types.RecognitionAudio(content=content)
            enable_word_time_offsets = True
            language_code="en-US"
            config = speech.types.RecognitionConfig(
                enable_word_time_offsets = enable_word_time_offsets,
                language_code = language_code)
            response = client.recognize(config, audio)    # for transcribing short audio
            # response = client.long_running_recognize(config, audio)   #  for transcribing long audio
            result = response.results[0]
            # First alternative is the most probable result
            alternative = result.alternatives[0]
        #     print(u"Transcript: {}".format(alternative.transcript))
            # Print the start and end time of each word
            for word in alternative.words:
                conversation.append(word)
        # CONVERTING THE LIST INTO DICTIONARY
        dict_list = conversation
        dictionary = {}
        for i, d in enumerate(dict_list):
            dictionary[i] = d
        dicionary = dictionary
        print(dictionary)
        # extracting the output into different list
        words = []
        starts =[]
        ends = []
        for items in conversation:
            end = items.end_time
            start = items.start_time
            word = items.word
            starts.append(start)
            ends.append(end)
            words.append(word)
        # print(words)
        # print(starts)
        # print(ends)
        # Converting the list into a dataframe
        matrix = np.matrix([words,starts,ends])
        df = pd.DataFrame(data=matrix)
        new = df.T
        # new = len(new)
        # return new
        # Renaming the column and saving to new csv
        new.rename(columns = {new.columns[0]: "Words", df.columns[1]: "Start_time", new.columns[2]: "End_time" }, inplace = True )
        new.to_csv("Bosses.csv", index=False)
        # Removing all tailing newlines from the csv
        final = pd.read_csv("Bosses.csv")
        keep_col = ["Words","Start_time","End_time"]
        new_f = final[keep_col].replace('\\n',' ', regex=True)
        data = new_f
        # EXPLORATORY DATA ANALYSIS (DATA TRANSFORMATION)
        new = data["Start_time"].str.split("nanos: ", n = 1, expand = True)
        # making seperate first name column from new data frame
        data["Seconds"]= new[0]
        # making seperate last name column from new data frame
        data["Nanos"]= new[1]
        # Dropping old Name columns
        data.drop(columns =["Start_time"])

        first_data = data
        new = first_data["End_time"].str.split("nanos: ", n = 1, expand = True)
        # making seperate first name column from new data frame
        first_data["End_Seconds"]= new[0]
        # making seperate last name column from new data frame
        first_data["End_Nanos"]= new[1]
        # Dropping old Name columns
        first_data.drop(columns =["End_time"])
        # df display
        later_data = first_data
        # later_data.head()
        new = later_data["End_Seconds"].str.split("seconds: ", n = 1, expand = True)
        # making seperate first name column from new data frame
        later_data["End_del_Nanos"]= new[0]
        # making seperate last name column from new data frame
        later_data["End_Secs"]= new[1]
        # Dropping old Name columns
        later_data.drop(columns =["End_Seconds"])
        # df display
        next_data = later_data
        # next_data.head()
        updated_data = later_data.drop(columns = ["End_del_Nanos", "End_Seconds"])
        # updated_data.head()
        new = updated_data["Seconds"].str.split("seconds: ", n = 1, expand = True)
        # making seperate first name column from new data frame
        updated_data["Start_del_Nanos"]= new[0]
        # making seperate last name column from new data frame
        updated_data["Start_Secs"]= new[1]
        # Dropping old Name columns
        updated_data.drop(columns =["Seconds"], inplace =True)
        # df display
        up_data = updated_data
        # up_data.head()
        arrange = up_data[["Words", "Nanos", "Start_Secs", "End_Nanos", "End_Secs", "Start_del_Nanos"]]
        final_data = arrange.drop(columns = ["Start_del_Nanos"])
        remove_na = final_data.fillna(0)

        df = remove_na
        df["Nanos_secs"] = round(df["Nanos"].astype(int) / 1000000000, 2)
        df["End_Nanos_secs"] = round(df["End_Nanos"].astype(int) / 1000000000, 2)
        df = df[["Words", "Start_Secs", "Nanos_secs", "End_Secs", "End_Nanos_secs"]]
        df['Start_time(in sec)'] = round(df['Start_Secs'].astype(int) + df['Nanos_secs'], 2)
        df['End_time(in secs)'] = round(df['End_Secs'].astype(int) + df['End_Nanos_secs'], 2)
        df['Total_Time_words'] = round(df['Start_time(in sec)'].astype(int) + df['End_time(in secs)'], 2)
        Word_time_stamp = df[["Words", "Start_time(in sec)", "End_time(in secs)", "Total_Time_words"]]
        # Word_time_stamp = str(len(Word_time_stamp))
        # SECOND ANALYSIS OF AUDIO FILE BY LIBROSA
        # audio = sorted(os.listdir('Test'))[0]
        # taco = "/Tested"
        # parent_dir = os.getcwd() + taco
        # # parent_dir = '/Test'
        # for file in glob.glob(os.path.join(parent_dir, '*')):
        #     print (audio)
        for audios in files:
          print(audios)
        samples, sampling_rate = librosa.load(audios)
        #furrier transform of data
        data_fft = np.fft.rfft(samples)
        #frequencies
        frequencies = np.abs(data_fft)

        df = pd.DataFrame(samples, columns=['Amplitudes'])
        # df = d["Amplitudes"]
        df.index = [(1/sampling_rate)*i for i in range(len(df.index))]
        amp = df.rename_axis('Time').reset_index()
        # amp.sort_values('Amplitudes', ascending=False)
        amp["Time"] = amp["Time"].round(2)
        amp = amp[["Time", "Amplitudes"]]

        amp = amp.sort_values('Amplitudes', ascending=False)
        # amp.head(3)
        new = amp[amp["Amplitudes"] > 0.0]
        new.sort_values('Amplitudes', ascending=False)
        # EXTRACTION OF AMPLITUDE FOR EACH WORDS
        amp = new
        data = Word_time_stamp
        # d = {e:amp.loc[amp['Time'].between(s, e), 'Amplitudes'].sort_values(ascending=False)[:5].mean()
        #      for s, e in data[['Start_time(in sec)','End_time(in secs)']].to_numpy()}
        d = {e:amp.loc[amp['Time'].between(s, e), 'Amplitudes'][:1].mean()
             for s, e in data[['Start_time(in sec)','End_time(in secs)']].to_numpy()}
        data['Amplitudes'] = data['End_time(in secs)'].map(d)
        final_five = data.sort_values('Amplitudes', ascending=False)
        final_five = final_five[:5]
        final_five = final_five.to_json(orient='records')
        final_five = json.loads(final_five)
        final_five = jsonify(final_five)

        # TO DELETE THE AUDIO FILE FROM THE FOLDER AFTER ANALYSING IT
        if final_five:
            folder = "Tested/"
            for filename in os.listdir(folder):
                 file_path = os.path.join(folder, filename)
                 try:
                       if os.path.isfile(file_path) or os.path.islink(file_path):
                              os.unlink(file_path)
                       elif os.path.isdir(file_path):
                             shutil.rmtree(file_path)
                 except Exception as e:
                         print('Failed to delete %s. Reason: %s' % (file_path, e))
        # final_five = final_five.replace("/", "")
        # final_five = json.dumps(final_five, sort_keys=True, indent=4)
        return final_five
        # os.remove(files)


            # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # return redirect(url_for('index'))
    # return render_template("Template/speech.html")
    return """
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    <p>%s</p>
    """ % "<br>".join(os.listdir(app.config['UPLOAD_FOLDER'],))
    # folder = UPLOAD_FOLDER

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5001, debug=True)