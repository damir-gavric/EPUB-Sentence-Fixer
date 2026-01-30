import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from ebooklib import epub
from bs4 import BeautifulSoup
import re
import os
import shutil
import zipfile

class EPUBFixerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EPUB Sentence Fixer")

        self.select_button = tk.Button(root, text="Select EPUB File", command=self.load_epub)
        self.select_button.pack(pady=10)

        self.text_display = scrolledtext.ScrolledText(root, width=100, height=30, wrap=tk.WORD)
        self.text_display.pack(padx=10, pady=10)

        self.merge_edit = tk.Text(root, height=6, width=100, wrap=tk.WORD, font=("Helvetica", 10))
        self.merge_edit.pack(padx=10, pady=(0, 10), fill=tk.BOTH, expand=True)

        self.fix_button = tk.Button(root, text="Fix", command=self.fix_current)
        self.skip_button = tk.Button(root, text="Skip", command=self.skip_current)
        self.back_button = tk.Button(root, text="Back", command=self.go_back)
        self.save_button = tk.Button(root, text="Save Fixed EPUB", command=self.save_fixed_epub)

        self.paragraphs = []
        self.suggestions = []
        self.tag_map = []
        self.current_suggestion_index = 0
        self.extracted_path = "_epub_working"
        self.loaded_epub_path = ""
        self.file_soups = {}
        self.applied_changes_log = []
        self.history_stack = []

    def load_epub(self):
        file_path = filedialog.askopenfilename(filetypes=[("EPUB files", "*.epub")])
        if not file_path:
            return

        self.loaded_epub_path = file_path
        self.cleanup_workspace()
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(self.extracted_path)

        self.paragraphs = []
        self.tag_map = []
        self.file_soups = {}
        self.applied_changes_log = []
        self.history_stack = []

        for root_dir, _, files in os.walk(self.extracted_path):
            for file in files:
                if file.endswith(".xhtml") or file.endswith(".html"):
                    full_path = os.path.join(root_dir, file)
                    with open(full_path, encoding="utf-8") as f:
                        soup = BeautifulSoup(f, "html.parser")
                        self.file_soups[full_path] = soup
                        for tag in soup.find_all(True):
                            if tag.name in ["p", "div"] and tag.get_text(strip=True):
                                text = tag.get_text().strip()
                                self.paragraphs.append(text)
                                self.tag_map.append((full_path, tag))

        self.suggestions = self.detect_broken_sentences(self.paragraphs)
        self.current_suggestion_index = 0
        self.display_next_suggestion()

    def cleanup_workspace(self):
        if os.path.exists(self.extracted_path):
            shutil.rmtree(self.extracted_path)

    def detect_broken_sentences(self, paragraphs):
        suggestions = []
        for i in range(1, len(paragraphs)):
            prev = paragraphs[i - 1].strip()
            curr = paragraphs[i].strip()
            if not prev or not curr:
                continue
            if not re.search(r'[.!?]["”\']?$|\)$', prev):
                if curr[0].islower():
                    suggestions.append((i - 1, prev, curr))
        return suggestions

    def display_next_suggestion(self):
        self.text_display.delete(1.0, tk.END)
        self.merge_edit.delete(1.0, tk.END)

        if self.current_suggestion_index >= len(self.suggestions):
            self.text_display.insert(tk.END, "✅ All suggestions processed. Click 'Save Fixed EPUB' to export.")
            self.fix_button.pack_forget()
            self.skip_button.pack_forget()
            self.back_button.pack_forget()
            self.save_button.pack(pady=5)
            return

        total = len(self.suggestions)
        i, prev, curr = self.suggestions[self.current_suggestion_index]
        merged = f"{prev} {curr}"

        print("\033[1mOriginal 1:\033[0m", prev)
        print("\033[1mOriginal 2:\033[0m", curr)

        self.text_display.insert(tk.END, f"--- Suggestion {self.current_suggestion_index + 1} of {total} --- (ID: {i})\n", "header")
        self.text_display.insert(tk.END, f"Original 1:\n{prev}\n", "original")
        self.text_display.insert(tk.END, f"Original 2:\n{curr}\n", "original")
        self.text_display.insert(tk.END, f"\nProposed Merge (editable below):\n\n", "merge")
        self.merge_edit.insert(tk.END, merged)

        self.text_display.tag_config("header", font=("Helvetica", 12, "bold"), foreground="blue")
        self.text_display.tag_config("original", font=("Helvetica", 10), foreground="black")
        self.text_display.tag_config("merge", font=("Helvetica", 10, "bold"), foreground="darkgreen")

        self.fix_button.pack(side=tk.LEFT, padx=10, pady=5)
        self.skip_button.pack(side=tk.LEFT, padx=10, pady=5)
        self.back_button.pack(side=tk.LEFT, padx=10, pady=5)

    def fix_current(self):
        if self.current_suggestion_index < len(self.suggestions):
            i, prev, curr = self.suggestions[self.current_suggestion_index]
            merged = self.merge_edit.get(1.0, tk.END).strip()
            self.history_stack.append((self.current_suggestion_index, prev, curr, self.paragraphs[i], self.paragraphs[i+1]))

            self.paragraphs[i] = merged
            self.paragraphs[i + 1] = ""
            file_path, tag = self.tag_map[i]
            _, tag_next = self.tag_map[i + 1]
            tag.string = merged
            tag_next.extract()

            self.applied_changes_log.append(f"[{file_path}]\nOriginal 1: {prev}\nOriginal 2: {curr}\nMerged: {merged}\n")

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(str(self.file_soups[file_path]))

            self.current_suggestion_index += 1
            self.display_next_suggestion()

    def skip_current(self):
        self.history_stack.append((self.current_suggestion_index, None, None, None, None))
        self.current_suggestion_index += 1
        self.display_next_suggestion()

    def go_back(self):
        if self.history_stack:
            self.current_suggestion_index, prev, curr, old_p1, old_p2 = self.history_stack.pop()
            if prev and curr:
                i = self.suggestions[self.current_suggestion_index][0]
                self.paragraphs[i] = old_p1
                self.paragraphs[i + 1] = old_p2
                file_path, tag = self.tag_map[i]
                _, tag_next = self.tag_map[i + 1]
                tag.string = old_p1
                new_tag = self.file_soups[file_path].new_tag(tag_next.name)
                new_tag.string = old_p2
                tag.insert_after(new_tag)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(str(self.file_soups[file_path]))
        self.display_next_suggestion()

    def save_fixed_epub(self):
        output_path = filedialog.asksaveasfilename(defaultextension=".epub", filetypes=[("EPUB files", "*.epub")])
        if not output_path:
            return

        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as epub_zip:
            mimetype_path = os.path.join(self.extracted_path, 'mimetype')
            if os.path.exists(mimetype_path):
                epub_zip.write(mimetype_path, 'mimetype', compress_type=zipfile.ZIP_STORED)
            for root, _, files in os.walk(self.extracted_path):
                for file in files:
                    full_path = os.path.join(root, file)
                    arcname = os.path.relpath(full_path, self.extracted_path)
                    if arcname != 'mimetype':
                        epub_zip.write(full_path, arcname)

        log_path = os.path.splitext(output_path)[0] + "_log.txt"
        with open(log_path, "w", encoding="utf-8") as log_file:
            log_file.write("\n\n".join(self.applied_changes_log))

        messagebox.showinfo("Success", f"Fixed EPUB saved to: {output_path}\nLog saved to: {log_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = EPUBFixerApp(root)
    root.mainloop()