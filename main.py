import os
import math
import json
import _thread
from os.path import split
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

    try:
        os.makedirs(dst_dir_path, exist_ok=True)
    except Exception as e:
        txt_log.insert(tk.END, e)
        return False

    files = list(filter(lambda a: (a.lower().endswith(ext) and a != logo_filepath), os.listdir(src_dir_path)))
    unit = math.floor(100 / len(files))

    if unit == 0:
        txt_log.insert(tk.END, addLine(lang['msg1'] + str(ext)))
        return False

    def convertMediaFiles():
        for file in files:
            src_filepath = src_dir_path + '/' + file
            dst_filepath = dst_dir_path + '/' + file
            txt_log.insert(tk.END, addLine(lang['msg2'] + src_filepath))
            logoImg = Image.open(logo_filepath)
            logoWidth, logoHeight = logoImg.size

            if file.lower().endswith('.mp4'):
                video = mp.VideoFileClip(src_filepath)
                vW, vH = video.size
                if vW <= logoWidth:
                    txt_log.insert(tk.END, addLine(lang['msg3'] + dst_filepath))
                    continue
                if vH <= logoHeight:
                    txt_log.insert(tk.END, addLine(lang['msg4'] + dst_filepath))
                    continue
                logo = mp.ImageClip(logo_filepath).set_duration(video.duration).set_pos(('right', 'bottom'))
                final = mp.CompositeVideoClip([video, logo])
                final.subclip(0).write_videofile(dst_filepath)
                txt_log.insert(tk.END, addLine(lang['msg8'] + dst_filepath))
            else:
                img = Image.open(src_filepath)
                imgWidth, imgHeight = img.size

                if imgWidth <= logoWidth:
                    txt_log.insert(tk.END, addLine(lang['msg5'] + src_filepath))
                    continue

                if imgHeight <= logoHeight:
                    txt_log.insert(tk.END, addLine(lang['msg6'] + src_filepath))
                    continue

                img.paste(logoImg, (imgWidth - logoWidth, imgHeight - logoHeight), logoImg)
                img.save(dst_filepath)
                txt_log.insert(tk.END, addLine(lang['msg7'] + dst_filepath))

            pgr_bar['value'] += unit
        
        txt_log.insert(tk.END, addLine(lang['msg9'] + dst_dir_path))
        txt_log.insert(tk.END, '--------------------------------\n')

    try :
        _thread.start_new_thread(convertMediaFiles, ())
    except Exception as e:
        print(e)
        return

    pgr_bar['value'] = 100
    txt_log.insert(tk.END, addLine(u"{}".format(lang['msg9']) + dst_dir_path))


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
    lang = config['lang'][lg]
    for name, widget in widgets.items():
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


pgr_bar = ttk.Progressbar(master=frm_main, orient=tk.HORIZONTAL, length=100, mode='determinate')
pgr_bar.pack(expand=True, fill=tk.X, padx=10, pady=10)
txt_log = tk.Text(master=frm_main, height=100)
txt_log.pack(expand=True, fill=tk.X, padx=10, pady=10)

root.mainloop()
