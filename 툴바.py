from tkinter import *
from PIL import Image,ImageTk
import pyautogui
import os
import fnmatch
from tkinter import filedialog
from tkinter import messagebox
import signal
import psutil
import cv2
import numpy
import threading
import time

is_recording=False
out=None

def take_screenshot():
    screenshot=pyautogui.screenshot()
    screenshot.save("screenshot.png")

def choose_directory():
    global directory
    directory=filedialog.askdirectory()
    if directory:
        dir.set(directory)
        update_file_list(directory)

def update_file_list(directory):
    list.delete(0,END)
    for root,dirs,files in os.walk(directory) :
        for file in files:
            list.insert(END,os.path.join(root,file))

def search_files():
    pat=entry.get()
    if not pat:
        print("검색 패턴을 입력해 주세요")
    if directory:
        list.delete(0,END)
        for root,dirs,files in os.walk(directory):
            for file in files:
                if fnmatch.fnmatch(file,f'*{pat}*'):
                    list.insert(END,os.path.join(root,file))

def new_file_window():
    global dir,list,entry,text
    search_file=Toplevel()
    btn_3=Button(search_file,text="경로",command=choose_directory)
    btn_3.pack()
    dir=StringVar()
    dir.set("디렉토리를 선택하세요")
    label_1=Label(search_file,textvariable=dir)
    label_1.pack()
    label_2=Label(search_file,text="검색 패턴")
    label_2.pack()
    entry=Entry(search_file)
    entry.pack()
    btn_4=Button(search_file,text="검색",command=search_files)
    btn_4.pack()
    list=Listbox(search_file,width=80,height=15)
    list.pack()
    list.bind("<<ListboxSelect>>",show_file_content)
    text=Text(search_file)
    text.pack(fill=BOTH,expand=True)
    btn_5=Button(search_file,text="저장",command=save_as_file)
    btn_5.pack()

def show_file_content(event):
    s_file=list.get(list.curselection())
    if os.path.isfile(s_file):
        f=open(s_file,'r',encoding="utf-8")
        text.delete(1.0,END)
        text.insert(END,f.read())
        f.close()

def save_as_file():
    save_path=filedialog.asksaveasfilename(defaultextension=".txt",filetypes=[("Text files","*.txt"),("All files","*.*")])
    if save_path:
        f=open(save_path,'w',encoding="utf-8")
        f.write(text.get(1.0,END))
        f.close()
        messagebox.showinfo("텍스트 저장",f"파일이 {save_path}에 저장되었습니다")

def shut_down():
    confirm=messagebox.askokcancel("전원 끄기","정말로 전원을 끄시겠습니까?")
    if confirm:
        os.system("shutdown /s /t 1")
        
def shut_all():
    confirm=messagebox.askokcancel("모두 종료","정말로 모든 프로그램을 종료하시겠습니까?")
    if confirm:
        for process in psutil.process_iter():
            try:
                if os.getpid()!=process.pid:
                    process.terminate() 
            except (psutil.NoSuchProcess,psutil.AccessDenied,psutil.ZombieProcess):
                pass

def on_icon_click():
    file_path=filedialog.askopenfilenames(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")] )
    if len(file_path)!=2:
        messagebox.showerror("오류","이미지 2개를 선택해주세요")
        return
    image_1=Image.open(file_path[0])
    image_2=Image.open(file_path[1])
    image_2=image_2.resize(image_1.size)
    collage_width=max(image_1.width,image_2.width)
    collage_height=image_1.height+image_2.height
    collage_image=Image.new("RGBA",(collage_width,collage_height))
    collage_image.paste(image_1,(0,0))
    collage_image.paste(image_2,(0,image_1.height))
    collage_image.save("collage_imgage.png")
    messagebox.showinfo("완료","저장이 완료되었습니다")

def start_recording():
    global is_recording,out
    if is_recording:
        messagebox.showinfo("경고","녹화가 이미 진행 중 입니다")
        return
    screen_width,screen_height=pyautogui.size()
    fourcc=cv2.VideoWriter_fourcc(*"XVID")
    out=cv2.VideoWriter("screen_record.avi",fourcc,20.0,(screen_width,screen_height))
    is_recording=True
    update_button()
    threading.Thread(target=record_screen).start()

def record_screen():
    global is_recording,out
    while is_recording:
        img=pyautogui.screenshot()
        frame=numpy.array(img)
        frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        out.write(frame)
        time.sleep(0.05)

def update_button():
    global is_recording
    if is_recording:
        btn_6.grid_forget()
        btn_7.grid(row=0,column=5)
    else:
        btn_7.grid_forget()
        btn_6.grid(row=0,column=5)

def stop_recording():
    global is_recording,out
    if not is_recording:
        messagebox.showinfo("경고","녹화중이 아닙니다")
        return
    is_recording=False
    out.release()
    update_button()
    messagebox.showinfo("녹화","영상 파일이 저장되었습니다")
                  
root=Tk()

image_1=Image.open("camera_icon.png").resize((32,32))
image_2=Image.open("mag_icon.png").resize((32,32))
camera_icon=ImageTk.PhotoImage(image_1)
mag_icon=ImageTk.PhotoImage(image_2)
btn_1=Button(root,image=camera_icon,command=take_screenshot)
btn_1.grid(row=0,column=0)
btn_2=Button(root,image=mag_icon,command=new_file_window)
btn_2.grid(row=0,column=1)
image_3=Image.open("power_icon.png").resize((32,32))
power_icon=ImageTk.PhotoImage(image_3)
btn_3=Button(root,image=power_icon,command=shut_down)
btn_3.grid(row=0,column=2)
image_4=Image.open("shutall_icon.png").resize((32,32))
shutall_icon=ImageTk.PhotoImage(image_4)
btn_4=Button(root,image=shutall_icon,command=shut_all)
btn_4.grid(row=0,column=3)
btn_5=Button(root,text="콜라주",command=on_icon_click)
btn_5.grid(row=0,column=4)
btn_6=Button(root,text="녹화",command=start_recording)
btn_6.grid(row=0,column=5)
btn_7=Button(root,text="녹화 중지",command=stop_recording)
btn_7.grid_forget()

root.mainloop()