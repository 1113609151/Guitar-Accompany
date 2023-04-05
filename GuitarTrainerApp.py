# -*- coding: utf-8 -*-
import datetime
import time
import tkinter as tk
from tkinter import Scrollbar, messagebox
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
        self.song_time = {}                  #每首歌的训练时间[单次训练时间，总训练时间]
        self.load_time()                     #读取每首歌的总练习时间

        self.img_url = "./pic/default.png"      #当前显示的img图片地址
        self.timer_id = 0                    #计时器id

        # 添加全屏显示和退出全屏的功能
        # self.master.attributes('-fullscreen', True)
        
        # 添加一个按钮，用于退出全屏
        button_exit_fullscreen = tk.Button(self.master, text="退出全屏", command=self.exit_fullscreen)
        button_exit_fullscreen.pack()

        #添加按钮，用于添加歌曲
        self.add_tab_button = tk.Button(self.master, text="添加曲谱", command=self.add_tab)
        self.add_tab_button.pack(side="bottom", padx=0, pady=10)
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

        #添加一个文本框，显示当前训练时间
        self.time_text_1 = tk.StringVar()
        self.time_label_1 = tk.Label(self.master, textvariable=self.time_text_1)
        self.time_label_1.place(relx=1.0, rely=1.0, anchor="se", x=-590, y=-10)

        #添加一个文本框，显示总共训练时间
        self.time_text_2 = tk.StringVar()
        self.time_label_2 = tk.Label(self.master, textvariable=self.time_text_2)
        self.time_label_2.place(relx=1.0, rely=1.0, anchor="se", x=-450, y=-10)

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

        #创建Canvas用于显示图片
        self.canvas = tk.Canvas(self.tab_frame)
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # 创建垂直滚动条
        yscrollbar = Scrollbar(self.canvas, orient='vertical', command=self.canvas.yview)
        yscrollbar.pack(side='right', fill='y')

        # 创建水平滚动条
        xscrollbar = Scrollbar(self.canvas, orient='horizontal', command=self.canvas.xview)
        xscrollbar.pack(side='bottom', fill='x')

        # 将滚动条与canvas绑定
        self.canvas.configure(xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set)
        yscrollbar.config(command=self.canvas.yview)
        xscrollbar.config(command=self.canvas.xview)
        self.canvas.config(scrollregion=self.canvas.bbox('all'))

        #添加一个按钮，用于放大图片
        self.zoom_button = tk.Button(self.tab_frame, text="放大图片", command=self.zoom)
        self.zoom_button.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-20)
        self.zoom_button.config(state='disabled')

        #添加一个按钮，用于缩小图片
        self.shrink_button = tk.Button(self.tab_frame, text="恢复大小", command=self.shrink)
        self.shrink_button.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-60)
        self.shrink_button.config(state='disabled')

        # 改变窗口尺寸时，同时改变照片大小
        self.canvas.bind("<Configure>", self.resize_image)
        # 右键listbox的内容，触发事件
        self.song_listbox.bind("<Button-3>", self.show_menu)
        # 左键listbox内空白处，取消选中
        self.song_listbox.bind("<Button-1>", self.clear_selection)
        #监听是否选中listbox内容
        self.song_listbox.bind("<<ListboxSelect>>", self.on_select)
        #滑动条滚动事件
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
    
    def on_mousewheel(self, event):
        # 获取滚轮方向，Linux和Windows有些许不同
        if event.num == 5 or event.delta < 0:
            # 滚轮向下滚动
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            # 滚轮向上滚动
            self.canvas.yview_scroll(-1, "units")

    def exit_fullscreen(self):       #退出全屏
        self.master.attributes('-fullscreen', False)

    def resize_image(self, event):   #改变图像大小(已优化)
        img_url = self.img_url
        
        # 获取Label的大小
        label_width = self.canvas.winfo_width()
        label_height = self.canvas.winfo_height()

        # 加载图片并计算缩放比例
        img = Image.open(img_url)
        img_width, img_height = img.size
        ratio = min(label_width / img_width, label_height / img_height)

        # 缩放图片
        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # 更新图片
        self.image = ImageTk.PhotoImage(img)
        #self.canvas显示图片
        self.canvas.delete("all")
        self.canvas.create_image(label_width//2, label_height//2, image=self.image)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
            
    def popup_menu(self, event):     #弹出菜单
        self.menu.post(event.x_root, event.y_root)

    def add_new_song(self):          #添加新歌曲(已优化)
        new_song_name = simpledialog.askstring("添加新歌曲", "                输入新歌曲的名称：                ")
        if new_song_name:
            # 去除字符串两端的空格
            new_song_name = new_song_name.strip()
            if not new_song_name:  # 如果去除空格后是空字符串，给出提示并重新弹出对话框
                messagebox.showwarning("歌曲名称不能为空", "请输入新歌曲的名称。")
                self.add_song()  # 重新弹出对话框
            elif new_song_name in self.song_list:  # 如果歌曲名已经存在，给出提示并重新弹出对话框
                messagebox.showwarning("歌曲重复", "这个歌曲已经存在了。请换一个歌曲名称。")
                self.add_song()  # 重新弹出对话框
            else:  # 如果歌曲名不存在，则添加新歌曲并保存
                self.song_list.append(new_song_name)
                self.song_listbox.insert(tk.END, new_song_name)
                self.save_songs()

    def load_songs(self):            #加载歌曲列表(已优化)
        song_list = []
        try:
            with open('./config/song_list.txt', "r") as f:
                song_list = f.read().splitlines()
        except FileNotFoundError:
            pass # File 不存在
        except Exception as e:
            messagebox.showwarning('读取歌曲列表失败', f"错误信息: {str(e)}")
        return song_list

    def save_songs(self):            #保存歌曲名称到文件中（已优化）
        file_path = "./config/song_list.txt"
        try:
            with open(file_path, "w") as f:
                f.write("\n".join(self.song_list))
        except Exception as e:
            error_msg = f"An error occurred while writing to file {file_path}:\n{e}"
            print(error_msg)
            messagebox.showwarning('保存失败', error_msg)

    def edit_song_name(self):        #重命名操作(已优化)
        # 获取选中的歌曲名称和索引
        selected_index = self.song_listbox.curselection()
        if not selected_index:
            return
        selection_index = selected_index[0]
        old_song_name = self.song_listbox.get(selection_index)

        # 显示修改歌曲名称的对话框
        new_song_name = simpledialog.askstring(
            "重命名歌名", 
            "                输入新的歌曲名:                ",  
        initialvalue=old_song_name
        )

        # 如果用户输入了新名称
        if new_song_name:
                    # 判断新名称是否与已有的名称重复
            if new_song_name == old_song_name:
                messagebox.showwarning("警告", "新名称和原名称相同.")
                return
            if new_song_name in self.song_list:
                messagebox.showwarning("警告", "这首歌曲已经存在了.")
                return
            
            # 修改列表框中的歌曲名称
            self.song_listbox.delete(selection_index)
            self.song_listbox.insert(selection_index, new_song_name)

            # 更新self.song_list
            self.song_list = list(self.song_listbox.get(0, tk.END))
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
            old_path = os.path.join('./pic', old_song_name)
            new_path = os.path.join('./pic', new_song_name)
            if os.path.exists(old_path):
                os.rename(old_path, new_path)

            # 将self.song_time中key的值改变
            if old_song_name in self.song_time:
                self.song_time[new_song_name] = self.song_time.pop(old_song_name)
                time = self.song_time[new_song_name]
                for i, t in enumerate(time):
                    time[i] = t.replace(old_song_name, new_song_name)
                self.song_time[new_song_name] = time
                self.save_time()
            
             # 提示修改成功
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
        self.song_time.pop(old_song_name, None)

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
        self.time_text_1.set('')
        self.time_text_2.set('')
        self.page_text.set('')
        self.img_url = './pic/default.png'
        self.load_image(self.img_url)
        self.save_songs()
        self.save_tabs()
        self.save_time()
        if self.timer_id:
            self.master.after_cancel(self.timer_id)

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
        
        tab_paths = filedialog.askopenfilenames(title="选择照片", filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.gif")])
        if not tab_paths:
            return

        # 创建一个文件夹，用于存放对应的吉他谱
        target_dir = os.path.join("./pic", selected_song)
        if not os.path.exists(target_dir):
            os.mkdir(target_dir)

        # 逐个复制吉他谱文件，并更新歌曲对应的吉他谱列表
        for tab_path in tab_paths:
            target_file = os.path.join(target_dir, f"{current_time}.jpg")
            shutil.copy2(tab_path, target_file)
            if selected_song not in self.song_tab:
                self.song_tab[selected_song] = []
            self.song_tab[selected_song].append(target_file)
            current_time = str(int(current_time) + 1)  # 让文件名不重复

        self.save_tabs()
        
        # 显示保存成功消息和缩略图
        messagebox.showinfo("保存成功", "图像已保存.")
        self.img_url = self.song_tab[selected_song][0]
        self.load_image(self.img_url)

        total_pages = len(self.song_tab[self.selected_song])
        self.page_text.set(f"1/{total_pages}")

    def load_image(self, filename):  #更改显示的图片
        # 获取Label的大小
        label_width = self.canvas.winfo_width()
        label_height = self.canvas.winfo_height()
    
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
        self.canvas.delete("all")
        self.canvas.create_image(label_width // 2, label_height // 2, image=photo)
        self.canvas.image = photo

    def on_select(self, event):      #判断当前选中的歌曲名(已优化)
        # 获取选中的歌曲名称
        selected_index = self.song_listbox.curselection()
        if selected_index:
            self.selected_song = self.song_listbox.get(selected_index)
            # 设置“添加曲谱”按钮为可点击状态
            self.add_tab_button.config(state=tk.NORMAL)
            # 设置“删除曲谱”按钮为可点击状态
            self.delete_tab_button.config(state=tk.NORMAL)

        self.img_url = self.song_tab.get(self.selected_song, ['./pic/default.png'])[0]
        total_pages = len(self.song_tab.get(self.selected_song, []))
        self.page_text.set(f"1/{total_pages}")
        self.load_image(filename=self.img_url)
        
        # 设置“放大”按钮为可点击状态
        if self.img_url != './pic/default.png':
            self.zoom_button.config(state=tk.NORMAL)
            self.shrink_button.config(state=tk.NORMAL)
        else:
            self.zoom_button.config(state=tk.DISABLED)
            self.shrink_button.config(state=tk.DISABLED)

        if self.selected_song not in self.song_tab:
            self.delete_tab_button.config(state=tk.DISABLED)

        if self.selected_song not in self.song_tab:
            self.delete_tab_button.config(state=tk.DISABLED)
            
        #开始计时
        if "调弦" not in self.selected_song:
            self.start_timer()
        else:
            self.master.after_cancel(self.timer_id) if self.timer_id else None
            self.time_text_1.set("")
            self.time_text_2.set("")
            self.page_text.set("")
        
    def start_timer(self):            #开始计时
        self.temp_time = 0
        if self.timer_id:
            self.master.after_cancel(self.timer_id)
        self.update_time_text()

    def update_time_text(self):    #更新文本框中的时间(已优化)
        # 更新选中歌曲的时间
        self.update_selected_song_time()

        # 更新文本框中的时间
        self.temp_time += 1
        if self.temp_time <= 60:
            self.time_text_1.set(f"当前练习时间: {self.temp_time}s")
        else:
            self.time_text_1.set(f"当前练习时间: {self.temp_time//60}m {self.temp_time%60}s")
        total_time = self.song_time[self.selected_song]
        if total_time <= 60:
            self.time_text_2.set(f"总共练习时间: {total_time}s")
        elif total_time <= 3600:
            self.time_text_2.set(f"总共练习时间: {total_time//60}m {total_time%60}s")
        else:
            hours = total_time // 3600
            minutes = (total_time - hours * 3600) // 60
            self.time_text_2.set(f"总共练习时间: {hours}h {minutes}m")

        # 每隔1秒更新一次
        self.timer_id = self.master.after(1000, self.update_time_text)

    def update_selected_song_time(self):    #更新选中歌曲的时间
        if self.selected_song not in self.song_time:
            self.song_time[self.selected_song] = 0
        else:
            self.song_time[self.selected_song] += 1
        self.save_time()     

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

    def save_time(self):             #保存记录时间
        with open('./config/time.pkl', 'wb') as f:
            pickle.dump(self.song_time, f)

    def load_time(self):             #读取记录时间
        if os.path.exists('./config/time.pkl'):
            with open('./config/time.pkl', 'rb') as f:
                self.song_time = pickle.load(f)
    
    def zoom(self):
        img_url = self.img_url
        # 获取Label的大小
        label_width = self.canvas.winfo_width()
        label_height = self.canvas.winfo_height()
        # 获取当前图片对象
        current_image = Image.open(img_url)
        # 缩放图片
        scaled_image = current_image.resize((int(current_image.width*1.2), int(current_image.height*1.2)))
        # 将缩放后的图片转换为Tkinter支持的对象，并保存引用
        self.scaled_photo = ImageTk.PhotoImage(scaled_image)
        # 更新Label中的图片
        self.canvas.delete("all")
        self.canvas.create_image(label_width // 2, label_height // 2, image=self.scaled_photo, anchor="center")
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.image = scaled_image

    def shrink(self):                #缩小图片   
        img_url = self.img_url
        
        # 获取Label的大小
        label_width = self.canvas.winfo_width()
        label_height = self.canvas.winfo_height()

        # 加载图片并计算缩放比例
        img = Image.open(img_url)
        img_width, img_height = img.size
        ratio = min(label_width / img_width, label_height / img_height)

        # 缩放图片
        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # 更新图片
        self.image = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(label_width // 2, label_height // 2, image=self.image)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.image = self.image