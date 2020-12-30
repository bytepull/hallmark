import os
import math
from PIL import Image
from moviepy import *
import moviepy.editor as mp
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog as fd

ext = ('.png', '.jpg', 'jpeg', '.mp4')
dst_dir_name = 'immagini_con_logo'

def addLine(str):
    return '>> ' + str + '\n'

def scegliLogo():
    global logo_filepath
    logo_filepath = fd.askopenfilename(title='Seleziona il logo', filetypes=(('png files', '*.png'), ('jpeg files', '*.jpg')))
    pgr_bar['value'] = 0
    lbl_logoPath['text'] = logo_filepath
    txt_log.insert(tk.END, addLine("Caricato logo: " + logo_filepath))


def scegliCartella():
    global src_dir_path
    src_dir_path = fd.askdirectory()
    pgr_bar['value'] = 0
    lbl_folderPath['text'] = src_dir_path
    txt_log.insert(tk.END, addLine("Caricata cartella: " + src_dir_path))


def applicaLogo():
    pgr_bar['value'] = 0

    if not ('logo_filepath' in globals() and logo_filepath != '' and 'src_dir_path' in globals() and src_dir_path != ''):
        return False

    dst_dir_path = src_dir_path + '/' + dst_dir_name

    try:
        os.makedirs(dst_dir_path, exist_ok=True)
    except Exception as e:
        txt_log.insert(tk.END, e)
        return False

    files = list(filter(lambda a: (a.lower().endswith(ext) and a != logo_filepath), os.listdir(src_dir_path)))
    unit = math.floor(100 / len(files))

    if unit == 0 :
        txt_log.insert(tk.END, addLine('Nessun file idoneo trovato. I formati supportati sono: ' + str(ext)))
        return False

    for file in files:
        src_filepath = src_dir_path + '/' + file
        dst_filepath = dst_dir_path  + '/' + file
        txt_log.insert(tk.END, addLine('Sto processando: ' + src_filepath))
        logoImg = Image.open(logo_filepath)
        logoWidth, logoHeight = logoImg.size

        if file.lower().endswith('.mp4'):
            video = mp.VideoFileClip(src_filepath)
            vW, vH = video.size
            if vW <= logoWidth:
                txt_log.insert(tk.END, addLine('Il video con il logo è stato salvato in: ' + dst_filepath))
                continue
            if vH <= logoHeight:
                txt_log.insert(tk.END, addLine('Il video con il logo è stato salvato in: ' + dst_filepath))
                continue
            logo = mp.ImageClip(logo_filepath).set_duration(video.duration).set_pos(('right', 'bottom'))
            final = mp.CompositeVideoClip([video, logo])
            final.subclip(0).write_videofile(dst_filepath)
            txt_log.insert(tk.END, addLine('Il video con il logo è stato salvato in: ' + dst_filepath))
        else:
            img = Image.open(src_filepath)
            imgWidth, imgHeight = img.size

            if imgWidth <= logoWidth:
                txt_log.insert(tk.END, addLine('L\'immagine ha una larghezza minore del logo!'))
                continue

            if imgHeight <= logoHeight:
                txt_log.insert(tk.END, addLine('L\'immagine ha una altezza minore del logo!'))
                continue

            img.paste(logoImg, (imgWidth - logoWidth, imgHeight - logoHeight), logoImg)
            img.save(dst_filepath)
            txt_log.insert(tk.END, addLine('Immagine salvata: ' + dst_filepath))

        pgr_bar['value'] += unit

    pgr_bar['value'] = 100
    txt_log.insert(tk.END, addLine(
        "Logo aggiunto! Le immagini sono state salvate nella cartella: " + dst_dir_path))


root = tk.Tk()
root.minsize(500, 500)
root.title("Aggiungi logo")

frm_main = tk.Frame(root, width=300, height=300)

btn_openLogo = tk.Button(
    frm_main, width=30, text="Scegli Logo", anchor='n', command=scegliLogo)
lbl_logoPath = tk.Label(frm_main, anchor='n')
btn_scegliCartella = tk.Button(
    frm_main, width=30, text="Scegli Cartella", anchor='n', command=scegliCartella)
lbl_folderPath = tk.Label(frm_main)
btn_convert = tk.Button(
    frm_main, width=30, text="Aggiungi Logo", anchor='n', command=applicaLogo)
pgr_bar = ttk.Progressbar(
    master=frm_main, orient=tk.HORIZONTAL, length=100, mode='determinate')
txt_log = tk.Text(frm_main, height=100)

frm_main.pack(expand=True, fill='both')
frm_main.pack_propagate(0)

btn_openLogo.pack(expand=True, padx=10, pady=10)
lbl_logoPath.pack(expand=True, padx=10, pady=10)
btn_scegliCartella.pack(expand=True, padx=10, pady=10)
lbl_folderPath.pack(expand=True, padx=10, pady=10)
btn_convert.pack(expand=True, padx=10, pady=10)
pgr_bar.pack(expand=True, fill=tk.X, padx=10, pady=10)
txt_log.pack(expand=True, fill=tk.X, padx=10, pady=10)

root.mainloop()
