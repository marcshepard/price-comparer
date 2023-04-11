import data
import tkinter as tk
import pandas as pd


# Create tkinter window subclass
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
        button = tk.Button(frame, text="Search", command=self.search)
        button.grid(row=0, column=2, padx=pad, pady=pad, sticky="e")

        # Create a scrollable grid
        df = data.create_merged_df(default_search)

        # Header labels
        label = tk.Label(frame, text="price")
        label.grid(row=1, column=0, sticky="w")
        label = tk.Label(frame, text="item")
        label.grid(row=1, column=1, columnspan=2, sticky="nsew")

        # Add a listbox to hold the rows, and a scrollbar to scroll it
        scrollbar = tk.Scrollbar(frame, orient="vertical")
        scrollbar.grid(row=2, column=3, sticky="nsw")
        list = tk.Listbox(frame, yscrollcommand = scrollbar.set)
        list.grid(row=2, column=0, columnspan=3, sticky="nsew")
        scrollbar.config(command=list.yview)
 
        # Fill the listbox with data
        for row in range(len(df)):
            price_col_ix = df.columns.get_loc("price")
            item_col_ix = df.columns.get_loc("item")
            text = f"${df.iloc[row, price_col_ix]:.2f}"
            text += " " * (10 - len(text))
            text += str(df.iloc[row, item_col_ix])
            list.insert("end", text)

        # Pack the frame
        frame.pack(fill="both", expand=True)

    def search(self):
        item = self.entry.get()
        df = data.create_merged_df(item)
        print(df)

# Run the app
app = App()
app.mainloop()
