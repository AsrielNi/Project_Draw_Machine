import tkinter
import random
from inspect import signature, _empty
from typing import Any
from .TabSystem import TabPage
from .Banner import BaseBanner, IDrawMember, BaseDrawMember


########## 測試相關頁面
class TestPage(TabPage):
    def layout(self):
        self._test_label = tkinter.Label(self._top_window, text=self._page_name)
        self._test_label.pack(anchor="center")


########## 抽獎池相關頁面
class DrawPage(TabPage):
    def __init__(self, page_name, attach_manager = None, dm_type: type[IDrawMember] = BaseDrawMember):
        TabPage.__init__(self, page_name, attach_manager)
        self._banner = BaseBanner[dm_type](page_name)
        self._column_configs = (
            {"index": 0, "weight": 3},
            {"index": 1, "weight": 2}
        )
        self._shared_cnf = {"relief": "solid", "borderwidth": 1, "width": 1}
    def layout(self):
        self._draw_member_lframe = tkinter.LabelFrame(self._top_window, text="抽獎池內容")
        self._draw_member_lframe.place(relx=0, rely=0, relwidth=0.25, relheight=1)
    
        self._column_frame = tkinter.Frame(self._draw_member_lframe)
        self._column_frame.place(relx=0, rely=0, relwidth=1, relheight=0.05)
        self._column_frame.columnconfigure(index=0, weight=3)
        self._column_frame.columnconfigure(index=1)
        for col_config in self._column_configs:
            self._column_frame.columnconfigure(**col_config)
        self._column_dict: dict[str, tkinter.Label] = dict()
        for idx, ex_opts in enumerate(self._banner.draw_member_type._expose_opts()):
            col_label = tkinter.Label(self._column_frame, text=ex_opts, **self._shared_cnf)
            col_label.grid(row=0, column=idx, sticky="news")
            self._column_dict[ex_opts] = col_label
        
        self._draw_content_frame = tkinter.Frame(self._draw_member_lframe)
        self._draw_content_frame.place(relx=0, rely=0.05, relwidth=1, relheight=0.95)

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
    def open_add_draw_member_page(self, banner: BaseBanner[BaseDrawMember]):
        self.add_button.config(state="disabled")
        add_page = AddDrawMemeberPage(self, banner)
        add_page.render()
    def open_remove_draw_member_page(self, banner: BaseBanner[BaseDrawMember]):
        self.remove_button.config(state="disabled")
        add_page = RemoveDrawMemeberPage(self, banner)
        add_page.render()
    def refresh_draw_container(self):
        for widget in self._draw_content_frame.winfo_children():
            widget.destroy()
        for dm in self._banner.draw_members.values():
            dm_frame = tkinter.Frame(self._draw_content_frame)
            dm_frame.pack(fill="x")
            for col_config in self._column_configs:
                dm_frame.columnconfigure(**col_config)
            for idx, dm_key in enumerate(dm._expose_opts()):
                value_label = tkinter.Label(dm_frame, text=dm.member_info[dm_key], **self._shared_cnf)
                value_label.grid(row=0, column=idx, sticky="news")
    def draw(self, banner: BaseBanner[BaseDrawMember]):
        draw_name_list = list()
        draw_proportion_list = list()
        for draw_m in banner.draw_members.values():
            draw_name_list.append(draw_m.name)
            draw_proportion_list.append(draw_m.proportion)
        result = random.choices(draw_name_list, weights=draw_proportion_list)
        self.result_label["text"] = result


class AddDrawMemeberPage:
    def __init__(self, parent_page: DrawPage, banner: BaseBanner[IDrawMember]):
        self._parent_page = parent_page
        self._banner = banner
        self._dm_sig = signature(self._banner.draw_member_type)
        self._draw_member_opts: dict[str, tkinter.StringVar] = dict()
        self._interact_window = tkinter.Toplevel()
        self._interact_window.geometry("200x200+100+100")
        self._interact_window.protocol("WM_DELETE_WINDOW", self.__on_closing)
        self._shared_cnf = {"relief": "solid", "borderwidth": 1, "width": 1}
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
            opt_frame = tkinter.Frame(self._draw_member_opts_frame)
            opt_frame.pack(side="top", fill="both")
            opt_frame.columnconfigure(index=0, weight=2)
            opt_frame.columnconfigure(index=1, weight=3)
            dm_opt_label = tkinter.Label(opt_frame, text=dm_opt, **self._shared_cnf)
            dm_opt_label.grid(row=0, column=0, sticky="news")
            dm_opt_sv = tkinter.StringVar()
            dm_opt_entry = tkinter.Entry(opt_frame, textvariable=dm_opt_sv, **self._shared_cnf)
            dm_opt_entry.grid(row=0, column=1, sticky="news")
            self._draw_member_opts[dm_opt] = dm_opt_sv
        self._button_frame = tkinter.Frame(self._interact_window)
        self._button_frame.pack(fill="x", pady=10)
        self._confirm_but = tkinter.Button(self._button_frame, text="確認", command=self.__confirm_member)
        self._confirm_but.pack(side="left")
        self._cancel_but = tkinter.Button(self._button_frame, text="取消", command=self.__cancel)
        self._cancel_but.pack(side="left")
    def render(self):
        self.layout()


class RemoveDrawMemeberPage:
    def __init__(self, parent_page: DrawPage, banner: BaseBanner[BaseDrawMember]):
        self._parent_page = parent_page
        self._interact_window = tkinter.Toplevel()
        self._interact_window.geometry("200x200+100+100")
        self._interact_window.protocol("WM_DELETE_WINDOW", self.__on_closing)
        self._banner = banner
        self._shared_cnf = {"relief": "solid", "borderwidth": 1, "width": 1}
    def __on_closing(self):
        self._parent_page.remove_button.config(state="normal")
        self._interact_window.destroy()
    def __confirm_member(self):
        target_draw_member_name = self._sv.get()
        if self._banner.draw_members.get(target_draw_member_name) != None:
            del self._banner.draw_members[target_draw_member_name]
            self._parent_page.refresh_draw_container()
    def __cancel(self):
        self.__on_closing()
    def layout(self):
        self._opt_frame = tkinter.Frame(self._interact_window)
        self._opt_frame.pack(fill="x")
        self._opt_frame.columnconfigure(index=0, weight=2)
        self._opt_frame.columnconfigure(index=1, weight=3)
        self._name_label = tkinter.Label(self._opt_frame, text="名稱", **self._shared_cnf)
        self._name_label.grid(row=0, column=0, sticky="news")
        self._sv = tkinter.StringVar()
        self._entry = tkinter.Entry(self._opt_frame, textvariable=self._sv, **self._shared_cnf)
        self._entry.grid(row=0, column=1, sticky="news")
        self._button_frame = tkinter.Frame(self._interact_window)
        self._button_frame.pack(fill="x", pady=10)
        self._confirm_but = tkinter.Button(self._button_frame, text="確認", command=self.__confirm_member)
        self._confirm_but.pack(side="left")
        self._cancel_but = tkinter.Button(self._button_frame, text="取消", command=self.__cancel)
        self._cancel_but.pack(side="left")
    def render(self):
        self.layout()
