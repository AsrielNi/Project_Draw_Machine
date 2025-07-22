import tkinter
from typing import Any


class RowFrame(tkinter.Frame):
    _DEFAULT_COLUMN_CONFIG = {"weight": 1}
    def __init__(self, master, max_column_idx: int, cnf={}, ref_column_config: dict[str, Any] | None = None, **kwargs):
        tkinter.Frame.__init__(self, master, cnf, **kwargs)
        self._column_widgets: dict[int, tkinter.Widget] = dict()
        self._max_column_idx: int = max_column_idx
        if ref_column_config == None:
            self._initialize_all_column_config(self._DEFAULT_COLUMN_CONFIG)
        else:
            self._initialize_all_column_config(ref_column_config)
    def _initialize_all_column_config(self, default_column_config: dict[str, Any]):
        for idx in range(0, self._max_column_idx):
            self.columnconfigure(index=idx, **default_column_config)
    def set_individual_column_config(self, idx: int, column_config: dict[str, Any]):
        if idx < 0:
            raise ValueError()
        elif idx > self._max_column_idx:
            raise ValueError()
        else:
            self.columnconfigure(index=idx, **column_config)
    def set_all_column_config(self, column_config: dict[str, Any]):
        for idx in range(0, self._max_column_idx):
            self.columnconfigure(index=idx, **column_config)
    def add_content(self, idx: int, widget_type: type[tkinter.Widget], widget_config: dict[str, Any]):
        if idx < 0:
            raise ValueError()
        elif idx > self._max_column_idx:
            raise ValueError()
        else:
            if self._column_widgets.get(idx) != None:
                raise KeyError()
            else:
                new_widget = widget_type(master=self, **widget_config)
                self._column_widgets[idx] = new_widget
                new_widget.grid(row=0, column=idx, sticky="news")
    def remove_content(self, idx: int):
        if idx < 0:
            raise ValueError()
        elif idx > self._max_column_idx:
            raise ValueError()
        else:
            if self._column_widgets.get(idx) == None:
                raise KeyError()
            else:
                self._column_widgets[idx].destroy()
                del self._column_widgets[idx]
    @property
    def max_column_idx(self) -> int:
        return self._max_column_idx
    @property
    def column_widgets(self) -> dict[int, tkinter.Widget]:
        return self._column_widgets


class RowFrameFactory:
    def __init__(self, max_column_idx: int, ref_column_config: dict[str, Any] | None = None):
        self._widget_type: type[tkinter.Widget]
        self._widget_config: dict[str, Any]
        self._max_column_idx: int = max_column_idx
        self._ref_column_config: dict[str, Any] = ref_column_config
        self._individual_configs: dict[int, dict[str, Any]] = dict()
    def set_default_widget_per_column(self, widget_type: type[tkinter.Widget], widget_config: dict[str, Any]):
        self._widget_type = widget_type
        self._widget_config = widget_config
    def set_individual_column_config(self, idx: int, column_config: dict[str, Any]):
        if idx < 0:
            raise ValueError()
        elif idx > self._max_column_idx:
            raise ValueError()
        else:
            self._individual_configs[idx] = column_config
    def create_row_frame(self, attach_master) -> RowFrame:
        row_frame = RowFrame(attach_master, self._max_column_idx, self._ref_column_config)
        for c_idx, column_config in self._individual_configs.items():
            row_frame.set_individual_column_config(c_idx, column_config)
        if (hasattr(self, "_widget_type") == True and
            hasattr(self, "_widget_config") == True):
            for idx in range(0, row_frame.max_column_idx):
                row_frame.add_content(idx, self._widget_type, self._widget_config)
        return row_frame
