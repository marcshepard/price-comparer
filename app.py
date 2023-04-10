import data
import tkinter as tk
import pandas as pd

# Create a scrollable grid of rows and columns from a pandas dataframe
class ScrollableGrid(tk.Frame):
    def __init__(self, df : pd.DataFrame, col_names : list = None, height : int =20):
        super().__init__(height=height)

        self.pd = pd
        if col_names is None:
            col_names = df.columns
        self.col_names = col_names
 
        for col in range(len(col_names)):
            col_name = col_names[col]
            label = tk.Label(self, text=col_name)
            label.grid(row=0, column=col)
        
        # Add a scrollbar
        self.scrollbar = tk.Scrollbar(self, orient="vertical")
        self.scrollbar.grid(row=1, column=len(col_names), sticky="nsw")
        self.scrollbar.config(command=self.yview)
        
        # For each loop over df rows
        for row in range(len(df)):
            if row >= height:
                break
            # For each loop over df columns
            for col in range(len(col_names)):
                # Get the value of the cell
                col_name = col_names[col]
                df_col_ix = df.columns.get_loc(col_name)
                value = df.iloc[row, df_col_ix]
                value = str(value)[:20]
                # Create a label for the cell
                label = tk.Label(self, text=value)
                # Place the label in the grid
                label.grid(row=row+1, column=col, sticky="w")

        self.pack()

    def yview(self, *args):
        self.scrollbar.set(*args)
        self.grid.yview(*args)

# Create tkinter window subclass
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Price Comparison")
        #self.geometry("400x400")

        # Create a frame to hold everything
        frame = tk.Frame(self)

        # Create a label
        pad = 10
        label = tk.Label(frame, text="Item")
        label.grid(row=0, column=0, padx=pad, pady=pad, sticky="w")
        self.entry = tk.Entry(frame)
        self.entry.grid(row=0, column=1, padx=pad, pady=pad, sticky="ew")
        button = tk.Button(frame, text="Search", command=self.search)
        button.grid(row=0, column=2, padx=pad, pady=pad, sticky="e")
        frame.pack()

        # Create a scrollable grid
        df = data.create_merged_df("shirt")
        self.grid = ScrollableGrid(df, ["price", "item"])
        self.grid.pack()

    def search(self):
        item = self.entry.get()
        df = data.create_merged_df(item)
        print(df)

# Run the app
app = App()
app.mainloop()
