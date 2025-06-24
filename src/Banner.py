import random
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, get_args


class IDrawMember(ABC):
    @classmethod
    @abstractmethod
    def _expose_opts(cls) -> tuple[str, ...]:
        raise NotImplementedError()
    @property
    @abstractmethod
    def member_info(self) -> dict[str, str | int]:
        raise NotImplementedError()
    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError()
    @property
    @abstractmethod
    def proportion(self) -> int:
        raise NotImplementedError()
    
DM = TypeVar("DM", bound=IDrawMember)

class BaseDrawMember(IDrawMember):
    _EXPOSE_OPTS = ("name", "proportion") # 公開參數名稱必須和建構式的參數名稱完全一樣
    @classmethod
    def _expose_opts(cls):
        temp_check_dict = dict()
        for opts in cls._EXPOSE_OPTS:
            if temp_check_dict.get(opts) != None:
                raise KeyError("抽選對象的公開參數名稱({})重複了。".format(opts))
            else:
                temp_check_dict[opts] = True
        del temp_check_dict
        return cls._EXPOSE_OPTS
    def __init__(self, name: str, proportion: int = 1):
        self._member_info_dict: dict[str, str | int] = dict()
        self._member_info_dict["name"] = name
        self._member_info_dict["proportion"] = proportion
    @property
    def member_info(self):
        return self._member_info_dict
    @property
    def name(self) -> str:
        return self._member_info_dict["name"]
    @property
    def proportion(self) -> int:
        return self._member_info_dict["proportion"]


class Banner(Generic[DM]):
    def __init__(self, banner_name: str):
        self._banner_name = banner_name
        self._draw_members: dict[str, DM] = dict()
    def add_draw_member(self, draw_member: DM):
        if self._draw_members.get(draw_member.name) != None:
            raise KeyError("該抽獎對象的名稱({})重複了".format(draw_member.name))
        else:
            self._draw_members[draw_member.name] = draw_member
    def remove_draw_member(self, draw_member_name: str):
        if self._draw_members.get(draw_member_name) == None:
            raise KeyError("該名稱({})並不存在。".format(draw_member_name))
        else:
            del self._draw_members[draw_member_name]
    def draw(self) -> str:
        if len(self._draw_members) == 0:
            result = "抽獎池沒有任何東西"
        else:
            draw_name_list = list()
            draw_proportion_list = list()
            for draw_m in self._draw_members.values():
                draw_name_list.append(draw_m.name)
                draw_proportion_list.append(draw_m.proportion)
            result = random.choices(draw_name_list, weights=draw_proportion_list)
        return result
    @property
    def banner_name(self) -> str:
        return self._banner_name
    @property
    def draw_members(self) -> dict[str, DM]:
        return self._draw_members
    @property
    def draw_member_type(self) -> type[DM]:
        if hasattr(self, "__orig_class__") == True:
            g1_type = get_args(self.__orig_class__)[0]
            if issubclass(g1_type, IDrawMember) == True:
                return g1_type
            else:
                raise TypeError("給定的類別({})必須是<IDrawMember>的子類。".format(g1_type.__name__))
        else:
            raise TypeError("未指定泛型類別，請指定一個<IDrawMember>的子類。 -> Example: {}[IDrawMember]()".format(self.__class__.__name__))
