# importing libraries
import shutil
import speech_recognition as sr
import os
from pydub import AudioSegment
from pydub.silence import split_on_silence
import tkinter as tk
from google_trans_new import google_translator
from youtube_transcript_api import *
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import requests


#TODO: Implement async/await to make the program more responsive
#TODO : Implement more language support
#TODO: Support more audio files types
#TODO: Implement way to generate a brand new video from youtube video with the translated subtitles
#Constants
black = "#000000"
white = "#C0C0C0"
BACKGROUNDCLOUR = "#f9a9c3"
LIGHTYELLOW = "#fffdd0"
BLUEGREEN = "#62b5b7"


#Global Variables
language_source =["ja", "en"]
language_target= "en"
youtube_video_code = ""
choosen_audio_file_path = None
translation_output = ""
translator = google_translator()
r = sr.Recognizer()
#functionalities
def save_youtube_code_video():
    global youtube_video_code
    global youtube_video_code_entry_box
    youtube_video_code = youtube_video_code_entry_box.get().replace(" ", "")
    print(youtube_video_code)

def get_audio_directory():
    global choosen_audio_file_path
    path = filedialog.askopenfilename(initialdir = "/",title = "Please select your audio file",  filetypes = (("wav files","*.wav"),("all files","*.*")))
    choosen_audio_file_path = path
    print(choosen_audio_file_path)

def change_language_source_code_to_google_cloud_speech_code():
    #TODO: Currently only support japaness source, make a dictionary of language: google cloud speech code and get the code from that dict
    global language_source
    language_source = "ja-JP"

def change_language_source_code_to_youtube_language_code():
    # TODO: Currently only support japaness source, make a dictionary of language: youtube code and get the code from that dict
    global language_source
    language_source = ["ja", "en"]
    pass

def showing_translation_result():
    global translation_output
    global output_text
    output_text.delete("1.0", END)
    output_text.insert("1.0", translation_output)

def translating_youtube_video_transcript():
    global language_source
    global language_target
    global translation_output
    global youtube_video_code

    try:
        video_subtitle = YouTubeTranscriptApi.get_transcript(youtube_video_code, languages=language_source)
        youtube_video_code_entry_box.delete(0, END)
    except VideoUnavailable:
        messagebox.showerror("An error has occured", "Could not get the transcript from youtube \n Please ensure the following:  \n The Youtube video code is correct \n The youtube video has the correct language subtitle \n You have a strong wifi connection ")

        return
    else:
        messagebox.showinfo("Please do not close the program",
                            "PLEASE DO NOT CLOSE THE PROGRAM \n It is currently in the process of translating \n this process can take from 1 minute to 1 hour depends on the length of the audio \n So grab a cookie cause it's gonna be long :))")
        for part in video_subtitle:
            text = part["text"]
            print(text)
            translated_text = translator.translate(text, lang_tgt=language_target)
            print(translated_text)
            part["text"] = translated_text
            try:
                translation_output += "\n" + str(part["start"]) + "\n" + part["text"] + "\n"
            except UnicodeEncodeError:
                continue
            except:
                messagebox.showerror("An error has occured", "Please try again")
                return



def get_large_audio_transcription(path):
    """
    Splitting the large audio file into chunks
    and apply speech recognition on each of these chunks
    """
    # open the audio file using pydub
    sound = AudioSegment.from_wav(path)
    # split audio sound where silence is 700 miliseconds or more and get chunks
    chunks = split_on_silence(sound,
        # experiment with this value for your target audio file
        min_silence_len = 500,
        # adjust this per requirement
        silence_thresh = sound.dBFS-14,
        # keep the silence for 1 second, adjustable as well
        keep_silence=500,
    )
    folder_name = "audio-chunks"
    # create a directory to store the audio chunks
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)
    whole_text = ""
    # process each chunk
    for i, audio_chunk in enumerate(chunks, start=1):
        # export audio chunk and save it in
        # the `folder_name` directory.
        chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
        audio_chunk.export(chunk_filename, format="wav")
        # recognize the chunk
        with sr.AudioFile(chunk_filename) as source:
            audio_listened = r.record(source)
            # try converting it to text
            try:
                text = r.recognize_google(audio_listened, language= language_source)
            except sr.UnknownValueError as e:
                print("Error:", str(e))
                continue
            else:
                text = f"{text.capitalize()}. "
                print(text)
                print(chunk_filename, ":", text)

                whole_text += text
    # return the text for all chunks detected
    return whole_text

def translating_audio_file():
    global translation_output

    try:
        messagebox.showinfo("Please do not close the program",
                            " PLEASE DO NOT CLOSE THE PROGRAM \n It is currently in the process of translating \n this process can take from 1 minute to 1 hour depends on the length of the audio \n So grab a cookie cause it's gonna be long :))")
        audio_transcript = get_large_audio_transcription(choosen_audio_file_path)
    except:
        messagebox.showerror("An error has occured", "Please try again and ensure the following: \n The language source is the same the video's language \n You have a strong wifi connection \n You have selected a wav file")
        return
    else:

        translated_text = translator.translate(audio_transcript, lang_tgt= language_target)
        translation_output = translated_text
        print(translation_output)
#Button Behaviours
def get_youtube_transcript_button_behaviour():
    menu_title.config(text = "Loading...")
    save_youtube_code_video()
    change_language_source_code_to_youtube_language_code()
    translating_youtube_video_transcript()
    showing_translation_result()
    menu_title.config(text="Audio Translation")

def upload_audio_file_button_behaviour():
    menu_title.config(text="Loading...")
    get_audio_directory()
    change_language_source_code_to_google_cloud_speech_code()
    translating_audio_file()
    showing_translation_result()
    menu_title.config(text="Audio Translation")

#Delete unnecessay audio chunks
try:
    audio_chunks_path = "./audio-chunks"
    shutil.rmtree(audio_chunks_path)
except FileNotFoundError:
    pass

#Set up window
window = Tk()
window.config(width = 800, height = 800, bg = BACKGROUNDCLOUR)
window.title("Audio Translation")
window.minsize(800,800)
#Set up main menu
#Menu Labels
menu_title = Label(text = "Audio Translation", font = ("Times", 24, "bold italic"),bg = BACKGROUNDCLOUR)
menu_title.grid(column = 0, row = 0, columnspan = 2)
instruction_to_get_video_code = Label(text = "Video code is in the URL and usually after the 'v='", bg = BACKGROUNDCLOUR)
instruction_to_get_video_code.grid(column = 0, row = 2)
compatible_file_text = Label(text = "Currently only compatible with wav files", bg = BACKGROUNDCLOUR)
compatible_file_text.grid(column = 1, row = 4)
language_source_label = Label(text = "Current language source is Japanese", bg = BLUEGREEN, height = 5, width = 30)
language_source_label.grid(column = 0, row = 5)
language_target_label = Label(text = "Currently language target is English", bg = BLUEGREEN, height = 5, width = 30)
language_target_label.grid(column = 1, row = 5)
output_text_title = Label(text = "Translation Output: ", bg = BACKGROUNDCLOUR, font = (("Times", 15, "bold italic")))
output_text_title.grid(column = 0, row = 7)
output_text = Text(padx = 10, pady = 10, height = 12, width = 60, font = ("Helvetica", "11"), bg = white)
output_text.grid(column = 0, columnspan = 3, row = 8, rowspan = 3)
output_text.tag_config("center", justify = "center")




#Buttons
#Get Transcript From Youtube
youtube_video_code_entry_box = Entry(width = 50)
youtube_video_code_entry_box.grid(column = 0, row = 1)
choose_youtube_mode_button = Button(text = "Get subtitles from youtube", height = 3, width = 25, command = get_youtube_transcript_button_behaviour, bg = LIGHTYELLOW)
choose_youtube_mode_button.grid(column = 1, row = 1)
get_file_from_dir_button = Button(text = "Get files from directory",height = 5, width = 25, command = upload_audio_file_button_behaviour, bg = LIGHTYELLOW)
get_file_from_dir_button.grid(column = 1, row =3)

change_language_source_button = Button(text = "Change Language Source")
change_language_source_button.grid(column = 0, row = 6)
change_language_target_button = Button(text = "Change Language Target")
change_language_target_button.grid(column = 1, row = 6)



window.mainloop()




