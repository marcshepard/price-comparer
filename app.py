import data
import tkinter as tk
import webbrowser
import urllib.request
from PIL import Image, ImageTk
import PIL
import ssl

# A control to display a hyperlink
class Hyperlink(tk.Label):
    def __init__(self, parent, text, url):
        super().__init__(parent, fg="blue", cursor="hand2", font="Arial 9 underline")
        self.set_link(text, url)
        self.bind("<Button-1>", self._open_url)

    def set_link (self, text, url):
        self.config(text=text)
        self.url = url

    def _open_url(self, event):
        webbrowser.open(self.url) 

# A control to display an image
class Image(tk.Label):
    """A control to display an image from a URL
    Uses a temp file to store the image, disables SSL cert
    verification on URL download to work around Python bug"""
    def __init__(self, parent, width=100, height=100):
        super().__init__(parent)
        self.url = None
        self.width = width
        self.height = height
        self.ssl_ctx = ssl._create_unverified_context()

    def set_image (self, url):
        self.url = url
        self._load_image()
    
    def _load_image(self):
        if self.url is None:
            return
        
        url_file_extension = self.url.split(".")[-1]
        if url_file_extension is None or len(url_file_extension) == 0:
            url_file_extension = "jpg"
        tmp_file = "temp." + url_file_extension

        try:
            with urllib.request.urlopen(self.url, context=self.ssl_ctx) as url:
                with open(tmp_file, "wb") as f:
                    f.write(url.read())
            image = PIL.Image.open(tmp_file)
            image = image.resize((self.width, self.height))
            image = ImageTk.PhotoImage(image)
            self.image = image
        except:
            print(f"Error loading image from {self.url}")

# The main app class
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Price Comparison")

        default_search = "shirt"

        # Create a frame to hold everything
        frame = tk.Frame(self)

        # Create a label
        pad = 10
        label = tk.Label(frame, text="Item")
        label.grid(row=0, column=0, padx=pad, pady=pad, sticky="w")
        self.entry = tk.Entry(frame)
        self.entry.insert(0, default_search)
        self.entry.grid(row=0, column=1, padx=pad, pady=pad, sticky="ew")
        self.entry.bind("<Return>", lambda event: self.search())
        button = tk.Button(frame, text="Search", command=self.search)
        button.grid(row=0, column=2, padx=pad, pady=pad, sticky="e")
        self.search_button = button
        
        # Create a scrollable grid
        df = data.create_merged_df(default_search)
        self.df = df

        # Header labels
        label = tk.Label(frame, text="price")
        label.grid(row=3, column=0, sticky="w")
        label = tk.Label(frame, text="item")
        label.grid(row=3, column=1, columnspan=2, sticky="nsew")

        # Add a listbox to hold the rows, and a scrollbar to scroll it
        scrollbar = tk.Scrollbar(frame, orient="vertical")
        scrollbar.grid(row=4, column=3, sticky="nsw")
        list = tk.Listbox(frame, yscrollcommand = scrollbar.set)
        list.grid(row=4, column=0, columnspan=3, sticky="nsew")
        list.bind("<<ListboxSelect>>", lambda event: self.select())
        scrollbar.config(command=list.yview)
        self.list = list
        self.fill_listbox(df)

        # Add the image and hyperlink of the selected item in the list
        self.image = Image(frame)
        self.image.grid(row=1, column=0, columnspan=3, padx=pad, pady=pad, sticky="nsew")
        self.link = Hyperlink(frame, "link", "https://www.google.com")
        self.link.grid(row=2, column=0, columnspan=3, padx=pad, pady=pad, sticky="nsew")

        self.select(0)

        # Pack the frame
        frame.pack(fill="both", expand=True)

    def search(self):
        """Search for the item in the entry box"""
        self.search_button.config(state="disabled", relief="sunken")
        self.update()
        item = self.entry.get().strip()
        if len(item) > 0:
            df = data.create_merged_df(item)
            self.fill_listbox(df)
        # resize window width to fit the longest item
        self.search_button.config(state="normal", relief="raised")

    def fill_listbox(self, df):
        """Fill the listbox with data from the dataframe"""
        self.list.delete(0, "end")

        max_len = 0
        for row in range(len(df)):
            price_col_ix = df.columns.get_loc("price")
            item_col_ix = df.columns.get_loc("item")
            text = f"${df.iloc[row, price_col_ix]:.2f}"
            text += " " * (10 - len(text))
            text += str(df.iloc[row, item_col_ix])
            max_len = max(max_len, len(text))
            self.list.insert("end", text)
        # set the listbox selection to the first item, if any
        if len(df) > 0:
            self.list.selection_set(0)
            self.list.activate(0)

        self.list.config(width=max_len + 8)

    def select(self, ix = None):
        if ix is None:
            ix = self.list.curselection()[0]
        df = self.df
        # Get the URL and item from self.df at row ix
        url = df.iloc[ix, df.columns.get_loc("url")]
        item = df.iloc[ix, df.columns.get_loc("item")]
        img_url = df.iloc[ix, df.columns.get_loc("img")]
        self.link.set_link(item, url)
        self.image.set_image(img_url)

# Run the app
app = App()
app.mainloop()
