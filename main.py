import pip
import sys
import traceback
import os
import math
import json
import _thread
from os.path import split
from traceback import print_exception, print_stack
from moviepy.video.VideoClip import ImageClip
import numpy as np
from PIL import ImageTk, Image
from moviepy import *
import moviepy.editor as mp
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkFont
from tkinter import filedialog as fd

config = json.load(open('lang.json'))
ext = tuple(config['ext'])
lang = config['lang']['en']

dst_dir_name = lang['dst_dir_name']


def addLine(str):
    return '>> ' + str + '\n'


def chooseLogo():
    global logo_filepath
    global widgets
    pgr_bar['value'] = 0
    logo_filepath = fd.askopenfilename(title=lang['btn1'], filetypes=(('png files', '*.png'), ('jpeg files', '*.jpg')))
    if logo_filepath == '':
        return
    widgets['lbl1']['text'] = logo_filepath
    txt_log.insert(tk.END, addLine(lang['lbl1'] + logo_filepath))


def chooseDir():
    global src_dir_path
    global dst_dir_path
    global widgets
    pgr_bar['value'] = 0
    src_dir_path = fd.askdirectory()
    dst_dir_path = src_dir_path + '/' + dst_dir_name
    if src_dir_path == '':
        return
    widgets['lbl2']['text'] = src_dir_path
    txt_log.insert(tk.END, addLine(lang['lbl2'] + src_dir_path))


def attachLogo():
    pgr_bar['value'] = 0

    if not ('logo_filepath' in globals() and logo_filepath != '' and 'src_dir_path' in globals() and src_dir_path != ''):
        return False

    files = list(filter(lambda a: (a.lower().endswith(ext) and a != logo_filepath.split('/')[-1]), os.listdir(src_dir_path)))
    unit = math.floor(100 / len(files))

    if unit == 0:
        txt_log.insert(tk.END, addLine(lang['msg1'] + str(ext)))
        return False

    def convertMediaFiles():
        try:
            # create the destination directory
            os.makedirs(dst_dir_path, exist_ok=True)

            logo_img = Image.open(logo_filepath)

            def scaleToImage(size_logo, size_img):
                
                new_size = size_logo

                for i in range(2):
                    if size_logo[i] > size_img[i]:
                        x = (size_img[i] - size_logo[i]) / size_logo[i]
                        new_size = [math.floor(y - y * x) for y in new_size]

                return tuple(new_size)
            
            for file in files:
                src_filepath = src_dir_path + '/' + file
                dst_filepath = dst_dir_path + '/' + file
                txt_log.insert(tk.END, addLine(lang['msg2'] + src_filepath))

                if file.lower().endswith('.mp4'):
                    video = mp.VideoFileClip(src_filepath)
                    new_logo_size = scaleToImage(logo_img.size, video.size)
                    limit_size = math.floor(min(video.size) * 0.2)
                    m = min(new_logo_size)
                    
                    if m > limit_size:
                        x = (m - limit_size) / m
                        new_logo_size = tuple([math.floor(y - y * x) for y in new_logo_size])
                    
                    print(video.size, new_logo_size)
                    
                    logo = mp.ImageClip(np.array(logo_img.resize(new_logo_size, Image.ANTIALIAS))).set_duration(video.duration).set_pos(('right', 'bottom'))
                    final = mp.CompositeVideoClip([video, logo], size=video.size).subclip(0)
                    final.write_videofile(dst_filepath)
                    final.close()
                    logo.close()
                    video.close()
                    txt_log.insert(tk.END, addLine(lang['msg8'] + dst_filepath))
                else:
                    img = Image.open(src_filepath)
                    new_logo_size = scaleToImage(logo_img.size, img.size)
                    limit_size = math.floor(min(img.size) * 0.2)
                    m = min(new_logo_size)

                    if m > limit_size:
                        x = (m - limit_size) / m
                        new_logo_size = tuple([math.floor(y - y * x) for y in new_logo_size])

                    print(img.size, new_logo_size)

                    scaled_logo_img = logo_img.resize(new_logo_size, Image.ANTIALIAS)
                    img.paste(scaled_logo_img, [(a - new_logo_size[i]) for i, a in enumerate(img.size)], (scaled_logo_img if scaled_logo_img.mode == "RGBA" else None))
                    img.save(dst_filepath, quality=100)
                    scaled_logo_img.close()
                    img.close()
                    txt_log.insert(tk.END, addLine(lang['msg7'] + dst_filepath))
                
                pgr_bar['value'] += unit

            logo_img.close()
            txt_log.insert(tk.END, '\n')
            txt_log.insert(tk.END, addLine(lang['msg9'] + dst_dir_path))
            txt_log.insert(tk.END, '\n')
            pgr_bar['value'] = 100
        except Exception as e:
            traceback.print_exc()
            txt_log.insert(tk.END, addLine(lang['msg10']))

    try:
        _thread.start_new_thread(convertMediaFiles, ())
    except Exception as e:
        traceback.print_exc()
        txt_log.insert(tk.END, addLine(lang['msg10']))
        return


root = tk.Tk()
root.iconbitmap('logo.ico')
root.minsize(500, 500)
root.title("Hallmark")


frm_lang = tk.Frame(root, relief=tk.RAISED, height=50)
frm_lang.pack(fill=tk.X, side=tk.TOP)
frm_lang.pack_propagate(0)

frm_main = tk.Frame()
frm_main.pack(expand=True, fill='both')
frm_main.pack_propagate(0)


images = []


for file in os.listdir('img/langs'):
    images.append(
        (
            file.split('.')[0],
            ImageTk.PhotoImage(Image.open('img/langs/' + file).resize((30, 30), Image.ANTIALIAS))
        )
    )
    btn = tk.Button(master=frm_lang, image=images[-1][1], width=30, height=30, compound=tk.CENTER, text='', command=lambda e=images[-1][0]: chooseLang(e))
    btn.pack(padx=5, pady=10, side=tk.RIGHT)


def chooseLang(lg):
    global config
    global lang
    global widgets
    global dst_dir_name
    lang = config['lang'][lg]
    dst_dir_name = lang['dst_dir_name']

    for name, widget in widgets.items():
        if not isinstance(widget, tk.Label):
            widget['text'] = lang[name]


widgets = {
    # Button for choosing logo file
    "btn1": tk.Button(master=frm_main, bg='light gray', width=30, text=lang['btn1'], anchor='n', command=chooseLogo),
    # Label that dislays the filepath of the chosen logo
    "lbl1": tk.Label(master=frm_main, anchor='n'),
    # Button for choosing the directory containing the multimedia file to attach the logo to
    "btn2": tk.Button(master=frm_main, bg='light gray', width=30, text=lang['btn2'], anchor='n', command=chooseDir),
    # Label that dislays the path of the chosen directory
    "lbl2": tk.Label(master=frm_main, anchor='n'),
    # Button to start the job
    "btn3": tk.Button(master=frm_main, bg='light gray', width=30, text=lang['btn3'], anchor='n', command=attachLogo)
}


for _, widget in widgets.items():
    widget.pack(expand=True, padx=10, pady=10)


pgr_bar = ttk.Progressbar(master=frm_main, orient=tk.HORIZONTAL, length=100, mode='determinate', value=0)
pgr_bar.pack(expand=True, fill=tk.X, padx=10, pady=10)
txt_log = tk.Text(master=frm_main, height=100)
txt_log.pack(expand=True, fill=tk.X, padx=10, pady=10)

root.mainloop()
