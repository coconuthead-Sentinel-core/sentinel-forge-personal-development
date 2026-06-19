import sys
content = open('book_reader.py', 'r', encoding='utf-8').read()

start_str = '        self._study_tab_buttons = {}'
end_str = '            ("study_notes", "📝 Study Notes",'

start_idx = content.find(start_str)
end_idx = content.find(end_str)

new_code = '''        self._study_tab_buttons = {}

        # The Reader has been "removed" from the UI per user request, but because the
        # software has massive text_area/notes_area coupling, we build it silently
        # off-screen so those attributes still exist and won't crash the app.
        hidden_reader_frame = tk.Frame(content)
        try:
            self._build_tab_reader(hidden_reader_frame)
        except Exception:
            pass

        tabs = [
'''

if start_idx != -1 and end_idx != -1:
    new_content = content[:start_idx] + new_code + content[end_idx:]
    with open('book_reader.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Reader tab removed from UI successfully.")
else:
    print("Could not find insertion points.")
