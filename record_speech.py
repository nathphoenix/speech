import os, glob, shutil
from flask import Flask, request, redirect, url_for, jsonify, render_template, make_response
# from werkzeug import secure_filename
from werkzeug.utils import secure_filename
import glob, os
import librosa
import pprint
import json
import pyaudio
import wave
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

class Page(Resource):
    @classmethod
    def pageNotFound(cls):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('404.html'),200,headers)

class Audio_Record(Resource):
    @classmethod
    def get(cls):
        folder = "./static/Test/"
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        CHUNK = 1024
        RECORD_SECONDS = 5
        try:
            os.makedirs('./static/Test')
        except OSError:
            pass
        WAVE_OUTPUT_FILENAME = "static/Test/file.wav"
        
        audio = pyaudio.PyAudio()

        # start Recording
        stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
        print ("recording...")
        frames = []

        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
        print ("finished recording")


        # stop Recording
        stream.stop_stream()
        stream.close()
        audio.terminate()

        waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        waveFile.setnchannels(CHANNELS)
        waveFile.setsampwidth(audio.get_sample_size(FORMAT))
        waveFile.setframerate(RATE)
        waveFile.writeframes(b''.join(frames))
        waveFile.close()



        # MAJOR AUDIO ANALYSIS

        # https://storage.cloud.google.com/audiofilex/sample.wav
        conversation = list()
        client = speech.SpeechClient()
        taco = "./static/Test"
        parent_dir = os.getcwd() + taco
        files = [pdf_file for pdf_file in glob.glob(os.path.join(parent_dir, '*'))]
        for file in tqdm(sorted(files)):

            try:
                with open(file, 'rb') as audio_file:
                    content = audio_file.read()
            except FileNotFoundError:
                print("Oops! No audio files found")

            audio = speech.types.RecognitionAudio(content=content)
            enable_word_time_offsets = True
            language_code="en-US"
            config = speech.types.RecognitionConfig(
                enable_word_time_offsets = enable_word_time_offsets,
                language_code = language_code)

            response = client.recognize(config, audio)
            try:
              result = response.results[0]
            #   if result is None:
            # direct 500 error, such as abort(500)
                #   return render_template("index.html"), 500
            except Exception as e:
              print(e)
              return Page.pageNotFound()
            #   page = Page.pageNotFound(cls)
            #   return page
            #   return render_template('404.html', error = "hey this is index error")
            # First alternative is the most probable result
            alternative = result.alternatives[0]
            print(u"Transcript: {}".format(alternative.transcript))
            # Print the start and end time of each word
            for word in alternative.words:
                print(u"Word: {}".format(word.word))
                print(
                    u"Start time: {} seconds {} nanos".format(
                        word.start_time.seconds, word.start_time.nanos
                    )
                )
                print(
                    u"End time: {} seconds {} nanos".format(
                        word.end_time.seconds, word.end_time.nanos
                    )
                )

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

        import pandas as pd
        import numpy as np
        matrix = np.matrix([words,starts,ends])
        df = pd.DataFrame(data=matrix)
        new = df.T

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

        # data.to_csv("sep.csv", index=False)
        # new_data = pd.read_csv("sep.csv")
        # new_data.head()
        # df display
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
        remove_na.to_csv("time.csv", index=False)
        df = pd.read_csv("time.csv")
        df["Nanos_secs"] = round(df["Nanos"] / 1000000000, 2)
        df["End_Nanos_secs"] = round(df["End_Nanos"] / 1000000000, 2)
        df = df[["Words", "Start_Secs", "Nanos_secs", "End_Secs", "End_Nanos_secs"]]
        df['Start_time(in_sec)'] = round(df['Start_Secs'] + df['Nanos_secs'], 2)
        df['End_time(in_sec)'] = round(df['End_Secs'] + df['End_Nanos_secs'], 2)
        df['Total_Time_words'] = round(df['Start_time(in_sec)'], 2)
        Word_time_stamp = df[["Words", "Start_time(in_sec)", "End_time(in_sec)", "Total_Time_words"]]



        # SECOND ANALYSIS OF AUDIO FILE BY LIBROSA

        sns.set() # Use seaborn's default style to make attractive graphs
        plt.rcParams['figure.dpi'] = 100 # Show nicely large images in this notebook
        for audios in files:
            print(audios)
        samples, sampling_rate = librosa.load(audios)
        samples, sampling_rate = librosa.load(files[0])
        #furrier transform of data
        data_fft = np.fft.rfft(samples)

        #frequencies
        frequencies = np.abs(data_fft)

        # print("sampling rate is :", sampling_rate)
        # print("Number of samples :", len(samples))

        max1 = max(samples)
        # print("Maximum amplitude", round(max1, 2))
        min1 = min(samples)
        # print("Minimum amplitude", round(min1, 2))

        duration = len(samples) / sampling_rate
        # print(duration)



        # TIME EXTRACTION FROM THE LIBROSA ANALYSIS

        df = pd.DataFrame(samples, columns=['Amplitudes'])
        # df = d["Amplitudes"]
        df.index = [(1/sampling_rate)*i for i in range(len(df.index))]
        df.head()
        df.to_csv("amp.csv", index=True)
        amp = pd.read_csv("amp.csv")
        amp.rename(columns = {"Unnamed: 0": "Time"}, inplace = True)

        # amp.sort_values('Amplitudes', ascending=False)

        amp["Time"] = amp["Time"].round(2)
        amp = amp[["Time", "Amplitudes"]]
        # amp = amp.abs()
        # amp = amp.round(2)
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
            for s, e in data[['Start_time(in_sec)','End_time(in_sec)']].to_numpy()}

        data['Amplitudes'] = data['End_time(in_sec)'].map(d)
        final_five = data
        # each_word_length = final_five["Total_Time_words"].to_list()
        # print(each_word_length)
        # new_dict = [{k:v} for k,v in zip(final_five["Words"], final_five["Total_Time_words"])]
        # print(new_dict)
        new_dict = final_five[["Total_Time_words", "Words"]]
        dictionary = new_dict.T.to_dict()
        last_dict = [v for k, v in dictionary.items()]
        print(last_dict)
        reset_data = final_five.sort_values('Amplitudes', ascending=False)
        reset_data = reset_data.reset_index(drop=True)
        final_five_sort = reset_data["Words"][0]
        final_five = final_five["Words"].to_list()
        final_five.append(final_five_sort)
        # if final_five:
        #     folder = "./static/Test"
        #     for filename in os.listdir(folder):
        #          file_path = os.path.join(folder, filename)
        #          try:
        #                if os.path.isfile(file_path) or os.path.islink(file_path):
        #                       os.unlink(file_path)
        #                elif os.path.isdir(file_path):
        #                      shutil.rmtree(file_path)
        #          except Exception as e:
        #                  print('Failed to delete %s. Reason: %s' % (file_path, e))
        # final_five = final_five.replace("/", "")
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('speech.html', word_list = final_five, word_time=last_dict), headers)

        # final_five = final_five.to_json(orient='records')
        # final_five = json.loads(final_five)
        # final_five = jsonify(final_five)
        # contains = []
        # for items in final_five:
        #   contains.append(items.words)
        # return contains
        # print(final_five.columns.values)

        # FOR WORKING WITH TABLES
        # columnNames = final_five.columns.values
        # headers = {'Content-Type': 'text/html'}
        # return make_response(render_template('speech.html', tables=[final_five.to_html(classes='data')], colnames=columnNames), headers)
# columnNames = df.columns.values
#         headers = {'Content-Type': 'text/html'}
#         return make_response(render_template('speech.html', records=final_five, colnames=columnNames), headers)
# return make_response(render_template('index.html'),200,headers)