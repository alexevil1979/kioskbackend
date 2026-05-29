from __future__ import annotations

import logging
import sys

logger = logging.getLogger(__name__)

if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    # Low-level keyboard hook constants
    WH_KEYBOARD_LL = 13
    WM_KEYDOWN = 0x0100
    WM_SYSKEYDOWN = 0x0104

    VK_TAB = 0x09
    VK_ESCAPE = 0x1B
    VK_LWIN = 0x5B
    VK_RWIN = 0x5C
    VK_LMENU = 0xA4
    VK_RMENU = 0xA5
    VK_DELETE = 0x2E
    VK_F4 = 0x73

    class KBDLLHOOKSTRUCT(ctypes.Structure):
        _fields_ = [
            ("vkCode", wintypes.DWORD),
            ("scanCode", wintypes.DWORD),
            ("flags", wintypes.DWORD),
            ("time", wintypes.DWORD),
            ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
        ]

    HOOKPROC = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)

    class KeyboardBlocker:
        """Блокирует Alt+Tab, Win, Alt+F4, Ctrl+Alt+Del (частично — CAD требует политик ОС)."""

        def __init__(self) -> None:
            self._hook_id = None
            self._proc = None
            self._alt_pressed = False

        def _callback(self, nCode: int, wParam: int, lParam: int) -> int:
            if nCode >= 0 and wParam in (WM_KEYDOWN, WM_SYSKEYDOWN):
                kb = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
                vk = kb.vkCode

                if vk in (VK_LMENU, VK_RMENU):
                    self._alt_pressed = True
                if vk in (VK_LWIN, VK_RWIN):
                    return 1
                if self._alt_pressed and vk == VK_TAB:
                    return 1
                if self._alt_pressed and vk == VK_F4:
                    return 1
                if self._alt_pressed and vk == VK_ESCAPE:
                    return 1
                # Ctrl+Alt+Del — на уровне hook не всегда перехватывается; нужна групповая политика
            return user32.CallNextHookEx(self._hook_id, nCode, wParam, lParam)

        def install(self) -> None:
            self._proc = HOOKPROC(self._callback)
            self._hook_id = user32.SetWindowsHookExW(
                WH_KEYBOARD_LL,
                self._proc,
                kernel32.GetModuleHandleW(None),
                0,
            )
            if not self._hook_id:
                logger.error("Не удалось установить keyboard hook")
            else:
                logger.info("Keyboard hook установлен")

        def uninstall(self) -> None:
            if self._hook_id:
                user32.UnhookWindowsHookEx(self._hook_id)
                self._hook_id = None

else:

    class KeyboardBlocker:
        def install(self) -> None:
            logger.warning("Блокировка клавиш только для Windows")

        def uninstall(self) -> None:
            pass
