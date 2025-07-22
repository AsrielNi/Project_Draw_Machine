from __future__ import annotations
from abc import ABC, abstractmethod
import tkinter
import tkinter.filedialog
import tkinter.ttk
from typing import Any
from .Lib import load_json_file, save_json_file

class ITabPage(ABC):
    @abstractmethod
    def __init__(self, page_name: str, attach_manager: TabPageManager | None = None) -> None:
        raise NotImplementedError()
    @abstractmethod
    def layout(self) -> None:
        raise NotImplementedError()
    @abstractmethod
    def _decide_master(self) -> tkinter.Toplevel | tkinter.Frame:
        raise NotImplementedError()
    @abstractmethod
    def _show(self) -> None:
        raise NotImplementedError()
    @abstractmethod
    def _hide(self) -> None:
        raise NotImplementedError()
    @property
    @abstractmethod
    def page_name(self) -> str:
        raise NotImplementedError()
    @property
    @abstractmethod
    def top_window(self) -> tkinter.Tk | tkinter.Frame:
        raise NotImplementedError()


class TabPage(ITabPage):
    def __init__(self, page_name: str, attach_manager: TabPageManager | None = None) -> None:
        self._page_name: str = page_name
        self._attach_manager: TabPageManager | None = attach_manager
        self._layout_flag: bool = False
        self._top_window: tkinter.Tk | tkinter.Frame = self._decide_master()
    def _decide_master(self) -> tkinter.Tk | tkinter.Frame:
        if self._attach_manager == None:
            top_window = tkinter.Tk()
            return top_window
        else:
            top_window = tkinter.Frame(self._attach_manager.page_frame)
            return top_window
    def _show(self) -> None:
        if self._attach_manager == None:
            raise AttributeError()
        else:
            if self._layout_flag == False:
                self.layout()
                self._layout_flag = True
        self._top_window.pack(fill="both", expand=1)
    def _hide(self) -> None:
        if self._attach_manager == None:
            raise AttributeError()
        else:
            self._top_window.pack_forget()
    def run(self) -> None:
        if self._attach_manager != None:
            raise AttributeError()
        else:
            if self._layout_flag == False:
                self.layout()
                self._layout_flag = True
            self._top_window.mainloop()
    @property
    def page_name(self) -> str:
        return self._page_name
    @property
    def top_window(self) -> tkinter.Tk | tkinter.Frame:
        return self._top_window


class TabPageManager:
    def __init__(self, title_name: str = "NoName", init_window_size: str = "800x600+50+50"):
        self._title_name: str = title_name
        self._init_window_size: str = init_window_size
        self._current_page_name: str | None = None
        self._register_types: dict[str, type[ITabPage]] = dict()
        self._tab_pages: dict[str, ITabPage] = dict()
        self._tab_page_buttons: dict[str, tkinter.Button] = dict()
        self.__select_color: str = "#90FFE5"
        self.__unselect_color: str = "#C5F6EB"
        self._top_window: tkinter.Tk
        self._menubar_frame: tkinter.Frame
        self._tab_frame: tkinter.Frame
        self._page_frame: tkinter.Frame
        self._operate_mb: tkinter.Menubutton
        self._operate_menu: tkinter.Menu
    def layout(self) -> None:
        self._top_window = tkinter.Tk()
        self._top_window.title(self._title_name)
        self._top_window.geometry(self._init_window_size)
        # 主要格局
        self._menubar_frame = tkinter.Frame(self._top_window, background="#D2CACA")
        self._menubar_frame.place(relx=0, rely=0, relwidth=1, relheight=0.05)
        self._tab_frame = tkinter.LabelFrame(self._top_window, text="分頁")
        self._tab_frame.place(relx=0, rely=0.05, relwidth=0.2, relheight=0.95)
        self._page_frame = tkinter.Frame(self._top_window, relief="sunken", borderwidth=3)
        self._page_frame.place(relx=0.2, rely=0.05, relwidth=0.8, relheight=0.95)
        # 選單
        self._operate_mb = tkinter.Menubutton(self._menubar_frame, text="操作", background=self._menubar_frame["background"])
        self._operate_mb.pack(side="left")
        self._operate_menu = tkinter.Menu(self._operate_mb, tearoff=0)
        self._operate_menu.add_command(label="創建分頁", command=self.__command_create_tab_page)
        self._operate_menu.add_command(label="導入分頁", command=self.__command_import_tab_page)
        self._operate_menu.add_command(label="儲存分頁", command=self.__command_save_tab_page)
        self._operate_menu.add_command(label="刪除分頁", command=self.__command_remove_tab_page)
        self._operate_mb.config(menu=self._operate_menu)
    def register_page(self, type_of_page: type[ITabPage]) -> None:
        if issubclass(type_of_page, ITabPage) == True:
            regsiter_name = type_of_page.__name__
            if self._register_types.get(regsiter_name) != None:
                raise KeyError("該分頁類型({})已經登記於管理器了。".format(regsiter_name))
            else:
                self._register_types[regsiter_name] = type_of_page
    def wrap_command(self, func, *args, **kwargs):
        def inner_func():
            func(*args, **kwargs)
        return inner_func
    def add_tab_page(self, tab_page: ITabPage) -> None:
        if self._tab_pages.get(tab_page.page_name) != None:
            raise KeyError()
        else:
            self._tab_pages[tab_page.page_name] = tab_page
            self._auto_build_tab_buttons()
    def remove_tab_page(self, page_name: str) -> None:
        if self._tab_pages.get(page_name) == None:
            raise KeyError()
        else:
            self._tab_pages[page_name].top_window.destroy()
            del self._tab_pages[page_name]
            del self._tab_page_buttons[page_name]
            self._auto_build_tab_buttons()
    def _auto_build_tab_buttons(self) -> None:
        for widget in self._tab_frame.winfo_children():
            widget.destroy()
        for tab_page in self._tab_pages.values():
            tab_button = tkinter.Button(
                self._tab_frame,
                text=tab_page.page_name,
                command=self.wrap_command(self.__command_change_page, tab_page),
                background=self.__unselect_color,
            )
            tab_button.pack(fill="x", padx=10, ipadx=10, pady=5)
            self._tab_page_buttons[tab_page.page_name] = tab_button
    def __command_create_tab_page(self) -> None:
        new_sub_page = CreateTabPage(self, "創建分頁")
        new_sub_page.layout()
        self._operate_menu.entryconfig(index="創建分頁", state="disabled")
    def __command_import_tab_page(self) -> None:
        name_of_class = self.__class__.__name__
        json_path = tkinter.filedialog.askopenfilename(filetypes=(("JSON file","*.json"),))
        json_dict = load_json_file(json_path)
        if json_dict.get(name_of_class) != None:
            for tab_setting in json_dict[name_of_class]:
                type_of_tab_page = self.register_types[tab_setting["PageType"]]
                new_tab_page = type_of_tab_page(tab_setting["PageName"], self)
                self.add_tab_page(new_tab_page)
    def __command_save_tab_page(self) -> None:
        name_of_class = self.__class__.__name__
        save_path = tkinter.filedialog.asksaveasfilename(defaultextension=".json", filetypes=(("JSON file","*.json"),))
        save_dict: dict[str, list[dict]] = {name_of_class: []}
        for tab_page in self._tab_pages.values():
            page_opt_dict = {
                "PageName": tab_page.page_name,
                "PageType": tab_page.__class__.__name__
            }
            save_dict[name_of_class].append(page_opt_dict)
        save_json_file(save_dict, save_path)
    def __command_remove_tab_page(self) -> None:
        new_sub_page = RemoveTabPage(self, "刪除分頁")
        new_sub_page.layout()
        self._operate_menu.entryconfig(index="刪除分頁", state="disabled")
    def __command_change_page(self, tab_page: ITabPage) -> None:
        if self._current_page_name == None:
            self._tab_pages[tab_page.page_name]._show()
            self._tab_page_buttons[tab_page.page_name].config(state="disabled", background=self.__select_color)
        elif self._current_page_name != tab_page.page_name:
            if self._tab_pages.get(self._current_page_name) == None:
                pass
            else:
                self._tab_pages[self._current_page_name]._hide()
                self._tab_page_buttons[self._current_page_name].config(state="normal", background=self.__unselect_color)
            self._tab_pages[tab_page.page_name]._show()
            self._tab_page_buttons[tab_page.page_name].config(state="disabled", background=self.__select_color)
        else:
            raise AssertionError("未預期之錯誤。")
        self._current_page_name = tab_page.page_name
    def run(self) -> None:
        self.layout()
        self._top_window.mainloop()
    @property
    def register_types(self) -> dict[str, type[ITabPage]]:
        return self._register_types
    @property
    def register_names(self) -> tuple[str, ...]:
        temp_list = [type_name for type_name in self._register_types.keys()]
        return tuple(temp_list)
    @property
    def tab_page_list(self) -> list[str]:
        output_list = [tab_name for tab_name in self._tab_pages.keys()]
        return output_list
    @property
    def page_frame(self) -> tkinter.Frame:
        return self._page_frame


class CreateTabPage:
    def __init__(self, parent_manager: TabPageManager, title_name: str = "創建分頁", window_size: str = "300x200+100+100") -> None:
        self._parent_manager: TabPageManager = parent_manager
        self._interact_window: tkinter.Toplevel = tkinter.Toplevel()
        self._interact_window.title(title_name)
        self._interact_window.geometry(window_size)
        self._interact_window.protocol("WM_DELETE_WINDOW", self.__on_closing)
        self._shared_config: dict[str, Any] = {"relief": "solid", "borderwidth": 1, "width": 1}
        self._page_info_label: tkinter.Label
        self._name_opt_frame: tkinter.Frame
        self._name_opt_label: tkinter.Label
        self._name_sv: tkinter.StringVar
        self._name_entry: tkinter.Entry
        self._tab_opt_frame: tkinter.Frame
        self._tab_opt_label: tkinter.Label
        self._tab_cbbox: tkinter.ttk.Combobox
        self._button_frame: tkinter.Frame
        self._confirm_button: tkinter.Button
        self._cancel_button: tkinter.Button
    def layout(self) -> None:
        self._page_info_label = tkinter.Label(self._interact_window, text="創建分頁需要的設定值")
        self._page_info_label.pack(fill="x")

        self._name_opt_frame = tkinter.Frame(self._interact_window)
        self._name_opt_frame.pack(fill="x", pady=20)
        self._name_opt_frame.columnconfigure(index=0, weight=1)
        self._name_opt_frame.columnconfigure(index=1, weight=2)
        self._name_opt_label = tkinter.Label(self._name_opt_frame, text="分頁的名稱：", **self._shared_config)
        self._name_opt_label.grid(row=0, column=0, sticky="news")
        self._name_sv = tkinter.StringVar()
        self._name_entry = tkinter.Entry(self._name_opt_frame, textvariable=self._name_sv, **self._shared_config)
        self._name_entry.grid(row=0, column=1, sticky="news")

        self._tab_opt_frame = tkinter.Frame(self._interact_window)
        self._tab_opt_frame.pack(fill="x", pady=20)
        self._tab_opt_frame.columnconfigure(index=0, weight=1)
        self._tab_opt_frame.columnconfigure(index=1, weight=2)
        self._tab_opt_label = tkinter.Label(self._tab_opt_frame, text="分頁類型：", **self._shared_config)
        self._tab_opt_label.grid(row=0, column=0, sticky="news")
        self._tab_cbbox = tkinter.ttk.Combobox(
            self._tab_opt_frame,
            values=self._parent_manager.register_names,
            state="readonly",
            width=1
        )
        self._tab_cbbox.grid(row=0, column=1, sticky="news")

        self._button_frame = tkinter.Frame(self._interact_window)
        self._button_frame.pack(fill="x", pady=20)
        self._confirm_button = tkinter.Button(self._button_frame, text="確認", command=self.__command_confirm)
        self._confirm_button.pack(side="left", padx=5, ipadx=5)
        self._cancel_button = tkinter.Button(self._button_frame, text="取消", command=self.__command_cancel)
        self._cancel_button.pack(side="left", padx=5, ipadx=5)
    def __on_closing(self) -> None:
        self._parent_manager._operate_menu.entryconfig(index="創建分頁", state="normal")
        self._interact_window.destroy()
    def __command_confirm(self) -> None:
        new_page_name = self._name_entry.get()
        if new_page_name == "":
            raise ValueError()
        new_page_type_key = self._tab_cbbox.get()
        if new_page_type_key == "":
            raise ValueError()
        new_page_type = self._parent_manager.register_types[new_page_type_key]
        new_page = new_page_type(new_page_name, self._parent_manager)
        self._parent_manager.add_tab_page(new_page)
    def __command_cancel(self) -> None:
        self.__on_closing()


class RemoveTabPage:
    def __init__(self, parent_manager: TabPageManager, title_name: str = "刪除分頁", window_size: str = "300x200+100+100") -> None:
        self._parent_manager = parent_manager
        self._interact_window = tkinter.Toplevel()
        self._interact_window.title(title_name)
        self._interact_window.geometry(window_size)
        self._interact_window.protocol("WM_DELETE_WINDOW", self.__on_closing)
        self._shared_config = {"relief": "solid", "borderwidth": 1, "width": 1}
        self._page_info_label: tkinter.Label
        self._name_opt_frame: tkinter.Frame
        self._name_opt_label: tkinter.Label
        self._name_opt_cbbox: tkinter.ttk.Combobox
        self._refresh_button: tkinter.Button
        self._button_frame: tkinter.Frame
        self._confirm_button: tkinter.Button
        self._cancel_button: tkinter.Button
    def layout(self) -> None:
        self._page_info_label = tkinter.Label(self._interact_window, text="刪除分頁需要的設定值")
        self._page_info_label.pack(fill="x")

        self._name_opt_frame = tkinter.Frame(self._interact_window)
        self._name_opt_frame.pack(fill="x", pady=20)
        self._name_opt_frame.columnconfigure(index=0, weight=1)
        self._name_opt_frame.columnconfigure(index=1, weight=2)
        self._name_opt_frame.columnconfigure(index=2, weight=1)
        self._name_opt_label = tkinter.Label(self._name_opt_frame, text="分頁的名稱：", **self._shared_config)
        self._name_opt_label.grid(row=0, column=0, sticky="news")
        self._name_opt_cbbox = tkinter.ttk.Combobox(
            self._name_opt_frame,
            values=self._parent_manager.tab_page_list,
            state="readonly",
            width=1
        )
        self._name_opt_cbbox.grid(row=0, column=1, sticky="news")
        self._refresh_button = tkinter.Button(self._name_opt_frame, text="更新", width=1, command=self._command_refresh_list)
        self._refresh_button.grid(row=0, column=2, sticky="news")

        self._button_frame = tkinter.Frame(self._interact_window)
        self._button_frame.pack(fill="x", pady=20)
        self._confirm_button = tkinter.Button(self._button_frame, text="確認", command=self.__command_confirm)
        self._confirm_button.pack(side="left", padx=5, ipadx=5)
        self._cancel_button = tkinter.Button(self._button_frame, text="取消", command=self.__command_cancel)
        self._cancel_button.pack(side="left", padx=5, ipadx=5)
    def __on_closing(self) -> None:
        self._parent_manager._operate_menu.entryconfig(index="刪除分頁", state="normal")
        self._interact_window.destroy()
    def __command_confirm(self) -> None:
        target_page_name = self._name_opt_cbbox.get()
        if target_page_name == "":
            raise ValueError()
        else:
            self._parent_manager.remove_tab_page(target_page_name)
            self._command_refresh_list()
    def __command_cancel(self) -> None:
        self.__on_closing()
    def _command_refresh_list(self) -> None:
        self._name_opt_cbbox.config(values=self._parent_manager.tab_page_list)
        self._name_opt_cbbox.set("")
