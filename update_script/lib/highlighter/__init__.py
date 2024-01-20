from re import I
import sys
import os
from .light import ANSIColors, print_clr, print_init, print_time, print_info, print_err, print_info_2, print_up_to_date, print_update_info


if os.name == "nt":
    import winreg
    try:
        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Console", 0, winreg.KEY_WRITE)
        winreg.QueryValueEx(reg_key, "VirtualTerminalLevel")
    except:
        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Console", 0, winreg.KEY_WRITE)
        winreg.SetValueEx(reg_key, "VirtualTerminalLevel", 0, winreg.REG_DWORD, 0x1)
        winreg.CloseKey(reg_key)
        print("Restrart needed!")
        input()
        sys.exit()

