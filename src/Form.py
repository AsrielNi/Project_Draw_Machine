import tkinter
import tkinter.ttk
from abc import ABC, abstractmethod
from typing import Iterable, TypeVar, Generic

########################################
class IFormLayout(ABC):
    @abstractmethod
    def __init__(self, master: tkinter.Tk | tkinter.Toplevel | tkinter.Frame) -> None:
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
    def __init__(self, master: tkinter.Tk | tkinter.Toplevel | tkinter.Frame) -> None:
        self.__master: tkinter.Tk | tkinter.Toplevel | tkinter.Frame = master
        self._title_frame: tkinter.Frame
        self._button_frame: tkinter.Frame
        self._form_frame: tkinter.Frame
        self._submit_button: tkinter.Button
        self._cancel_button: tkinter.Button
        self.create_widget()
        self.deploy_widget()
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
class IQusetionLayout(ABC):
    @abstractmethod
    def __init__(self, master: tkinter.Tk | tkinter.Toplevel | tkinter.Frame, question: str) -> None:
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
    def question_frame(self) -> tkinter.Frame:
        raise NotImplementedError()
    @property
    @abstractmethod
    def question_label(self) -> tkinter.Label:
        raise NotImplementedError()
    @property
    @abstractmethod
    def answer_frame(self) -> tkinter.Frame:
        raise NotImplementedError()
    @property
    @abstractmethod
    def message_label(self) -> tkinter.Label:
        raise NotImplementedError()

class DefaultQuestionLayout(IQusetionLayout):
    def __init__(self, master: tkinter.Tk | tkinter.Toplevel | tkinter.Frame, question: str) -> None:
        self.__master = master
        self.__question: str = question
        self.create_widget()
        self.deploy_widget()
    def create_widget(self):
        self._question_frame = tkinter.Frame(self.__master, background="cyan2")
        self._question_label = tkinter.Label(self._question_frame, text=self.__question)
        self._answer_frame = tkinter.Frame(self._question_frame)
        self._message_label = tkinter.Label(self._question_frame, background=self._question_frame["background"])
    def deploy_widget(self):
        self._question_frame.pack(padx=10, pady=10, ipadx=10, ipady=10, fill="x")
        self._question_label.pack(fill="x")
        self._answer_frame.pack(padx=10, ipadx=10, fill="x")
        self._message_label.pack(padx=10, anchor="w")
    def clear_widget(self):
        self._question_frame.destroy()
        self._question_label.destroy()
        self._answer_frame.destroy()
        self._message_label.destroy()
    @property
    def question_frame(self) -> tkinter.Frame:
        return self._question_frame
    @property
    def question_label(self) -> tkinter.Label:
        return self._question_label
    @property
    def answer_frame(self) -> tkinter.Frame:
        return self._answer_frame
    @property
    def message_label(self) -> tkinter.Label:
        return self._message_label


W = TypeVar("W", bound=tkinter.Widget)

class BaseQuestionWidget(Generic[W]):
    def __init__(
            self,
            master: tkinter.Tk | tkinter.Toplevel | tkinter.Frame,
            question: str, type_of_layout: type[IQusetionLayout]
        ) -> None:
        self._master: tkinter.Tk | tkinter.Toplevel | tkinter.Frame = master
        self._question: str = question
        self._layout: IQusetionLayout = type_of_layout(self._master, self._question)
        self.build_interact_widget()
    def build_interact_widget(self) -> None:
        raise NotImplementedError()
    @property
    def question(self) -> str:
        return self._question
    @property
    def answer(self) -> str:
        raise NotImplementedError()
    @property
    def interact_widget(self) -> W:
        raise NotImplementedError()


class FillInBlankQuestionWidget(BaseQuestionWidget[tkinter.Entry]):
    def build_interact_widget(self):
        self._answer_sv: tkinter.StringVar = tkinter.StringVar()
        self._answer_entry: tkinter.Entry = tkinter.Entry(self._layout.answer_frame, textvariable=self._answer_sv)
        self._answer_entry.pack(fill="both")
    @property
    def answer(self) -> str:
        return self._answer_sv.get()
    @property
    def interact_widget(self):
        return self._answer_entry


class ComboBoxQuestionWidget(BaseQuestionWidget[tkinter.ttk.Combobox]):
    def __init__(self, master, question, type_of_layout, opts_of_combobox: Iterable[str]) -> None:
        self.__opts_of_combobox: Iterable[str] = opts_of_combobox
        BaseQuestionWidget.__init__(self, master, question, type_of_layout)
    def build_interact_widget(self):
        self._answer_cbbox: tkinter.ttk.Combobox = tkinter.ttk.Combobox(self._layout.answer_frame, values=self.__opts_of_combobox, state="readonly")
        self._answer_cbbox.pack(fill="both")
    @property
    def answer(self) -> str:
        return self._answer_cbbox.get()
    @property
    def interact_widget(self):
        return self._answer_cbbox
########################################

########################################
class FormPage:
    def __init__(self, master: tkinter.Tk | tkinter.Toplevel | tkinter.Frame, type_of_layout: type[IFormLayout] = DefaultFormLayout):
        self.__master: tkinter.Tk | tkinter.Toplevel | tkinter.Frame = master
        self.__result: dict[str, str] = dict()
        self.__layout: IFormLayout = type_of_layout(self.__master)
        self.__storage_questions: dict[str, BaseQuestionWidget] = dict()
        self.is_exist: bool = True
    def __on_closing(self) -> None:
        if isinstance(self.__master, tkinter.Tk) == True:
            self.__layout.clear_widget()
        elif isinstance(self.__master, tkinter.Toplevel) == True:
            self.__master.destroy()
        elif isinstance(self.__master, tkinter.Frame) == True:
            self.__layout.clear_widget()
        else:
            raise TypeError()
        self.is_exist = False
    def add_question(self, question_widget: BaseQuestionWidget) -> None:
        if self.__storage_questions.get(question_widget.question) != None:
            raise KeyError()
        else:
            self.__storage_questions[question_widget.question] = question_widget
    def remove_question(self, question: str) -> None:
        if self.__storage_questions.get(question) == None:
            raise KeyError()
        else:
            del self.__storage_questions[question]
    def command_submit(self) -> None:
        for question_widget in self.__storage_questions.values():
            self.__result[question_widget.question] = question_widget.answer
        self.__on_closing()
    def command_cancel(self) -> None:
        self.__on_closing()
    def bind_command_to_widget(self) -> None:
        self.__layout.submit_button.config(command=self.command_submit)
        self.__layout.cancel_button.config(command=self.command_cancel)
    def active_bind_command(self) -> None:
        if isinstance(self.__master, tkinter.Toplevel) == True:
            self.__master.protocol("WM_DELETE_WINDOW", self.__on_closing)
        self.bind_command_to_widget()
    @property
    def layout(self) -> IFormLayout:
        return self.__layout
    @property
    def result(self) -> dict[str, str]:
        return self.__result
########################################
