import speech_recognition as sr
import numpy as np
import matplotlib.pyplot as plt
from easygui import buttonbox, enterbox
import os
from PIL import Image, ImageTk
from itertools import count
import tkinter as tk
import string

# base directory of this script for data files
# file resides in Translator/blogs already
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def blog_path(*parts: str) -> str:
    return os.path.join(BASE_DIR, *parts)
#import selecting
# obtain audio from the microphone

def show_phrase(phrase: str):
    """Display a GIF or sequence of letter images for the given phrase."""
    phrase = phrase.strip().lower()
    if not phrase:
        return
    isl_gif = [
        'address','ahemdabad','all','any questions','are you busy','are you angry','are you hungry','assam','august',
        'banana','banaras','banglore','be careful','bridge',
        'cat','christmas','church',
        'dasara','december','did you finish homework','do you have money','do you want something to drink','do you watch TV','dont worry',
        'flower is beautiful',
        'good afternoon','good morning','good question','grapes',
        'hello','hindu','hyderabad',
        'i am a clerk','i am fine','i am sorry','i am thinking','i am tired','i go to a theatre','i had to say something but i forgot','i like pink colour','i love to shop',
        'job','july','june',
        'karnataka','kerala','krishna',
        'lets go for lunch',
        'mango','may','mile','mumbai',
        'nagpur','nice to meet you'
        'open the door',
        'pakistan','please call me later','please wait for sometime','police station','post office','pune','punjab',
        'saturday','shall i help you','shall we go together tommorow','shop','sign language interpreter','sit down','stand up',
        'take care','temple','there was traffic jam','thursday','toilet','tomato','tuesday',
        'usa',
        'village',
        'wednesday','what are you doing','what is the problem','what is todays date','what is your father do','what is your mobile number','what is your name',
        'whats up','where is the bathroom','where is police station',
        'you are wrong'
    ]
    arr = list(string.ascii_lowercase)
    if phrase in isl_gif:
        root = tk.Tk()
        class ImageLabel(tk.Label):
            """a label that displays images, and plays them if they are gifs"""
            def load(self, im):
                if isinstance(im, str):
                    im = Image.open(im)
                self.loc = 0
                self.frames = []

                try:
                    for i in count(1):
                        self.frames.append(ImageTk.PhotoImage(im.copy()))
                        im.seek(i)
                except EOFError:
                    pass

                try:
                    self.delay = im.info['duration']
                except Exception:
                    self.delay = 100

                if len(self.frames) == 1:
                    self.config(image=self.frames[0])
                else:
                    self.next_frame()

            def unload(self):
                self.config(image=None)  # type: ignore[arg-type]
                self.frames = None

            def next_frame(self):
                if self.frames:
                    self.loc += 1
                    self.loc %= len(self.frames)
                    self.config(image=self.frames[self.loc])
                    self.after(self.delay, self.next_frame)
        lbl = ImageLabel(root)
        lbl.pack()
        gif_file = blog_path('ISL_Gifs', f"{phrase}.gif")
        lbl.load(gif_file)
        root.mainloop()
    else:
        for ch in phrase:
            if ch in arr:
                ImageAddress = blog_path('letters', ch + '.jpg')
                ImageItself = Image.open(ImageAddress)
                ImageNumpyFormat = np.asarray(ImageItself)
                plt.imshow(ImageNumpyFormat)
                plt.draw()
                plt.pause(0.8)


def func():
        r = sr.Recognizer()
        isl_gif=['address','ahemdabad','all','any questions','are you busy','are you angry','are you hungry','assam','august',
                 'banana','banaras','banglore','be careful','bridge',
                 'cat','christmas','church',
                 'dasara','december','did you finish homework','do you have money','do you want something to drink','do you watch TV','dont worry',
                 'flower is beautiful',
                 'good afternoon','good morning','good question','grapes',
                 'hello','hindu','hyderabad',
                 'i am a clerk','i am fine','i am sorry','i am thinking','i am tired','i go to a theatre','i had to say something but i forgot','i like pink colour','i love to shop',
                 'job','july','june',
                 'karnataka','kerala','krishna',
                 'lets go for lunch',
                 'mango','may','mile','mumbai',
                 'nagpur','nice to meet you'
                 'open the door',
                 'pakistan','please call me later','please wait for sometime','police station','post office','pune','punjab',
                 'saturday','shall i help you','shall we go together tommorow','shop','sign language interpreter','sit down','stand up',
                 'take care','temple','there was traffic jam','thursday','toilet','tomato','tuesday',
                 'usa',
                 'village',
                 'wednesday','what are you doing','what is the problem','what is todays date','what is your father do','what is your mobile number','what is your name',
                 'whats up','where is the bathroom','where is police station',
                 'you are wrong']
        
        
        arr=['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r', 's','t','u','v','w','x','y','z']
        with sr.Microphone() as source:
                # image   = "signlang.png"
                # msg="HEARING IMPAIRMENT ASSISTANT"
                # choices = ["Live Voice","All Done!"] 
                # reply   = buttonbox(msg,image=image,choices=choices)
                r.adjust_for_ambient_noise(source) 
                i=0
                while True:
                        print("I am Listening")
                        audio = r.listen(source)
                        # recognize speech using Sphinx
                        try:
                                a=r.recognize_google(audio)  # type: ignore[attr-defined]
                                a = a.lower()
                                print('You Said: ' + a.lower())
                                
                                for c in string.punctuation:
                                    a= a.replace(c,"")
                                    
                                if(a.lower()=='goodbye' or a.lower()=='good bye' or a.lower()=='bye'):
                                        print("oops!Time To say good bye")
                                        break
                                
                                elif(a.lower() in isl_gif):
                                    
                                    class ImageLabel(tk.Label):
                                            """a label that displays images, and plays them if they are gifs"""
                                            def load(self, im):
                                                if isinstance(im, str):
                                                    im = Image.open(im)
                                                self.loc = 0
                                                self.frames = []

                                                try:
                                                    for i in count(1):
                                                        self.frames.append(ImageTk.PhotoImage(im.copy()))
                                                        im.seek(i)
                                                except EOFError:
                                                    pass

                                                try:
                                                    self.delay = im.info['duration']
                                                except Exception:
                                                    self.delay = 100

                                                if len(self.frames) == 1:
                                                    self.config(image=self.frames[0])
                                                else:
                                                    self.next_frame()

                                            def unload(self):
                                                self.config(image=None)  # type: ignore[arg-type]
                                                self.frames = None

                                            def next_frame(self):
                                                if self.frames:
                                                    self.loc += 1
                                                    self.loc %= len(self.frames)
                                                    self.config(image=self.frames[self.loc])
                                                    self.after(self.delay, self.next_frame)
                                    root = tk.Tk()
                                    lbl = ImageLabel(root)
                                    lbl.pack()
                                    print(a)
                                    gif_file = blog_path('ISL_Gifs', f"{a.lower()}.gif")
                                    lbl.load(gif_file)
                                    root.mainloop()
                                else:
                                    for i in range(len(a)):
                                                    if(a[i] in arr):
                                            
                                                            ImageAddress = blog_path('letters', a[i] + '.jpg')
                                                            ImageItself = Image.open(ImageAddress)
                                                            ImageNumpyFormat = np.asarray(ImageItself)
                                                            plt.imshow(ImageNumpyFormat)
                                                            plt.draw()
                                                            plt.pause(0.8)
                                                    else:
                                                        continue

                        except Exception:
                               print(" ")
                        plt.close()
if __name__ == '__main__':
    image = blog_path('signlang.png')
    if not os.path.exists(image):
        raise FileNotFoundError(f"Image file {image} does not exist.")
    msg = "HEARING IMPAIRMENT ASSISTANT"
    choices = ["Live Voice", "Type Phrase", "All Done!"]
    while True:
        reply = buttonbox(msg, image=image, choices=choices)
        if reply == "Live Voice":
            func()
        elif reply == "Type Phrase":
            text = enterbox("Enter phrase to show:")
            if text:
                show_phrase(text)
        elif reply == "All Done!":
            break


#python manage.py runserver