import tkinter as tk
from PIL import Image, ImageTk

class GuitarTrainerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Guitar Trainer")  #设置窗口标题
        self.master.geometry("500x400")  #设置窗口尺寸

        # 添加全屏显示和退出全屏的功能
        self.master.attributes('-fullscreen', True)
        
        # 添加一个按钮，用于退出全屏
        button_exit_fullscreen = tk.Button(self.master, text="Exit Fullscreen", command=self.exit_fullscreen)
        button_exit_fullscreen.pack()
    
        # 创建一个包含两个Frame的Frame
        self.frame = tk.Frame(self.master)
        self.frame.pack(fill="both", expand=True)

        # 创建左侧song_Frame
        self.song_frame = tk.Frame(self.frame)
        self.song_frame.pack(side="left", fill="both", expand=True)
        
        # 创建左侧歌曲名的Label和Listbox
        self.song_label = tk.Label(self.song_frame, text="吉他谱名", font=("宋体", 20), width=10)
        self.song_label.pack(side="top", padx=10, pady=10)

        self.song_listbox = tk.Listbox(self.song_frame, height=40, width=5)
        self.song_listbox.pack(side="left", fill="both", expand=True)
        
        # 添加一些样例歌曲
        self.song_listbox.insert(tk.END, "Song 1")
        self.song_listbox.insert(tk.END, "Song 2")
        self.song_listbox.insert(tk.END, "Song 3")
        
        # 创建右侧图片Frame
        self.tab_frame = tk.Frame(self.frame)
        self.tab_frame.pack(side="right", fill="both", expand=True)

        # 创建右侧Label和Listbox
        self.tab_label = tk.Label(self.tab_frame, text="吉他谱", font=("宋体", 20))
        self.tab_label.pack(side="top", padx=10, pady=10)

        self.image_label = tk.Label(self.tab_frame)
        self.image_label.pack(side="left", fill="both", expand=True)
        
        # 加载图片并显示
        img = Image.open("./pic/test.gif")

        # 获取Label的大小
        label_width = self.image_label.winfo_width()
        label_height = self.image_label.winfo_height()

        # 缩放图片
        img = img.resize((label_width, label_height), Image.ANTIALIAS)

        self.image = ImageTk.PhotoImage(img)
        self.image_label.config(image=self.image)

        # 点击listbox的内容，触发事件
        self.song_listbox.bind("<<ListboxSelect>>", self.show_tab_data)
        # 改变窗口尺寸时，同时改变照片大小
        self.image_label.bind("<Configure>", self.resize_image)
        
    
    def show_tab_data(self, event):
        # get selected song name
        selection = event.widget.curselection()
        song_name = event.widget.get(selection[0])
        
        # load tab data from file
        with open(song_name + ".txt", "r") as f:
            tab_data = f.read()
        
        # display tab data in text widget
        self.tab_text.delete("1.0", tk.END)
        self.tab_text.insert(tk.END, tab_data)
    
    def exit_fullscreen(self):
        self.master.attributes('-fullscreen', False)

    def resize_image(self, evnet, img_url = "./pic/test.gif"):
        # 获取Label的大小
        label_width = self.image_label.winfo_width()
        label_height = self.image_label.winfo_height()

        img = Image.open(img_url)

        # 计算缩放比例
        img_width, img_height = img.size
        width_ratio = label_width / img_width
        height_ratio = label_height / img_height
        ratio = min(width_ratio, height_ratio)

        # 缩放图片
        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)
        img = img.resize((new_width, new_height), Image.ANTIALIAS)

        # 更新图片
        self.image = ImageTk.PhotoImage(img)
        self.image_label.config(image=self.image)

root = tk.Tk()
app = GuitarTrainerApp(root)
root.mainloop()