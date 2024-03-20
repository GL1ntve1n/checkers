from checkers.enums import CheckerType


#Класс шашки
class Checker:
    def __init__(self, type: CheckerType = CheckerType.NONE):
        self.__type = type

    @property
    def type(self):
        return self.__type

    #Изменение типа шашки
    def change_type(self, type: CheckerType):
        self.__type = type
