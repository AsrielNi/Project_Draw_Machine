import tkinter
from inspect import signature, _empty
import tkinter.ttk
from typing import Any
from .TabSystem import TabPage
from .Banner import Banner, IDrawMember, BaseDrawMember
from .GUIunit import RowFrameFactory, RowFrame

########## 測試相關頁面
class TestPage(TabPage):
    def layout(self):
        self._show_label = tkinter.Label(self._top_window, text="這只是個測試頁面，會顯示頁面名稱，無任何功能")
        self._show_label.pack(anchor="center")
        self._test_label = tkinter.Label(self._top_window, text=self._page_name)
        self._test_label.pack(anchor="center")


########## 抽獎池相關頁面
class DrawPage(TabPage):
    _REGISTER_DMS: dict[str, type[IDrawMember]] = {
        "BaseDrawMember": BaseDrawMember
    }
    @classmethod
    def get_register_type_names(cls) -> tuple[str, ...]:
        output_list = [type_name for type_name in cls._REGISTER_DMS.keys()]
        return tuple(output_list)
    def __init__(self, page_name, attach_manager = None):
        TabPage.__init__(self, page_name, attach_manager)
        self._draw_member_frames: dict[str, RowFrame] = dict()
        self._row_frame_shared_config = {"width": 1, "relief": "solid", "borderwidth": 1}
    def layout(self):
        self._dm_frame = tkinter.Frame(self._top_window, relief="solid", borderwidth=2)
        self._dm_frame.place(relx=0, rely=0, relwidth=0.25, relheight=0.9)
        self._operate_frame = tkinter.Frame(self._top_window, relief="solid", borderwidth=2)
        self._operate_frame.place(relx=0, rely=0.9, relwidth=0.25, relheight=0.1)
        self._operate_frame.rowconfigure(index=(0, 1), weight=1)
        self._operate_frame.columnconfigure(index=(0, 1, 2, 3), weight=1)
        self._banner_frame = tkinter.Frame(self._top_window, relief="solid", borderwidth=2)
        self._banner_frame.place(relx=0.25, rely=0, relwidth=0.75, relheight=1)
        self._banner_frame.rowconfigure(index=(0, 1, 2, 3), weight=1)
        self._banner_frame.columnconfigure(index=(0, 1, 2, 3), weight=1)

        self._dm_type_label = tkinter.Label(self._operate_frame, text="類型", width=1)
        self._dm_type_label.grid(row=0, column=0, sticky="news")
        self._dm_cbbox = tkinter.ttk.Combobox(
            self._operate_frame, values=self.get_register_type_names(), width=1, height=1, state="readonly"
        )
        self._dm_cbbox.grid(row=0, column=1, columnspan=3, sticky="news")

        self._add_dm_button = tkinter.Button(
            self._operate_frame,
            text="新增",
            width=1,
            state="disabled",
            command=self._command_add_draw_member
        )
        self._add_dm_button.grid(row=1, column=0, sticky="news", padx=2, pady=2, ipadx=2, ipady=2)

        self._remove_dm_button = tkinter.Button(
            self._operate_frame,
            text="移除",
            width=1,
            state="disabled",
            command=self._command_remove_draw_member
        )
        self._remove_dm_button.grid(row=1, column=1, sticky="news", padx=2, pady=2, ipadx=2, ipady=2)

        self._lock_button = tkinter.Button(
            self._operate_frame,text="鎖定",
            width=1,
            command=self._command_lock_draw_banner_type
        )
        self._lock_button.grid(row=1, column=2, sticky="news", padx=2, pady=2, ipadx=2, ipady=2)

        self._reset_button = tkinter.Button(
            self._operate_frame,
            text="重置",
            width=1,
            state="disabled",
            command=self._command_reset_banner
        )
        self._reset_button.grid(row=1, column=3, sticky="news", padx=2, pady=2, ipadx=2, ipady=2)

        self._draw_button = tkinter.Button(
            self._banner_frame,
            text="抽獎",
            width=1,
            state="disabled",
            command=self._command_draw,
            font=("標楷體", 36, "bold")
        )
        self._draw_button.grid(row=3, column=0, columnspan=4, sticky="news")

        self._result_lframe = tkinter.LabelFrame(self._banner_frame, text="抽選結果")
        self._result_lframe.grid(row=2, column=0, columnspan=4, sticky="news")

        self._result_label = tkinter.Label(self._result_lframe, text="未抽選", width=1, font=("標楷體", 36, "bold"))
        self._result_label.pack(fill="both", expand=1)
    def _command_lock_draw_banner_type(self):
        type_name = self._dm_cbbox.get()
        if self._REGISTER_DMS.get(type_name) == None:
            raise KeyError()
        else:
            dm_type = self._REGISTER_DMS[type_name]
            self._draw_banner = Banner[dm_type](self._page_name)
            self._data_row_frame_factory = RowFrameFactory(len(dm_type._expose_opts()))
            self._title_row_frame = self._data_row_frame_factory.create_row_frame(self._dm_frame)
            for title_idx, title_name in enumerate(dm_type._expose_opts()):
                self._title_row_frame.add_content(
                    title_idx, tkinter.Label, {"text": title_name, **self._row_frame_shared_config}
                )
            self._title_row_frame.pack(fill="x", pady=5, ipady=5, padx=3, ipadx=3)
            self._dm_cbbox.config(state="disabled")
            self._lock_button.config(state="disabled")
            self._add_dm_button.config(state="normal")
            self._remove_dm_button.config(state="normal")
            self._reset_button.config(state="normal")
            self._draw_button.config(state="normal")
    def _command_add_draw_member(self):
        self._add_dm_button.config(state="disabled")
        self._add_dm_page = AddDrawMemeberPage(self)
        self._add_dm_page.layout()
    def _command_remove_draw_member(self):
        self._remove_dm_button.config(state="disabled")
        self._remove_dm_page = RemoveDrawMemeberPage(self)
        self._remove_dm_page.layout()
    def _command_reset_banner(self):
        if hasattr(self, "_add_dm_page") == True:
            self._add_dm_page._interact_window.destroy()
            del self._add_dm_page
        if hasattr(self, "_remove_dm_page") == True:
            self._remove_dm_page._interact_window.destroy()
            del self._remove_dm_page
        del self._draw_banner
        self._title_row_frame.destroy()
        for row_frame in self._draw_member_frames.values():
            row_frame.destroy()
        self._draw_member_frames: dict[str, RowFrame] = dict()
        self._dm_cbbox.config(state="readonly")
        self._lock_button.config(state="normal")
        self._add_dm_button.config(state="disabled")
        self._remove_dm_button.config(state="disabled")
        self._reset_button.config(state="disabled")
        self._draw_button.config(state="disabled")
        self._result_label["text"] = "未抽選"
    def _command_draw(self):
        result = self._draw_banner.draw()
        self._result_label["text"] = result
    def refresh_draw_container(self):
        for row_frame in self._draw_member_frames.values():
            row_frame.destroy()
        del self._draw_member_frames
        self._draw_member_frames: dict[str, RowFrame] = dict()
        for dm in self._draw_banner.draw_members.values():
            row_frame = self._data_row_frame_factory.create_row_frame(self._dm_frame)
            row_frame.pack(fill="x", padx=3, ipadx=3)
            for idx, dm_key in enumerate(dm._expose_opts()):
                row_frame.add_content(
                    idx, tkinter.Label, {"text": dm.member_info[dm_key], **self._row_frame_shared_config}
                )
            self._draw_member_frames[dm.name] = row_frame
    
    @property
    def draw_member_list(self):
        output_list = [member_name for member_name in self._draw_member_frames.keys()]
        return output_list


class AddDrawMemeberPage:
    def __init__(self, parent_page: DrawPage):
        self._parent_page = parent_page
        self._dm_sig = signature(self._parent_page._draw_banner.draw_member_type)
        self._draw_member_opts: dict[str, tkinter.StringVar] = dict()
        self._interact_window = tkinter.Toplevel()
        self._interact_window.geometry("200x200+100+100")
        self._interact_window.protocol("WM_DELETE_WINDOW", self.__on_closing)
        self._shared_cnf = {"relief": "solid", "borderwidth": 1, "width": 1}
    def __on_closing(self):
        self._parent_page._add_dm_button.config(state="normal")
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
        new_draw_member = self._parent_page._draw_banner.draw_member_type(**value_pack_dict)
        self._parent_page._draw_banner.add_draw_member(new_draw_member)
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
        for dm_opt in self._parent_page._draw_banner.draw_member_type._expose_opts():
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


class RemoveDrawMemeberPage:
    def __init__(self, parent_page: DrawPage):
        self._parent_page = parent_page
        self._interact_window = tkinter.Toplevel()
        self._interact_window.geometry("200x200+100+100")
        self._interact_window.protocol("WM_DELETE_WINDOW", self.__on_closing)
        self._shared_cnf = {"relief": "solid", "borderwidth": 1, "width": 1}
    def __on_closing(self):
        self._parent_page._remove_dm_button.config(state="normal")
        self._interact_window.destroy()
    def __confirm_member(self):
        target_draw_member_name = self._name_cbbox.get()
        if self._parent_page._draw_banner.draw_members.get(target_draw_member_name) != None:
            del self._parent_page._draw_banner.draw_members[target_draw_member_name]
            self._parent_page.refresh_draw_container()
            self._command_refresh_list()
    def __cancel(self):
        self.__on_closing()
    def layout(self):
        self._opt_frame = tkinter.Frame(self._interact_window)
        self._opt_frame.pack(fill="x")
        self._opt_frame.columnconfigure(index=0, weight=1)
        self._opt_frame.columnconfigure(index=1, weight=2)
        self._opt_frame.columnconfigure(index=2, weight=1)
        self._name_label = tkinter.Label(self._opt_frame, text="名稱", **self._shared_cnf)
        self._name_label.grid(row=0, column=0, sticky="news")
        self._name_cbbox = tkinter.ttk.Combobox(
            self._opt_frame,
            values=self._parent_page.draw_member_list,
            state="readonly",
            width=1
        )
        self._name_cbbox.grid(row=0, column=1, sticky="news")
        self._refresh_button = tkinter.Button(self._opt_frame, text="更新", width=1, command=self._command_refresh_list)
        self._refresh_button.grid(row=0, column=2, sticky="news")
        self._button_frame = tkinter.Frame(self._interact_window)
        self._button_frame.pack(fill="x", pady=10)
        self._confirm_but = tkinter.Button(self._button_frame, text="確認", command=self.__confirm_member)
        self._confirm_but.pack(side="left")
        self._cancel_but = tkinter.Button(self._button_frame, text="取消", command=self.__cancel)
        self._cancel_but.pack(side="left")
    def _command_refresh_list(self):
        self._name_cbbox.config(values=self._parent_page.draw_member_list)
        self._name_cbbox.set("")
