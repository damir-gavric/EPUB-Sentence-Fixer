# EPUB-Sentence-Fixer
The EPUB Sentence Fixer is a desktop application built in Python with a Tkinter-based GUI that assists in repairing broken sentences caused by poor PDF-to-EPUB conversions.

I made it for myself, it is simple and unpolished but it helps a lot.

## 🧪 Example

### ❌ Problem: Broken Sentence After Conversion

When EPUB is generated from a poorly converted PDF, sentences are often split across two `<div>` or `<p>` blocks, like this:

```html
<div>History is the systematic study of the past, focusing primarily on the human past. As an academic discipline, it analyses and interprets</div>
<div>evidence to construct narratives about what happened and explain why it happened.</div>

✅ ** Fixed Output**
Using EPUB Sentence Fixer, the above is reviewed and corrected to:
<div>History is the systematic study of the past, focusing primarily on the human past. As an academic discipline, it analyses and interprets evidence to construct narratives about what happened and explain why it happened.</div>



## 🚀 Features

- ✅ **Open and unpack EPUB files**
- 🧠 **Detect broken sentences** across `<div>` and `<p>` tags using simple heuristics
- 📝 **Editable merge proposal** per detection (modify before applying)
- ⏮️⏭️ **Step-by-step navigation**: Fix, Skip, or Go Back
- ✍️ **Live XHTML edits** using BeautifulSoup
- 📦 **Export a new, fixed EPUB** without touching the original
- 🗂️ **Change log** saved to a text file for reference

---

## 🔍 How It Works

1. Select an `.epub` file
2. The app extracts and analyzes its XHTML contents
3. Sentence breaks are flagged when:
   - The previous sentence doesn't end with punctuation
   - The next line starts lowercase
4. You get:
   - A side-by-side view of original sentences
   - An editable merge suggestion
   - A chance to confirm or skip each one

---

## 🛠 Tech Stack

| Tech         | Usage                           |
|--------------|----------------------------------|
| Python 3     | Core programming language        |
| `tkinter`    | GUI interface                    |
| `ebooklib`   | EPUB unpacking/validation        |
| `beautifulsoup4` | XHTML parsing and DOM edits   |
| `zipfile`    | Repacking fixed EPUB             |

---


