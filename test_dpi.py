import tkinter as tk

# Windows 11 high-DPI scaling
try:
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception as e:
    print('DPI error:', e)

def _apply_win11_dark_mode(window):
    try:
        import ctypes
        window.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
        # Immersive dark mode (Windows 11)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, 20, ctypes.byref(ctypes.c_int(1)), 4
        )
        # Rounded corners (Windows 11) -> 2 = DWMWCP_ROUND
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, 33, ctypes.byref(ctypes.c_int(2)), 4
        )
        print('Applied Win11 Dark Mode and Rounded Corners')
    except Exception as e:
        print('Win11 API error:', e)

_orig_Tk_init = tk.Tk.__init__
def _new_Tk_init(self, *args, **kwargs):
    _orig_Tk_init(self, *args, **kwargs)
    self.after(10, lambda: _apply_win11_dark_mode(self))
tk.Tk.__init__ = _new_Tk_init

root = tk.Tk()
root.configure(bg='#0f172a')
tk.Label(root, text='Windows 11 Native Integration Check', bg='#0f172a', fg='white', font=('Segoe UI', 14)).pack(padx=20, pady=20)
root.after(1000, root.destroy)
root.mainloop()
