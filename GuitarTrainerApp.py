# -*- coding: utf-8 -*-
import datetime
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image, ImageTk
from tkinter import simpledialog
import os
import shutil
import pickle

class GuitarTrainerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Guitar Trainer")  #设置窗口标题
        self.master.geometry("800x600")      #设置窗口尺寸
        self.song_list = self.load_songs()   #读取歌曲清单
        self.selected_song = ""              #目前选中的歌曲
        self.song_tab = {}                   #每首歌的曲谱文件地址
        self.load_tabs()                     #读取每首歌的曲谱文件地址
        self.img_url = "./pic/default.png"      #当前显示的img图片地址

        # 添加全屏显示和退出全屏的功能
        # self.master.attributes('-fullscreen', True)
        
        # 添加一个按钮，用于退出全屏
        button_exit_fullscreen = tk.Button(self.master, text="退出全屏", command=self.exit_fullscreen)
        button_exit_fullscreen.pack()

        #添加按钮，用于添加歌曲
        self.add_tab_button = tk.Button(self.master, text="添加曲谱", command=self.add_tab)
        self.add_tab_button.pack(side="bottom", padx=10, pady=10, expand=True)
        self.add_tab_button.config(state='disabled')

        #添加一个按钮，放在add_tab_button的右侧，用于删除图片
        self.delete_tab_button = tk.Button(self.master, text="删除曲谱", command=self.del_tab)
        self.delete_tab_button.place(relx=1.0, rely=1.0, anchor="se", x=-850, y=-10)
        self.delete_tab_button.config(state='disabled')

        #添加一个按钮，用于显示下一张图片
        self.next_tab_button = tk.Button(self.master, text="下一张", command=self.next_tab)
        self.next_tab_button.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        self.next_tab_button.config(state='active')

        #添加一个按钮，用于显示上一张图片
        self.prev_tab_button = tk.Button(self.master, text="上一张", command=self.prev_tab)
        self.prev_tab_button.place(relx=1.0, rely=1.0, anchor="se", x=-100, y=-10)
        self.prev_tab_button.config(state='active')

        #添加一个文本框，显示当前为第几页（当前页/总页数）
        self.page_text = tk.StringVar()
        self.page_label = tk.Label(self.master, textvariable=self.page_text)
        self.page_label.place(relx=1.0, rely=1.0, anchor="se", x=-720, y=-10)

        # 创建一个包含两个Frame的Frame
        self.frame = tk.Frame(self.master)
        self.frame.pack(fill="both", expand=True)

        # 创建左侧song_Frame
        self.song_frame = tk.Frame(self.frame)
        self.song_frame.pack(side="left", fill="both")
        
        # 创建左侧歌曲名的Label和Listbox
        self.song_label = tk.Label(self.song_frame, text="吉他谱名", font=("宋体", 20), width=10)
        self.song_label.pack(side="top", padx=10, pady=10)
        
        self.song_listbox = tk.Listbox(self.song_frame, height=40, width=60)
        self.song_listbox.pack(side="left", fill="both")
        self.song_listbox.pack_propagate(False)
        
        #在song_listbox内右击出现菜单
        self.menu = tk.Menu(self.song_listbox, tearoff=0)
        self.menu.add_command(label="添加新歌曲", command=self.add_new_song)
        
        #针对歌曲右击出现的菜单
        self.song_listbox_menu = tk.Menu(self.song_listbox, tearoff=0)
        self.song_listbox_menu.add_command(label="重命名", command=self.edit_song_name)
        self.song_listbox_menu.add_command(label="删除歌曲", command=self.delete_song)
        self.song_listbox_menu.add_command(label="更改位置", command=self.change_pos)
        self.song_listbox_menu.add_command(label="当前位置", command=self.current_pos)

        # 添加现存歌曲
        for song_name in self.song_list:
            self.song_listbox.insert(tk.END, song_name)

        # 创建右侧图片Frame
        self.tab_frame = tk.Frame(self.frame)
        self.tab_frame.pack(side="right", fill="both", expand=True)

        # 创建右侧Label和Listbox
        self.tab_label = tk.Label(self.tab_frame, text="吉他谱", font=("宋体", 20))
        self.tab_label.pack(side="top", padx=10, pady=10)

        self.image_label = tk.Label(self.tab_frame)
        self.image_label.pack(side="left", fill="both", expand=True)

        # 改变窗口尺寸时，同时改变照片大小
        self.image_label.bind("<Configure>", self.resize_image)
        # 右键listbox的内容，触发事件
        self.song_listbox.bind("<Button-3>", self.show_menu)
        # 左键listbox内空白处，取消选中
        self.song_listbox.bind("<Button-1>", self.clear_selection)
        #监听是否选中listbox内容
        self.song_listbox.bind("<<ListboxSelect>>", self.on_select)
    
    def exit_fullscreen(self):       #退出全屏
        self.master.attributes('-fullscreen', False)

    def resize_image(self, event):   #改变图像大小
        img_url = self.img_url
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
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # 更新图片
        self.image = ImageTk.PhotoImage(img)
        self.image_label.config(image=self.image)        

    def popup_menu(self, event):     #弹出菜单
        self.menu.post(event.x_root, event.y_root)

    def add_new_song(self):          #添加新歌曲
        new_song_name = simpledialog.askstring("添加新歌曲", "                输入新歌曲的名称：                ")
        if new_song_name:
            if new_song_name not in self.song_list:
                self.song_list.append(new_song_name)
                self.song_listbox.insert(tk.END, new_song_name)
                self.save_songs()
            else:
                tk.messagebox.showwarning("歌曲重复", "这个歌曲已经存在了.")

    def load_songs(self):            #从文件中加载所有歌曲名称
        song_list = []
        if os.path.exists('./config/song_list.txt'):
            with open('./config/song_list.txt', "r") as f:
                song_list = f.read().splitlines()
        return song_list
    
    def save_songs(self):            #将所有歌曲名称保存到文件中
        with open("./config/song_list.txt", "w") as f:
            try:
                f.write("\n".join(self.song_list))
            except Exception as e:
                messagebox.showwarning('输入有误')

    def edit_song_name(self):        #重命名操作
        # 获取选中的歌曲名称和索引
        selection_index = self.song_listbox.curselection()[0]
        old_song_name = self.song_listbox.get(selection_index)

        # 显示修改歌曲名称的对话框
        new_song_name = simpledialog.askstring("重命名歌名", "                输入新的歌曲名:                ",  
                                                  initialvalue=old_song_name, )

        # 如果用户输入了新名称
        if new_song_name:
            # 判断新名称是否与已有的名称重复
            if new_song_name in self.song_listbox.get(0, tk.END):
                tk.messagebox.showwarning("警告", "这首歌曲已经存在了.")
            else:
                # 修改列表框中的歌曲名称
                self.song_listbox.delete(selection_index)
                self.song_listbox.insert(selection_index, new_song_name)

                #将self.song_list按照self.song_listbox的顺序重写
                self.song_list = self.song_listbox.get(0, tk.END)
                self.save_songs()

                # 将self.song_tab中key的值改变
                if old_song_name in self.song_tab:
                    self.song_tab[new_song_name] = self.song_tab.pop(old_song_name)
                    tab = self.song_tab[new_song_name]
                    for i, t in enumerate(tab):
                        tab[i] = t.replace(old_song_name, new_song_name)
                    self.song_tab[new_song_name] = tab
                    self.save_tabs()

                # 将存放歌曲曲谱的文件夹名称改变
                if old_song_name in self.song_tab:
                    old_path = os.path.join('./pic', old_song_name)
                    new_path = os.path.join('./pic', new_song_name)
                    os.rename(old_path, new_path)             
                
                #提示修改成功
                messagebox.showinfo("修改成功", "修改成功！")

    def delete_song(self):           #删除歌曲操作(已优化)
        # 获取选中的歌曲名
        selection_index = self.song_listbox.curselection()[0]
        old_song_name = self.song_listbox.get(selection_index)

        # 弹出确认对话框
        confirm = tk.messagebox.askyesno("删除歌曲", f"确定要删除{old_song_name}吗？")
        if not confirm:
            return
        
        # 从列表、字典中删除选中的歌曲
        self.song_listbox.delete(selection_index)
        self.song_list.remove(old_song_name)
        self.song_tab.pop(old_song_name, None)

        # 保存更新后的列表和字典
        self.save_songs()
        self.save_tabs()

        #删除保存照片的文件夹
        if os.path.exists(f"./pic/{old_song_name}"):
            shutil.rmtree(f"./pic/{old_song_name}")
        
        # 显示删除成功消息和默认图片
        tk.messagebox.showinfo("删除歌曲", f"删除{old_song_name}成功")
        self.img_url = './pic/default.png'
        self.load_image(self.img_url)
        
    def show_menu(self, event):      #判断出现哪种菜单
        if self.song_listbox.curselection():
            self.song_listbox_menu.post(event.x_root, event.y_root)
        else:
            self.menu.post(event.x_root, event.y_root)

    def clear_selection(self, event):#取消选中
        self.song_listbox.select_clear(0, tk.END)
        self.selected_song = ""
        self.add_tab_button.config(state='disabled')
        self.delete_tab_button.config(state='disabled')

    def add_tab(self):               #增加吉他谱
        # 获取当前时间，作为文件名的一部分
        now = datetime.datetime.now()
        current_time = now.strftime("%Y-%m-%d_%H-%M-%S")
        current_time = ''.join([char for char in current_time if char.isnumeric()])

        # 获取选中的歌曲名和吉他谱路径
        selected_song = self.selected_song
        if not selected_song:
            messagebox.showerror("错误", "请先选择曲目")
            return
        
        tab_path = filedialog.askopenfilename(title="选择照片", filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.gif")])
        if not tab_path:
            return

        # 创建一个文件夹，用于存放对应的吉他谱
        target_dir = os.path.join("./pic", selected_song)
        if not os.path.exists(target_dir):
            os.mkdir(target_dir)

        target_file = os.path.join(target_dir, f"{current_time}.jpg")
        shutil.copy2(tab_path, target_file)

        # 更新歌曲对应的吉他谱列表
        if selected_song not in self.song_tab:
            self.song_tab[selected_song] = []
        self.song_tab[selected_song].append(target_file)
        self.save_tabs()
        
        # 显示保存成功消息和缩略图
        messagebox.showinfo("保存成功", "图像已保存.")
        self.img_url = self.song_tab[selected_song][0]
        self.load_image(self.img_url)

        total_pages = len(self.song_tab[self.selected_song])
        self.page_text.set(f"1/{total_pages}")

    def load_image(self, filename):  #更改显示的图片
        # 获取Label的大小
        label_width = self.image_label.winfo_width()
        label_height = self.image_label.winfo_height()
    
        img = Image.open(filename)
            
        # 计算缩放比例
        img_width, img_height = img.size
        width_ratio = label_width / img_width
        height_ratio = label_height / img_height
        ratio = min(width_ratio, height_ratio)

        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        photo = ImageTk.PhotoImage(img)
        self.image_label.config(image=photo)
        self.image_label.image = photo  

    def on_select(self, event):      #判断当前选中的歌曲名
        # 获取选中的歌曲名称
        selected_index = self.song_listbox.curselection()
        if self.song_listbox.curselection():
            self.selected_song = self.song_listbox.get(selected_index)
            # 设置“添加曲谱”按钮为可点击状态
            self.add_tab_button.config(state=tk.NORMAL)
            # 设置“删除曲谱”按钮为可点击状态
            self.delete_tab_button.config(state=tk.NORMAL)

        if self.selected_song in self.song_tab:
            self.img_url = self.song_tab[self.selected_song][0]
            total_pages = len(self.song_tab[self.selected_song])
            self.page_text.set(f"1/{total_pages}")
            self.load_image(filename=self.img_url)

        else:
            self.img_url = './pic/default.png'
            self.load_image(filename=self.img_url)

        if self.selected_song not in self.song_tab:
            self.delete_tab_button.config(state=tk.DISABLED)
            
    def save_tabs(self):             #保存乐谱信息
        with open('./config/song_dict.pkl', 'wb') as f:
            pickle.dump(self.song_tab, f)
    
    def load_tabs(self):             #读取乐谱信息
        if os.path.exists('./config/song_dict.pkl'):
            with open('./config/song_dict.pkl', 'rb') as f:
                self.song_tab = pickle.load(f)
        
    def del_tab(self):               #删除当前的图片
        #弹窗，确认是否删除
        print(self.img_url)
        if not messagebox.askyesno("删除", "确定要删除当前图片吗？"):
            return

        try:
            tab = self.song_tab[self.selected_song]
        except KeyError:
            messagebox.showerror("错误", "当前无曲谱")
            return
        
        # 删除当前选中的self.img_url这张吉他谱
        if self.img_url in self.song_tab[self.selected_song]:
            self.song_tab[self.selected_song].remove(self.img_url)
       
       #删除文件夹中的这张图片
        if os.path.exists(self.img_url):
            os.remove(self.img_url)

        #若只有这一张曲谱，则显示默认图片
        if len(self.song_tab[self.selected_song]) == 0:
            self.song_tab.pop(self.selected_song, None)
            self.img_url = './pic/default.png'
        
        #否则，显示下一张图片
        else:
            self.img_url = tab[0]
         
        self.load_image(filename=self.img_url)

        #保存更新后的字典
        self.save_tabs()

        #提示删除成功
        messagebox.showinfo("删除成功", "图像已删除.")

        total_pages = len(self.song_tab[self.selected_song])
        self.page_text.set(f"1/{total_pages}")

    def next_tab(self):              #显示下一张图片
        if self.selected_song not in self.song_tab:
            messagebox.showerror("错误", "当前无曲谱")
            return
        
        if self.img_url in self.song_tab[self.selected_song]:
            idx = self.song_tab[self.selected_song].index(self.img_url)
            self.img_url = self.song_tab[self.selected_song][(idx + 1) % len(self.song_tab[self.selected_song])]
            self.load_image(filename=self.img_url)
            self.page_text.set(f"{(idx + 1) % len(self.song_tab[self.selected_song]) + 1}/{len(self.song_tab[self.selected_song])}")

    def prev_tab(self):              #显示上一张图片
        if self.selected_song not in self.song_tab:
            messagebox.showerror("错误", "当前无曲谱")
            return
        
        if self.img_url in self.song_tab[self.selected_song]:
            idx = self.song_tab[self.selected_song].index(self.img_url)
            self.img_url = self.song_tab[self.selected_song][(idx - 1) % len(self.song_tab[self.selected_song])]
            self.load_image(filename=self.img_url)
            self.page_text.set(f"{(idx - 1) % len(self.song_tab[self.selected_song]) + 1}/{len(self.song_tab[self.selected_song])}")
    
    def change_pos(self):            #改变歌曲在listbox中的位置
        #弹出对话框，获取改变的位置
        pos1 = simpledialog.askstring("改变位置", "请输入位置(从1开始):")
        if pos1 is not None and pos1.isdigit():
            pos1 = int(pos1)
        else:
            messagebox.showerror("错误", "数据错误")
            return
        
        if pos1 < 1 or pos1 > len(self.song_list):
            messagebox.showerror("错误", "位置超出范围")
            return

        pos2 = self.song_listbox.curselection()
        song = self.song_listbox.get(pos2)
        self.song_listbox.delete(pos2)
        self.song_listbox.insert(pos1 - 1, song)

        #将self.song_list按照self.song_listbox的顺序重写
        self.song_list = self.song_listbox.get(0, tk.END)
        self.save_songs()

        # 提示改变成功
        messagebox.showinfo("改变成功", "位置已改变.")

    def current_pos(self):           #显示当前歌曲在listbox中的位置
        pos = self.song_listbox.curselection()[0] + 1
        #弹窗，告知用户当前位置
        messagebox.showinfo("当前位置", f"当前位置为{pos}")