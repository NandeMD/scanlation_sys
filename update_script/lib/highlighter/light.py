import traceback
from dataclasses import dataclass


BLANK = 16


@dataclass(frozen=True)
class ANSIColors:
    BLACK = "\u001b[30m"
    RED = "\u001b[31m"
    GREEN = "\u001b[32m"
    YELLOW = "\u001b[33m"
    BLUE = "\u001b[34m"
    MAGENTA = "\u001b[35m"
    CYAN = "\u001b[36m"
    WHITE = "\u001b[37m"
    RESET = "\u001b[0m"


def print_clr(text: str, reset: bool = True):
    text = text
    for key, value in ANSIColors.__dict__.items():
        if not "_" in key or not "__" in key:
            text = text.replace(f"<{key}>", value)

    if reset:
        text += ANSIColors.RESET
    print(text)


def print_init(text: str, reset: bool = True):
    print_clr(
        f"<YELLOW>[INIT]<RESET>"
        f"{(BLANK-6)*' '}{text}"
    )


def print_time(elapsed: float):
    print_clr(
        f"<GREEN>[TIME]<RESET>"
        f"{(BLANK-6)*' '}"
        f"Took <CYAN>{elapsed}<RESET> seconds."
    )


def print_info(text: str):
    print_clr(
        f"<YELLOW>[INFO]<RESET>"
        f"{(BLANK-6)*' '}"
        f"{text}"
    )


def print_info_2(text: str, text2: str):
    print_clr(
        f"<YELLOW>[INFO]<RESET>"
        f"{(BLANK-6)*' '}"
        f"{text}<CYAN>{text2}"
    )


def print_err(text: str):
    print_clr(
        f"<RED>[ERROR]<RESET>"
        f"{(BLANK-7)*' '}"
        f"<MAGENTA>{text}\n"
        f"<RED>"
    )
    traceback.print_exc()
    print_clr("<RESET>")

def print_up_to_date(id: int):
    print_clr(
        f"<GREEN>[U-INFO]"
        f"{(BLANK-8)*' '}"
        f"<MAGENTA>ID: <CYAN>{id}"
        f"\tAlready up to date"
    )

def print_update_info(id: int, name: str, message: str):
    print_clr(
        f"<GREEN>[U-INFO]"
        f"{(BLANK-8)*' '}"
        f"<MAGENTA>ID: <CYAN>{id}  |  <MAGENTA>Name: <CYAN>{name}"
        f"\t{message}"
    )