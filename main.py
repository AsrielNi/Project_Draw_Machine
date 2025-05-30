from __future__ import annotations
import tkinter
import random

class Banner:
    def __init__(self, banner_name: str):
        self._banner_name = banner_name
        self.__draw_member_dict: dict[str, str] = dict()
    def add_draw_member(self, name: str):
        if self.__draw_member_dict.get(name) != None:
            raise KeyError("該名稱已經登記了")
        else:
            self.__draw_member_dict[name] = name
    def remove_draw_member(self, name: str):
        if self.__draw_member_dict.get(name) == None:
            raise KeyError("該名稱並未存在")
        else:
            del self.__draw_member_dict[name]
    @property
    def draw_member_dict(self):
        return self.__draw_member_dict


class AddDrawMemeberPage:
    def __init__(self, parent_page: DrawPage, banner: Banner):
        self._parent_page = parent_page
        self._interact_window = tkinter.Toplevel()
        self._interact_window.geometry("200x200+100+100")
        self._interact_window.protocol("WM_DELETE_WINDOW", self.__on_closing)
        self._banner = banner
    def __on_closing(self):
        self._parent_page.add_button.config(state="normal")
        self._interact_window.destroy()
    def __confirm_member(self):
        new_draw_member_name = self._sv.get()
        if new_draw_member_name != "":
            self._banner.add_draw_member(new_draw_member_name)
            self._parent_page.refresh_draw_container()
    def __cancel(self):
        self.__on_closing()
    def layout(self):
        self._name_label = tkinter.Label(self._interact_window, text="名稱")
        self._name_label.pack()
        self._sv = tkinter.StringVar()
        self._entry = tkinter.Entry(self._interact_window, textvariable=self._sv)
        self._entry.pack()
        self._confirm_but = tkinter.Button(self._interact_window, text="確認", command=self.__confirm_member)
        self._confirm_but.pack()
        self._cancel_but = tkinter.Button(self._interact_window, text="取消", command=self.__cancel)
        self._cancel_but.pack()
    def render(self):
        self.layout()


class RemoveDrawMemeberPage:
    def __init__(self, parent_page: DrawPage, banner: Banner):
        self._parent_page = parent_page
        self._interact_window = tkinter.Toplevel()
        self._interact_window.geometry("200x200+100+100")
        self._interact_window.protocol("WM_DELETE_WINDOW", self.__on_closing)
        self._banner = banner
    def __on_closing(self):
        self._parent_page.add_button.config(state="normal")
        self._interact_window.destroy()
    def __confirm_member(self):
        target_draw_member_name = self._sv.get()
        if self._banner.draw_member_dict.get(target_draw_member_name) != None:
            del self._banner.draw_member_dict[target_draw_member_name]
            self._parent_page.refresh_draw_container()
    def __cancel(self):
        self.__on_closing()
    def layout(self):
        self._name_label = tkinter.Label(self._interact_window, text="名稱")
        self._name_label.pack()
        self._sv = tkinter.StringVar()
        self._entry = tkinter.Entry(self._interact_window, textvariable=self._sv)
        self._entry.pack()
        self._confirm_but = tkinter.Button(self._interact_window, text="確認", command=self.__confirm_member)
        self._confirm_but.pack()
        self._cancel_but = tkinter.Button(self._interact_window, text="取消", command=self.__cancel)
        self._cancel_but.pack()
    def render(self):
        self.layout()


class DrawPage:
    def __init__(self):
        self._top_window = tkinter.Tk()
        self._top_window.geometry("600x400+50+50")
        self._banner = Banner("Test")
    def layout(self):
        self.proportion_frame = tkinter.Frame(self._top_window, relief="ridge", borderwidth=3)
        self.proportion_frame.place(relx=0, rely=0, relwidth=0.25, relheight=1)

        self.draw_frame = tkinter.Frame(self._top_window)
        self.draw_frame.place(relx=0.25, rely=0, relwidth=0.75, relheight=1)
        self.draw_frame.rowconfigure(index=0, weight=4)
        self.draw_frame.rowconfigure(index=(1, 2), weight=1)
        self.draw_frame.columnconfigure(index=(0, 1), weight=1)

        self.result_labelframe = tkinter.LabelFrame(self.draw_frame, text="抽獎結果")
        self.result_labelframe.grid(row=0, column=0, columnspan=2, sticky="news")

        self.result_label = tkinter.Label(self.result_labelframe, text="未抽獎", font=("Arial", 18, "bold"))
        self.result_label.pack()

        self.draw_button = tkinter.Button(
            self.draw_frame,
            text="抽獎",
            font=("Arial", 18, "bold"),
            command=lambda: self.draw(self._banner)
        )
        self.draw_button.grid(row=1, column=0, columnspan=2, sticky="news")

        self.add_button = tkinter.Button(
            self.draw_frame,
            text="加入抽選項目",
            font=("Arial", 18, "bold"),
            command=lambda: self.open_add_draw_member_page(self._banner)
        )
        self.add_button.grid(row=2, column=0, sticky="news")

        self.remove_button = tkinter.Button(
            self.draw_frame,
            text="移除抽選項目",
            font=("Arial", 18, "bold"),
            command=lambda: self.open_remove_draw_member_page(self._banner)
        )
        self.remove_button.grid(row=2, column=1, sticky="news")
    def render(self):
        self.layout()
        self.refresh_draw_container()
    def start(self):
        self._top_window.mainloop()
    ######## 行為 ########
    def open_add_draw_member_page(self, banner: Banner):
        self.add_button.config(state="disabled")
        add_page = AddDrawMemeberPage(self, banner)
        add_page.render()
    def open_remove_draw_member_page(self, banner: Banner):
        self.add_button.config(state="disabled")
        add_page = RemoveDrawMemeberPage(self, banner)
        add_page.render()
    def refresh_draw_container(self):
        for widget in self.proportion_frame.winfo_children():
            widget.destroy()
        for draw_member_name in self._banner.draw_member_dict.keys():
            new_lebel = tkinter.Label(self.proportion_frame, text=draw_member_name)
            new_lebel.pack()
    def draw(self, banner: Banner):
        population = [draw_m for draw_m in banner.draw_member_dict.keys()]
        result_member = random.choice(population)
        self.result_label["text"] = result_member



def main():
    dp = DrawPage()
    dp.render()
    dp.start()


if __name__ == "__main__":
    main()
