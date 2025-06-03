from __future__ import annotations
import tkinter
import random
from inspect import signature, _empty
from typing import Any
from src.Banner import BaseBanner, BaseDrawMember, IDrawMember


class AddDrawMemeberPage:
    def __init__(self, parent_page: DrawPage, banner: BaseBanner[IDrawMember]):
        self._parent_page = parent_page
        self._banner = banner
        self._dm_sig = signature(self._banner.draw_member_type)
        self._draw_member_opts: dict[str, tkinter.StringVar] = dict()
        self._interact_window = tkinter.Toplevel()
        self._interact_window.geometry("200x200+100+100")
        self._interact_window.protocol("WM_DELETE_WINDOW", self.__on_closing)
    def __on_closing(self):
        self._parent_page.add_button.config(state="normal")
        self._interact_window.destroy()
    def __confirm_member(self):
        value_pack_dict: dict[str, Any] = dict()
        for dm_opt_name, sv in self._draw_member_opts.items():
            input_value = sv.get()
            if input_value == "":
                raise ValueError("數值不能為空白。")
            if self._dm_sig.parameters.get(dm_opt_name) == None:
                raise KeyError("<Signature>物件並未記述有關此名稱({})的訊息。".format(dm_opt_name))
            else:
                expect_type = self._dm_sig.parameters[dm_opt_name].annotation
                if issubclass(expect_type, int) == True:
                    if input_value.isdigit() == False:
                        raise ValueError("使用者輸入的值無法轉換成整數。")
                    else:
                        value_pack_dict[dm_opt_name] = int(input_value)
                elif issubclass(expect_type, (str, _empty)) == True:
                    value_pack_dict[dm_opt_name] = input_value
                else:
                    raise TypeError("沒有從<str>轉換成<{}>的方法。".format(expect_type))
        new_draw_member = self._banner.draw_member_type(**value_pack_dict)
        self._banner.add_draw_member(new_draw_member)
        self.__clear_input()
        self._parent_page.refresh_draw_container()
    def __clear_input(self):
        for sv in self._draw_member_opts.values():
            sv.set("")
    def __cancel(self):
        self.__on_closing()
    def layout(self):
        self._draw_member_opts_frame = tkinter.Frame(self._interact_window)
        self._draw_member_opts_frame.pack(side="top", fill="x")
        for dm_opt in self._banner.draw_member_type._expose_opts():
            pair_frame = tkinter.Frame(self._draw_member_opts_frame)
            pair_frame.pack(side="top", fill="both")
            dm_opt_label = tkinter.Label(pair_frame, text=dm_opt)
            dm_opt_label.pack(side="left", fill="both")
            dm_opt_sv = tkinter.StringVar()
            dm_opt_entry = tkinter.Entry(pair_frame, textvariable=dm_opt_sv)
            dm_opt_entry.pack(side="left", fill="both", expand=1)
            self._draw_member_opts[dm_opt] = dm_opt_sv
        self._confirm_but = tkinter.Button(self._interact_window, text="確認", command=self.__confirm_member)
        self._confirm_but.pack()
        self._cancel_but = tkinter.Button(self._interact_window, text="取消", command=self.__cancel)
        self._cancel_but.pack()
    def render(self):
        self.layout()


class RemoveDrawMemeberPage:
    def __init__(self, parent_page: DrawPage, banner: BaseBanner[BaseDrawMember]):
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
        if self._banner.draw_members.get(target_draw_member_name) != None:
            del self._banner.draw_members[target_draw_member_name]
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
        self._banner = BaseBanner[BaseDrawMember]("Test")
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
    def open_add_draw_member_page(self, banner: BaseBanner[BaseDrawMember]):
        self.add_button.config(state="disabled")
        add_page = AddDrawMemeberPage(self, banner)
        add_page.render()
    def open_remove_draw_member_page(self, banner: BaseBanner[BaseDrawMember]):
        self.add_button.config(state="disabled")
        add_page = RemoveDrawMemeberPage(self, banner)
        add_page.render()
    def refresh_draw_container(self):
        for widget in self.proportion_frame.winfo_children():
            widget.destroy()
        for draw_member_name in self._banner.draw_members.keys():
            new_lebel = tkinter.Label(self.proportion_frame, text=draw_member_name)
            new_lebel.pack()
    def draw(self, banner: BaseBanner[BaseDrawMember]):
        population = [draw_m for draw_m in banner.draw_members.keys()]
        result_member = random.choice(population)
        self.result_label["text"] = result_member



def main():
    dp = DrawPage()
    dp.render()
    dp.start()


if __name__ == "__main__":
    main()
