from __future__ import annotations
from abc import ABC, abstractmethod
import tkinter
import time
from .Lib import wrap_func_to_thread, wrap_func
from .Form import FormPage, FillInBlankQuestionWidget, ComboBoxQuestionWidget, DefaultQuestionLayout


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
            top_window = tkinter.Frame(self._attach_manager.layout.page_content_frame)
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


class ITabPageManagerLayout(ABC):
    @abstractmethod
    def __init__(self, master) -> None:
        raise NotImplementedError()
    @abstractmethod
    def create_widget(self) -> None:
        raise NotImplementedError()
    @abstractmethod
    def deploy_widget(self) -> None:
        raise NotImplementedError()
    @property
    @abstractmethod
    def menubar_frame(self) -> tkinter.Frame:
        raise NotImplementedError()
    @property
    @abstractmethod
    def pages_frame(self) -> tkinter.Frame:
        raise NotImplementedError()
    @property
    @abstractmethod
    def page_content_frame(self) -> tkinter.Frame:
        raise NotImplementedError()
    @property
    @abstractmethod
    def operate_mb(self) -> tkinter.Menubutton:
        raise NotImplementedError()
    @property
    @abstractmethod
    def operate_menu(self) -> tkinter.Menu:
        raise NotImplementedError()
    @property
    @abstractmethod
    def select_page_button_color(self) -> str:
        raise NotImplementedError()
    @property
    @abstractmethod
    def unselect_page_button_color(self) -> str:
        raise NotImplementedError()


class DefaultLayoutTPM(ITabPageManagerLayout):
    def __init__(self, master):
        self.__master = master
        self._menubar_frame: tkinter.Frame
        self._pages_frame: tkinter.Frame
        self._page_content_frame: tkinter.Frame
        self._operate_mb: tkinter.Menubutton
        self._operate_menu: tkinter.Menu
    def create_widget(self):
        self._menubar_frame = tkinter.Frame(self.__master, background="#D2CACA")
        self._pages_frame = tkinter.Frame(self.__master)
        self._page_content_frame = tkinter.Frame(self.__master, relief="sunken", borderwidth=3)
        self._operate_mb = tkinter.Menubutton(self._menubar_frame, text="操作", background=self._menubar_frame["background"])
        self._operate_menu = tkinter.Menu(self._operate_mb, tearoff=0)
        self._operate_mb.config(menu=self._operate_menu)
    def deploy_widget(self):
        self._menubar_frame.place(relx=0, rely=0, relwidth=1, relheight=0.05)
        self._pages_frame.place(relx=0, rely=0.05, relwidth=0.25, relheight=0.95)
        self._page_content_frame.place(relx=0.25, rely=0.05, relwidth=0.75, relheight=0.95)
        self._operate_mb.pack(side="left", fill="y")
    @property
    def menubar_frame(self) -> tkinter.Frame:
        return self._menubar_frame
    @property
    def pages_frame(self) -> tkinter.Frame:
        return self._pages_frame
    @property
    def page_content_frame(self) -> tkinter.Frame:
        return self._page_content_frame
    @property
    def operate_mb(self) -> tkinter.Menubutton:
        return self._operate_mb
    @property
    def operate_menu(self) -> tkinter.Menu:
        return self._operate_menu
    @property
    def select_page_button_color(self) -> str:
        return "#90FFE5"
    @property
    def unselect_page_button_color(self) -> str:
        return "#C5F6EB"


class TabPageManager:
    def __init__(self, type_of_layout: type[ITabPageManagerLayout]) -> None:
        self._register_types: dict[str, type[ITabPage]] = dict()
        self._tab_pages: dict[str, ITabPage] = dict()
        self._tab_page_buttons: dict[str, tkinter.Button] = dict()
        self._current_page_name: str | None = None
        self.__main_window: tkinter.Tk = tkinter.Tk()
        self.__type_of_layout: type[ITabPageManagerLayout] = type_of_layout
        self.__layout: ITabPageManagerLayout
    def refresh_pages_frame(self) -> None:
        for widget in self.__layout.pages_frame.winfo_children():
            widget.destroy()
        for tab_page in self._tab_pages.values():
            tab_button = tkinter.Button(
                self.__layout.pages_frame,
                text=tab_page.page_name,
                command=wrap_func(self.button_command_change_page, tab_page),
                background=self.__layout.unselect_page_button_color,
            )
            tab_button.pack(fill="x", padx=10, ipadx=10, pady=5)
            self._tab_page_buttons[tab_page.page_name] = tab_button
    def register_page(self, type_of_page: type[ITabPage]) -> None:
        if issubclass(type_of_page, ITabPage) == True:
            regsiter_name = type_of_page.__name__
            if self._register_types.get(regsiter_name) != None:
                raise KeyError("該分頁類型({})已經登記於管理器了。".format(regsiter_name))
            else:
                self._register_types[regsiter_name] = type_of_page
    def add_tab_page(self, tab_page: ITabPage) -> None:
        if self._tab_pages.get(tab_page.page_name) != None:
            raise KeyError()
        else:
            self._tab_pages[tab_page.page_name] = tab_page
    def remove_tab_page(self, page_name: str) -> None:
        if self._tab_pages.get(page_name) == None:
            raise KeyError()
        else:
            self._tab_pages[page_name].top_window.destroy()
            del self._tab_pages[page_name]
            del self._tab_page_buttons[page_name]
    def button_command_change_page(self, tab_page: ITabPage) -> None:
        if self._current_page_name == None:
            self._tab_pages[tab_page.page_name]._show()
            self._tab_page_buttons[tab_page.page_name].config(
                state="disabled",
                background=self.__layout.select_page_button_color
            )
        elif self._current_page_name != tab_page.page_name:
            if self._tab_pages.get(self._current_page_name) == None:
                pass
            else:
                self._tab_pages[self._current_page_name]._hide()
                self._tab_page_buttons[self._current_page_name].config(
                    state="normal",
                    background=self.__layout.unselect_page_button_color
                )
            self._tab_pages[tab_page.page_name]._show()
            self._tab_page_buttons[tab_page.page_name].config(
                state="disabled",
                background=self.__layout.select_page_button_color
            )
        else:
            raise AssertionError("未預期之錯誤。")
        self._current_page_name = tab_page.page_name
    def button_command_create_page(self) -> None:
        self.__layout.operate_menu.entryconfig("創建", state="disabled")
        pop_up_window = tkinter.Toplevel(self.__main_window)
        pop_up_window.geometry("600x400+100+100")
        form_page = FormPage(pop_up_window)
        form_page.add_question(FillInBlankQuestionWidget(
            form_page.layout.form_frame,
            "分頁名稱？",
            DefaultQuestionLayout
        ))
        form_page.add_question(ComboBoxQuestionWidget(
            form_page.layout.form_frame,
            "分頁的種類？",
            DefaultQuestionLayout,
            sorted(self._register_types.keys())
        ))
        form_page.active_bind_command()
        while form_page.is_exist:
            time.sleep(0.1)
        page_name = form_page.result["分頁名稱？"]
        tab_page_type = self._register_types[form_page.result["分頁的種類？"]]
        new_tab_page = tab_page_type(page_name, self)
        self.add_tab_page(new_tab_page)
        self.refresh_pages_frame()
        self.__layout.operate_menu.entryconfig("創建", state="normal")
    def button_command_remove_page(self) -> None:
        self.__layout.operate_menu.entryconfig("刪除", state="disabled")
        pop_up_window = tkinter.Toplevel(self.__main_window)
        pop_up_window.geometry("600x400+100+100")
        form_page = FormPage(pop_up_window)
        form_page.add_question(ComboBoxQuestionWidget(
            form_page.layout.form_frame,
            "分頁名稱？",
            DefaultQuestionLayout,
            sorted(self._tab_pages.keys())
        ))
        form_page.active_bind_command()
        while form_page.is_exist:
            time.sleep(0.1)
        self.remove_tab_page(form_page.result["分頁名稱？"])
        self.refresh_pages_frame()
        self.__layout.operate_menu.entryconfig("刪除", state="normal")
    def bind_button_command_to_widget(self) -> None:
        self.__layout.operate_menu.add_command(label="創建", command=wrap_func_to_thread(self.button_command_create_page))
        self.__layout.operate_menu.add_command(label="刪除", command=wrap_func_to_thread(self.button_command_remove_page))
    def run(self) -> None:
        self.__layout = self.__type_of_layout(self.__main_window)
        self.__layout.create_widget()
        self.__layout.deploy_widget()
        self.bind_button_command_to_widget()
        self.__main_window.mainloop()
    @property
    def main_window(self) -> tkinter.Tk:
        return self.__main_window
    @property
    def layout(self) -> ITabPageManagerLayout:
        return self.__layout
