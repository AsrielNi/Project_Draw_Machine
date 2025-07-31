import tkinter
import tkinter.ttk
from abc import ABC, abstractmethod
from typing import Iterable

########################################
class IFormLayout(ABC):
    @abstractmethod
    def __init__(self, master) -> None:
        raise NotImplementedError()
    @abstractmethod
    def create_widget(self) -> None:
        raise NotImplementedError()
    @abstractmethod
    def deploy_widget(self) -> None:
        raise NotImplementedError()
    @abstractmethod
    def clear_widget(self) -> None:
        raise NotImplementedError()
    @property
    @abstractmethod
    def form_frame(self) -> tkinter.Frame:
        raise NotImplementedError()
    @property
    @abstractmethod
    def submit_button(self) -> tkinter.Button:
        raise NotImplementedError()
    @property
    @abstractmethod
    def cancel_button(self) -> tkinter.Button:
        raise NotImplementedError()


class DefaultFormLayout(IFormLayout):
    def __init__(self, master) -> None:
        self.__master = master
    def create_widget(self) -> None:
        self._title_frame = tkinter.Frame(self.__master, background="cyan2")
        self._button_frame = tkinter.Frame(self.__master, background="green2")
        self._form_frame = tkinter.Frame(self.__master, background="yellow2")
        self._submit_button = tkinter.Button(self._button_frame, text="提交")
        self._cancel_button = tkinter.Button(self._button_frame, text="取消")
    def deploy_widget(self) -> None:
        self._title_frame.place(relx=0, rely=0, relwidth=0.75, relheight=0.1)
        self._button_frame.place(relx=0.75, rely=0, relwidth=0.25, relheight=0.1)
        self._button_frame.columnconfigure(index=(0, 1), weight=1)
        self._button_frame.rowconfigure(index=0, weight=1)
        self._form_frame.place(relx=0, rely=0.1, relwidth=1, relheight=0.9)
        self._submit_button.grid(row=0, column=0, padx=5, ipadx=5, pady=5, ipady=5)
        self._cancel_button.grid(row=0, column=1, padx=5, ipadx=5, pady=5, ipady=5)
    def clear_widget(self):
        self._title_frame.destroy()
        self._button_frame.destroy()
        self._form_frame.destroy()
        self._submit_button.destroy()
        self._cancel_button.destroy()
    @property
    def form_frame(self) -> tkinter.Frame:
        return self._form_frame
    @property
    def submit_button(self) -> tkinter.Button:
        return self._submit_button
    @property
    def cancel_button(self) -> tkinter.Button:
        return self._cancel_button
########################################

########################################
class IQuestionWidget(ABC):
    @abstractmethod
    def layout(self) -> None:
        raise NotImplementedError()
    @property
    @abstractmethod
    def question(self) -> str:
        raise NotImplementedError()
    @property
    @abstractmethod
    def answer(self) -> str:
        raise NotImplementedError()


class FillInBlankQuestionWidget(IQuestionWidget):
    def __init__(self, question: str):
        self.__master: tkinter.Tk | tkinter.Toplevel | tkinter.Frame
        self.__question: str = question
    def layout(self, master: tkinter.Tk | tkinter.Toplevel | tkinter.Frame):
        self.__master = master
        self._question_frame = tkinter.Frame(self.__master, background="cyan2")
        self._question_frame.pack(padx=10, pady=10, ipadx=10, ipady=10, fill="x")
        self._question_label = tkinter.Label(self._question_frame, text=self.__question)
        self._question_label.pack(fill="x")
        self._answer_sv = tkinter.StringVar()
        self._answer_entry = tkinter.Entry(self._question_frame, textvariable=self._answer_sv, width=1)
        self._answer_entry.pack(padx=10, ipadx=10, fill="x")
        self._message_label = tkinter.Label(self._question_frame, background=self._question_frame["background"])
        self._message_label.pack(padx=10, anchor="w")
    @property
    def question(self) -> str:
        return self.__question
    @property
    def answer(self) -> str:
        return self._answer_sv.get()

class ComboBoxQuestionWidget(IQuestionWidget):
    def __init__(self, question: str, opts_of_combobox: Iterable[str]):
        self.__master: tkinter.Tk | tkinter.Toplevel | tkinter.Frame
        self.__question: str = question
        self.__opts_of_combobox = opts_of_combobox
    def layout(self, master: tkinter.Tk | tkinter.Toplevel | tkinter.Frame):
        self.__master = master
        self._question_frame = tkinter.Frame(self.__master, background="cyan2")
        self._question_frame.pack(padx=10, pady=10, ipadx=10, ipady=10, fill="x")
        self._question_label = tkinter.Label(self._question_frame, text=self.__question)
        self._question_label.pack(fill="x")
        self._answer_cbbox = tkinter.ttk.Combobox(self._question_frame, values=self.__opts_of_combobox, state="readonly")
        self._answer_cbbox.pack(padx=10, ipadx=10, fill="x")
        self._message_label = tkinter.Label(self._question_frame, background=self._question_frame["background"])
        self._message_label.pack(padx=10, anchor="w")
    @property
    def question(self) -> str:
        return self.__question
    @property
    def answer(self) -> str:
        return self._answer_cbbox.get()
########################################

########################################
class FormPage:
    def __init__(self, type_of_layout: type[IFormLayout] = DefaultFormLayout):
        self.__master: tkinter.Tk | tkinter.Toplevel | tkinter.Frame
        self.__result: dict[str, str] = dict()
        self.__type_of_layout: type[IFormLayout] = type_of_layout
        self.__layout: IFormLayout
        self.__storage_questions: dict[str, IQuestionWidget] = dict()
        self.is_exist: bool = False
    def __on_closing(self):
        if isinstance(self.__master, tkinter.Tk) == True:
            self.__layout.clear_widget()
        elif isinstance(self.__master, tkinter.Toplevel) == True:
            self.__master.destroy()
        elif isinstance(self.__master, tkinter.Frame) == True:
            self.__layout.clear_widget()
        else:
            raise TypeError()
        self.is_exist = False
    def add_question(self, question_widget: IQuestionWidget) -> None:
        if self.__storage_questions.get(question_widget.question) != None:
            raise KeyError()
        else:
            self.__storage_questions[question_widget.question] = question_widget
    def remove_question(self, question: str) -> None:
        if self.__storage_questions.get(question) == None:
            raise KeyError()
        else:
            del self.__storage_questions[question]
    def deploy_question_widgets(self):
        for question_widget in self.__storage_questions.values():
            question_widget.layout(self.__layout.form_frame)
    def command_submit(self):
        for question_widget in self.__storage_questions.values():
            self.__result[question_widget.question] = question_widget.answer
        self.__on_closing()
    def command_cancel(self):
        self.__on_closing()
    def bind_command_to_widget(self):
        self.__layout.submit_button.config(command=self.command_submit)
        self.__layout.cancel_button.config(command=self.command_cancel)
    def deploy_to_master(self, master: tkinter.Tk | tkinter.Toplevel | tkinter.Frame):
        self.__master = master
        if isinstance(self.__master, tkinter.Toplevel) == True:
            self.__master.protocol("WM_DELETE_WINDOW", self.__on_closing)
        self.__layout = self.__type_of_layout(master)
        self.__layout.create_widget()
        self.__layout.deploy_widget()
        self.deploy_question_widgets()
        self.bind_command_to_widget()
        self.is_exist = True
    @property
    def result(self) -> dict[str, str]:
        return self.__result
########################################
