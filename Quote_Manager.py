import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3
import os
import sys

gl_author_id = -1
gl_book_id = -1
gl_quote_id = -1
gl_page = ""
quote_index = -1
quote_id_list = -1

def close_db():
    conn.close()

def on_window_close():
    close_db()
    window.destroy()

def connect_db():
    return sqlite3.connect(db_path)

def create_table():
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS authors (
        author_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
        );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        author_id INTEGER,
        book_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        PRIMARY KEY (author_id, book_id),
        FOREIGN KEY (author_id) REFERENCES authors(author_id)
        );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quotes (
        author_id INTEGER,
        book_id INTEGER,
        quote_id INTEGER,
        page TEXT NOT NULL,
        content TEXT NOT NULL,
        PRIMARY KEY (author_id, book_id, quote_id),
        FOREIGN KEY (author_id) REFERENCES authors(author_id),
        FOREIGN KEY (author_id, book_id) REFERENCES books(author_id, book_id)
        );  
    """)
    
    cursor.execute("INSERT INTO sqlite_sequence (name, seq) VALUES ('authors', 100);")
    cursor.execute("INSERT INTO sqlite_sequence (name, seq) VALUES ('books', 100);")
    cursor.execute("INSERT INTO sqlite_sequence (name, seq) VALUES ('quotes', 100);")
    
    conn.commit()
    
def get_author_names(clean=True):
    global gl_author_id
    global gl_book_id
    
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM authors;")
    authors = cursor.fetchall()
    cursor.close()
    author_list = [author[0] for author in authors]
    author_list.sort()
    author_name_combobox['values'] = author_list
    
    if clean:
        author_name_combobox.set("Select an author")
        gl_author_id = 0
        book_name_combobox.set("")
        gl_book_id = 0
        quote_id_combobox.set("")
        quote_content_text["state"] = "normal"
        quote_content_text.delete(1.0, tk.END)
        quote_content_text["state"] = "disable"
    
def edit_author():
    global gl_author_id
    author_id = gl_author_id
    
    if not author_id:
        return
    
    def ea_submit():
        name = ea_author_name_entry.get()
        
        cursor = conn.cursor()
        cursor.execute("UPDATE authors SET name = ? WHERE author_id = ?", (name, author_id))
        conn.commit()
        get_author_names(clean=False)
        author_name_combobox.set(name)
        
        edit_author_window.destroy()
    
    edit_author_window = tk.Toplevel(window)
    edit_author_window.title("Edit Author")
    edit_author_window.geometry("250x150")
    
    ea_author_info_frame = tk.Frame(
        edit_author_window
        )
    ea_author_info_frame.pack(side=tk.TOP, pady=20)
    
    ea_author_name_label = tk.Label(
        ea_author_info_frame,
        text="Author Name")
    ea_author_name_label.pack(side=tk.TOP)
    
    ea_author_name_entry = tk.Entry(
        ea_author_info_frame
        )
    ea_author_name_entry.pack(side=tk.TOP)
    ea_author_name_entry.insert(0, author_name_combobox.get())
    
    ea_submit_button = tk.Button(
        ea_author_info_frame,
        text="Submit",
        command=ea_submit
        )
    ea_submit_button.pack(side=tk.TOP, pady=10)
    
    edit_author_window.mainloop()  

def create_new_author():
    def cna_submit():
        global gl_author_id
        
        name = cna_author_name_entry.get()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO authors (name) VALUES (?)", (name,))
        conn.commit()
        get_author_names()
        author_name_combobox.set(name)
        cursor.execute("SELECT author_id FROM authors WHERE name = ?", (name,))
        author_id = cursor.fetchone()
        author_id = author_id[0]
        gl_author_id = author_id
        get_book_titles()
        add_author_window.destroy()
    
    add_author_window = tk.Toplevel(window)
    add_author_window.title("Add Author")
    add_author_window.geometry("250x150")
    
    cna_author_info_frame = tk.Frame(
        add_author_window
        )
    cna_author_info_frame.pack(side=tk.TOP, pady=20)
    
    cna_author_name_label = tk.Label(
        cna_author_info_frame,
        text="Enter Author Name")
    cna_author_name_label.pack(side=tk.TOP)
    
    cna_author_name_entry = tk.Entry(
        cna_author_info_frame
        )
    cna_author_name_entry.pack(side=tk.TOP)
    
    cna_submit_button = tk.Button(
        cna_author_info_frame,
        text="Submit",
        command=cna_submit
        )
    cna_submit_button.pack(side=tk.TOP, pady=10)
    
    add_author_window.mainloop()
    
def delete_author():
    global gl_author_id
    selected_author = author_name_combobox.get()
    author_id = gl_author_id
    confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete '{selected_author}'?")
    
    if confirm:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM quotes WHERE author_id = ?", (author_id,))
        cursor.execute("DELETE FROM books WHERE author_id = ?", (author_id,))
        cursor.execute("DELETE FROM authors WHERE author_id = ?", (author_id,))
        conn.commit()
        get_author_names()
    
def get_book_titles(event=None, clean=True):
    global gl_author_id
    global gl_book_id
    
    selected_author = author_name_combobox.get()
    
    if not selected_author:
        return
    
    cursor = conn.cursor()
    cursor.execute("SELECT author_id FROM authors WHERE name = ?", (selected_author,))
    author_id = cursor.fetchone()
    
    author_id = author_id[0]
    gl_author_id = author_id
    cursor.execute("SELECT title FROM books WHERE author_id = ?", (author_id,))
    books = cursor.fetchall()
    cursor.close()
    book_list = [book[0] for book in books]
    book_list.sort()
    book_name_combobox['values'] = book_list
    
    if clean:
        book_name_combobox.set("Select a book")
        gl_book_id = 0
        quote_id_combobox.set('')
        quote_content_text["state"] = "normal"
        quote_content_text.delete(1.0, tk.END)
        quote_content_text["state"] = "disable"
        
        edit_author_button['state'] = 'normal'
        delete_author_button['state'] = 'normal'
        new_book_button['state'] = 'normal'
        edit_book_button['state'] = 'disable'
        delete_book_button['state'] = 'disable'
        new_quote_button['state'] = 'disable'
        edit_quote_button['state'] = 'disable'
        delete_quote_button['state'] = 'disable'
    
def edit_book():
    global gl_author_id
    global gl_book_id

    author_id = gl_author_id
    book_id = gl_book_id
    
    def eb_submit():
        title = eb_book_title_entry.get()
        cursor = conn.cursor()
        cursor.execute("UPDATE books SET title = ? WHERE author_id = ? AND book_id = ?", (title, author_id, book_id))
        conn.commit()
        get_book_titles(clean=False)
        book_name_combobox.set(title)
        edit_book_window.destroy()
    
    edit_book_window = tk.Toplevel(window)
    edit_book_window.title("Edit Book")
    edit_book_window.geometry("250x150")
    
    eb_book_info_frame = tk.Frame(
        edit_book_window
        )
    eb_book_info_frame.pack(side=tk.TOP, pady=20)
    
    eb_book_name_label = tk.Label(
        eb_book_info_frame,
        text="Book Name")
    eb_book_name_label.pack(side=tk.TOP)
    
    eb_book_title_entry = tk.Entry(
        eb_book_info_frame
        )
    eb_book_title_entry.pack(side=tk.TOP)
    eb_book_title_entry.insert(0, book_name_combobox.get())
    
    eb_submit_button = tk.Button(
        eb_book_info_frame,
        text="Submit",
        command=eb_submit
        )
    eb_submit_button.pack(side=tk.TOP, pady=10)
    
    edit_book_window.mainloop()      


def create_new_book():
    def cnb_submit():
        global gl_author_id
        global gl_book_id
        
        author_id = gl_author_id
        name = cnb_book_name_entry.get().strip()
        if not name:
            return
        cursor = conn.cursor()
        
        cursor.execute("SELECT MAX(book_id) FROM books WHERE author_id = ?", (author_id,))
        max_book_id = cursor.fetchone()[0]
        
        if max_book_id is None:
            new_book_id = 101
        else:
            new_book_id = max_book_id + 1
            
        cursor.execute("INSERT INTO books (author_id, book_id, title) VALUES (?, ?, ?)", (author_id, new_book_id, name))
        conn.commit()
        get_book_titles()
        book_name_combobox.set(name)
        cursor.execute("SELECT book_id FROM books WHERE author_id = ? AND title = ?", (author_id, name,))
        book_id = cursor.fetchone()
        book_id = book_id[0]
        gl_book_id = book_id
        get_quote_ids()
        add_book_window.destroy()
    
    add_book_window = tk.Toplevel(window)
    add_book_window.title("Add Author")
    add_book_window.geometry("250x150")
    
    cnb_book_info_frame = tk.Frame(
        add_book_window
        )
    cnb_book_info_frame.pack(side=tk.TOP, pady=20)
    
    cnb_book_name_label = tk.Label(
        cnb_book_info_frame,
        text="Enter Book Name")
    cnb_book_name_label.pack(side=tk.TOP)
    
    cnb_book_name_entry = tk.Entry(
        cnb_book_info_frame
        )
    cnb_book_name_entry.pack(side=tk.TOP)
    
    cnb_submit_button = tk.Button(
        cnb_book_info_frame,
        text="Submit",
        command=cnb_submit
        )
    cnb_submit_button.pack(side=tk.TOP, pady=10)
    
    add_book_window.mainloop()
    
def delete_book():
    global gl_author_id
    global gl_book_id
    
    selected_book = book_name_combobox.get()
    author_id = gl_author_id
    book_id = gl_book_id
    confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete '{selected_book}'?")
    
    if confirm:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM quotes WHERE author_id = ? AND book_id = ?", (author_id, book_id,))
        cursor.execute("DELETE FROM books WHERE author_id = ? AND book_id = ?", (author_id, book_id,))
        conn.commit()
        get_book_titles()

def get_quote_ids(event=None, clean=True):
    global gl_author_id
    global gl_book_id
    
    global quote_id_list
    selected_book = book_name_combobox.get()
    
    author_id = gl_author_id
    if not selected_book:
        return
    
    cursor = conn.cursor()
    cursor.execute("SELECT book_id FROM books WHERE author_id = ? AND title = ?", (author_id, selected_book,))
    book_id = cursor.fetchone()
    
    book_id = book_id[0]
    gl_book_id = book_id
    cursor.execute("SELECT quote_id, page FROM quotes WHERE author_id = ? AND book_id = ?", (author_id, book_id,))
    quotes_pages = cursor.fetchall()
    cursor.close()
    quote_id_list = [quote_page[0] for quote_page in quotes_pages]
    page_list = [quote_page[1] for quote_page in quotes_pages]
    merge_list =[]
    
    for i, quote_id in enumerate(quote_id_list):
        merge_list.append(f"{gl_author_id}{gl_book_id}{quote_id} at page {page_list[i]}")

    quote_id_combobox['values'] = merge_list
    
    if clean:
        quote_id_combobox.set("Select a quote")
        quote_content_text["state"] = "normal"
        quote_content_text.delete(1.0, tk.END)    
        quote_content_text["state"] = "disable"
            
        edit_book_button['state'] = 'normal'
        delete_book_button['state'] = 'normal'
        new_quote_button['state'] = 'normal'
        edit_quote_button['state'] = 'disable'
        delete_quote_button['state'] = 'disable'
    
def edit_quote():
    global gl_author_id
    global gl_book_id
    global gl_quote_id
    
    author_id = gl_author_id
    book_id = gl_book_id
    quote_id = gl_quote_id
    
    def eq_submit():
        global quote_index
        page = eq_quote_page_entry.get().strip()
        quote = eq_content_text.get(1.0, "end-1c").strip()
        
        if not quote:
            return
        
        cursor = conn.cursor()
        cursor.execute("UPDATE quotes SET page = ?, content = ? WHERE author_id = ? AND book_id = ? AND quote_id = ?", (page, quote, author_id, book_id, quote_id,))
        conn.commit()
        quote_id_combobox.set(f"{gl_author_id}{gl_book_id}{quote_id} at page {page}")
        prev_quote_index = quote_index
        get_quote_info(passed_quote_index=prev_quote_index)
        get_quote_ids(clean=False)
        edit_quote_window.destroy()

    
    edit_quote_window = tk.Toplevel(window)
    edit_quote_window.title("Edit Quote")
    edit_quote_window.geometry("700x450")
    
    eq_quote_info_frame = tk.Frame(
        edit_quote_window
        )
    eq_quote_info_frame.pack(side=tk.TOP, pady=10)
    
    eq_quote_page_label = tk.Label(
        eq_quote_info_frame,
        text="Page Number")
    eq_quote_page_label.pack(side=tk.TOP)
    
    eq_quote_page_entry = tk.Entry(
        eq_quote_info_frame
        )
    eq_quote_page_entry.pack(side=tk.TOP, pady=10)
    eq_quote_page_entry.insert(0, gl_page)
    
    eq_content_label = tk.Label(
        eq_quote_info_frame,
        text="Content"
        )
    eq_content_label.pack(side=tk.TOP, pady=5)

    eq_content_text = tk.Text(
        eq_quote_info_frame,
        height=15,
        wrap=tk.WORD
        )
    eq_content_text.pack(side=tk.TOP, pady=5)
    eq_content_text.insert('1.0', quote_content_text.get(1.0, "end-1c"))
    
    eq_submit_button = tk.Button(
        eq_quote_info_frame,
        text="Submit",
        command=eq_submit
        )
    eq_submit_button.pack(side=tk.TOP, pady=10)
    
    edit_quote_window.mainloop()
    
def create_new_quote():
    def cnq_submit():
        global gl_author_id
        global gl_book_id
        global gl_quote_id
        
        author_id = gl_author_id
        book_id = gl_book_id
        page = cnq_quote_page_entry.get().strip()
        quote = cnq_content_text.get(1.0, "end-1c").strip()
        
        if not quote:
            return
        
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(quote_id) FROM quotes WHERE author_id = ? AND book_id = ?", (author_id, book_id,))
        max_quote_id = cursor.fetchone()[0]
        
        if max_quote_id is None:
            new_quote_id = 101
        else:
            new_quote_id = max_quote_id + 1

        gl_quote_id = max_quote_id
        cursor.execute("INSERT INTO quotes (author_id, book_id, quote_id, page, content) VALUES (?, ?, ?, ?, ?)", (author_id, book_id, new_quote_id, page, quote))
        conn.commit()
        get_quote_ids()
        quote_id_combobox.set(f"{gl_author_id}{gl_book_id}{new_quote_id} at page {page}")
        get_quote_info()
        add_quote_window.destroy()
    
    add_quote_window = tk.Toplevel(window)
    add_quote_window.title("Add Quote")
    add_quote_window.geometry("700x450")
    
    cnq_quote_info_frame = tk.Frame(
        add_quote_window
        )
    cnq_quote_info_frame.pack(side=tk.TOP, pady=10)
    
    cnq_quote_page_label = tk.Label(
        cnq_quote_info_frame,
        text="Enter Page Number")
    cnq_quote_page_label.pack(side=tk.TOP)
    
    cnq_quote_page_entry = tk.Entry(
        cnq_quote_info_frame
        )
    cnq_quote_page_entry.pack(side=tk.TOP, pady=10)
    
    cnq_content_label = tk.Label(
        cnq_quote_info_frame,
        text="Content"
        )
    cnq_content_label.pack(side=tk.TOP, pady=5)

    cnq_content_text = tk.Text(
        cnq_quote_info_frame,
        height=15,
        wrap=tk.WORD
        )
    cnq_content_text.pack(side=tk.TOP, pady=5)
    
    cnq_submit_button = tk.Button(
        cnq_quote_info_frame,
        text="Submit",
        command=cnq_submit
        )
    cnq_submit_button.pack(side=tk.TOP, pady=10)
    
    add_quote_window.mainloop()
    
def delete_quote():
    global gl_author_id
    global gl_book_id
    global gl_quote_id
    
    quote_id = gl_quote_id
    author_id = gl_author_id
    book_id = gl_book_id
    confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete the quote (ID: {gl_author_id}{gl_book_id}{quote_id})?")
    
    if confirm:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM quotes WHERE author_id = ? AND book_id = ? AND quote_id = ?", (author_id, book_id, quote_id,))
        conn.commit()
        get_quote_ids()

def get_quote_info(event=None, passed_quote_index=-1):
    global gl_author_id
    global gl_book_id
    global gl_quote_id
    global gl_page
    global quote_index
    global quote_id_list
    
    author_id = gl_author_id
    book_id = gl_book_id
    
    if passed_quote_index == -1:
        quote_index = quote_id_combobox.current()
    else:
        quote_index = passed_quote_index
        
    selected_quote_id = quote_id_list[quote_index]
    gl_quote_id = selected_quote_id
    
    if not selected_quote_id:
        return
    
    cursor = conn.cursor()
    cursor.execute("SELECT page, content FROM quotes WHERE author_id = ? AND book_id = ? AND quote_id = ?", (author_id, book_id, selected_quote_id,))
    quote_info = cursor.fetchone()
    
    if quote_info[0] and quote_info[1]:
        gl_page = quote_info[0]
        quote_content_text["state"] = "normal"
        quote_content_text.delete(1.0, tk.END)
        quote_content_text.insert('1.0', quote_info[1])
        quote_content_text["state"] = "disable"
    
    edit_quote_button['state'] = 'normal'
    delete_quote_button['state'] = 'normal'

window = tk.Tk()

window.title("Quote Manager")

window.geometry("1200x700")

entry_frame = tk.Frame(
    window
    )
entry_frame.pack(side=tk.TOP, fill=tk.BOTH)

author_frame = tk.Frame(
    entry_frame
    )
author_frame.pack(side=tk.TOP, fill=tk.BOTH, pady=20)

author_frame.columnconfigure(0, minsize=200)
author_frame.columnconfigure(1, weight=1)

author_frame_title_frame = tk.Frame(
    author_frame
    )
author_frame_title_frame.grid(row=0, column=0, sticky="w")

author_frame_title = tk.Label(
    author_frame_title_frame,
    text="Author Info",
    font=20
    )
author_frame_title.pack(padx=20)

author_frame_entry_frame = tk.Frame(
    author_frame
    )
author_frame_entry_frame.grid(row=0, column=1, sticky="nsew")

author_frame_entry_frame_container = tk.Frame(
    author_frame_entry_frame
    )
author_frame_entry_frame_container.pack()

author_name_label = tk.Label(
    author_frame_entry_frame_container,
    text="Name"
    )
author_name_label.grid(row=0, column=0, padx=20)

author_name_combobox = ttk.Combobox(
    author_frame_entry_frame_container,
    state="readonly"
    )
author_name_combobox.grid(row=1, column=0, padx=20)
author_name_combobox.bind("<<ComboboxSelected>>", get_book_titles)

edit_author_button = tk.Button(
    author_frame_entry_frame_container,
    text="Edit",
    command=edit_author,
    state="disable"
    )
edit_author_button.grid(row=1, column=1, padx=10)

new_author_button = tk.Button(
    author_frame_entry_frame_container,
    text="New",
    command=create_new_author
    )
new_author_button.grid(row=1, column=2, padx=10)

delete_author_button = tk.Button(
    author_frame_entry_frame_container,
    text="Delete",
    command=delete_author,
    state="disable"
    )
delete_author_button.grid(row=1, column=3, padx=10)

seperator1 = tk.Frame(
    entry_frame,
    bg="grey",
    height=1
    )
seperator1.pack(side=tk.TOP, fill=tk.BOTH)

book_frame = tk.Frame(
    entry_frame
    )
book_frame.pack(side=tk.TOP, fill=tk.BOTH, pady=20)

book_frame.columnconfigure(0, minsize=200)
book_frame.columnconfigure(1, weight=1)

book_frame_title_frame = tk.Frame(
    book_frame
    )
book_frame_title_frame.grid(row=0, column=0, sticky="w")

book_frame_title = tk.Label(
    book_frame_title_frame,
    text="Book Info",
    font=20
    )
book_frame_title.pack(padx=20)

book_frame_entry_frame = tk.Frame(
    book_frame
    )
book_frame_entry_frame.grid(row=0, column=1, sticky="nsew")

book_frame_entry_frame_container = tk.Frame(
    book_frame_entry_frame
    )
book_frame_entry_frame_container.pack()

book_name_label = tk.Label(
    book_frame_entry_frame_container,
    text="Name"
    )
book_name_label.grid(row=0, column=0, padx=20)

book_name_combobox = ttk.Combobox(
    book_frame_entry_frame_container,
    state="readonly"
    )
book_name_combobox.grid(row=1, column=0, padx=20)
book_name_combobox.bind("<<ComboboxSelected>>", get_quote_ids)

edit_book_button = tk.Button(
    book_frame_entry_frame_container,
    text="Edit",
    command=edit_book,
    state="disable"
    )
edit_book_button.grid(row=1, column=1, padx=10)

new_book_button = tk.Button(
    book_frame_entry_frame_container,
    text="New",
    command=create_new_book,
    state="disable"
    )
new_book_button.grid(row=1, column=2, padx=10)

delete_book_button = tk.Button(
    book_frame_entry_frame_container,
    text="Delete",
    command=delete_book,
    state="disable"
    )
delete_book_button.grid(row=1, column=3, padx=10)

seperator2 = tk.Frame(
    entry_frame,
    bg="grey",
    height=1
    )
seperator2.pack(side=tk.TOP, fill=tk.BOTH)

quote_frame = tk.Frame(
    entry_frame
    )
quote_frame.pack(side=tk.TOP, fill=tk.BOTH, pady=20)

quote_frame.columnconfigure(0, minsize=200)
quote_frame.columnconfigure(1, weight=1)

quote_frame_title_frame = tk.Frame(
    quote_frame
    )
quote_frame_title_frame.grid(row=0, column=0, sticky="w")

quote_frame_title = tk.Label(
    quote_frame_title_frame,
    text="Quote Info",
    font=20
    )
quote_frame_title.pack(padx=20)

quote_frame_entry_frame = tk.Frame(
    quote_frame
    )
quote_frame_entry_frame.grid(row=0, column=1, sticky="nsew")

quote_frame_entry_frame_container = tk.Frame(
    quote_frame_entry_frame
    )
quote_frame_entry_frame_container.pack()

quote_id_label = tk.Label(
    quote_frame_entry_frame_container,
    text="ID"
    )
quote_id_label.grid(row=0, column=0, padx=20)

quote_id_combobox = ttk.Combobox(
    quote_frame_entry_frame_container,
    state="readonly"
    )
quote_id_combobox.grid(row=1, column=0, padx=20)
quote_id_combobox.bind("<<ComboboxSelected>>", get_quote_info)

edit_quote_button = tk.Button(
    quote_frame_entry_frame_container,
    text="Edit",
    command=edit_quote,
    state="disable"
    )
edit_quote_button.grid(row=1, column=1, padx=10)

new_quote_button = tk.Button(
    quote_frame_entry_frame_container,
    text="New",
    command=create_new_quote,
    state="disable"
    )
new_quote_button.grid(row=1, column=2, padx=10)

delete_quote_button = tk.Button(
    quote_frame_entry_frame_container,
    text="Delete",
    command=delete_quote,
    state="disable"
    )
delete_quote_button.grid(row=1, column=3, padx=10)

quote_content_container = tk.Frame(
    quote_frame_entry_frame
    )
quote_content_container.pack(pady=30)

quote_content_label = tk.Label(
    quote_content_container,
    text="Content"
    )
quote_content_label.grid(row=0, column=0)

quote_content_text = tk.Text(
    quote_content_container,
    height=15,
    wrap=tk.WORD,
    state="disable"
    )
quote_content_text.grid(row=1, column=0)

seperator3 = tk.Frame(
    entry_frame,
    bg="grey",
    height=1
    )
seperator3.pack(side=tk.TOP, fill=tk.BOTH)

version_label = tk.Label(
    window,
    text="Developed by yzm. |  Version 1.1",
    font=("Arial", 8, "italic"),
    anchor='e'
    )
version_label.pack(side='bottom', padx=5, pady=3, fill='x')

db_file = 'quotes.db'
    
if getattr(sys, 'frozen', False):
    app_path = os.path.dirname(sys.executable)
else:
    app_path = os.path.dirname(os.path.abspath(__file__))

db_path = os.path.join(app_path, 'quotes.db')

if not os.path.exists(db_path):
    conn = connect_db()
    create_table()
else:
    conn = sqlite3.connect(db_path)

create_table()
get_author_names()

window.protocol("WM_DELETE_WINDOW", on_window_close)

window.mainloop()

