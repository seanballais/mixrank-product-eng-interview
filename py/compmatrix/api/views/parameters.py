from enum import Enum


class ParamPartnership(Enum):
    """
    A parameter partnership that is coupled means that two or more parameters
    must be specified at the same time. A partnership that is inverse means
    that only one of two parameters must be specified.
    """
    COUPLED = 0
    INVERSE = 1
