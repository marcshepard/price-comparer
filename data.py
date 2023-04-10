"""
data.py - get data from eBay and Poshmark and merge into a single dataframe

Main method: create_merged_df(item : str, use_cache=True) -> pd.DataFrame
item - what you are searching for
use_cache - if True, use cached data if it exists, otherwise get new data
"""

import requests
from bs4 import BeautifulSoup
from sys import exit
from os import path
import pandas as pd

def create_merged_df (item : str, use_cache=True) -> pd.DataFrame:
    """Create a merged dataframe of item listings from eBay and Poshmark
    with columns 'name', 'cost', 'condition'"""
    ebay_df = get_ebay_df(item, use_cache)

    posh_df = get_poshmark_df(item, use_cache)
    if (ebay_df.columns != posh_df.columns).any():
        print("Columns don't match")
        print("Ebay columns:", ebay_df.columns)
        print(ebay_df.dtypes)
        print("Posh columns:", posh_df.columns)
        print(posh_df.dtypes)
    df = pd.concat([ebay_df, posh_df], ignore_index=True)
    return df

def get_soup(url, print_soup=False):
    """Get the bs4 soup from a URL"""
    response = requests.get(url)
    if not response.ok:
        print(f"Error connecting to {url}: {response.status_code}")
        exit(-1)
    soup = BeautifulSoup(response.text, "html.parser")
    if print_soup:
        print(soup)
    return soup

def print_df_info(df):
    """print information about a dataframe - for debugging purposes"""
    print(f"Number of rows: {df.shape[0]}")
    print(f"Number of columns: {df.shape[1]}")
    print(f"Column names: {df.columns}")
    num_rows = 5
    print(f"First {num_rows} rows:")
    print(df.head(num_rows))

def get_ebay_df(item : str, use_cache : bool=True):
    """Get the eBay dataframe for a given item"""
    url = "https://www.ebay.com/sch/" + item
    file_name = "ebay " + item + ".csv"

    if use_cache and path.isfile(file_name):
        return pd.read_csv(file_name)

    soup = get_soup(url)
    tagscost = soup.findAll(class_ = "s-item__price")
    tagsname = soup.findAll(class_ = "s-item__title")
    secondhand = soup.findAll(class_ = "SECONDARY_INFO")

    items = []
    prices = []
    conditions = []
    for i in range (1, len(tagsname)):
        items.append(tagsname[i].text)
        price = tagscost[i].text
        price = price.strip()
        price = price.split()[0]
        price = price.strip().strip('$')
        try:
            price = float(price)
        except ValueError:
            print("Error converting price to float")
            print(price)
            exit(-1)
        prices.append(price)
        conditions.append(secondhand[i].text)

    df = pd.DataFrame()
    df["item"] = items
    df["price"] = prices
    df["url"] = "https://www.ebay.com"
    df["img"] = "https://commons.wikimedia.org/wiki/File:Blue_Tshirt.jpg"
    df["condition"] = conditions

    df.to_csv(file_name, index=False)

    return df

def get_attributes(soup_obj):
    "Extract product values from card"
    price = soup_obj['data-post-price']

    url_tag = soup_obj.a
    url = "https://poshmark.com" + url_tag['href']
    title = url_tag['title']

    img_tag = url_tag.img
    img = img_tag['src']

    return (title, price, url, img)

def get_poshmark_df (item : str, use_cache : bool=True) -> pd.DataFrame:
    """Get the Poshmark dataframe for a given item"""
    url = "https://poshmark.com/search?query=" + item + "%20&type=listings&src=dir"
    file_name = "poshmark " + item + ".csv"

    if use_cache and path.isfile(file_name):
        return pd.read_csv(file_name)
    
    soup = get_soup(url)
    item_container = soup.find_all('div', class_ = 'item__details')

    items = []
    prices = []
    urls = []
    for item in item_container:
        price = item.find('span', class_ = 'p--t--1 fw--bold').text
        price = price.strip().strip('$')
        prices.append(price)

        link = item.find('a')
        url = "https://poshmark.com" + link["href"]
        urls.append(url)

        item = link.text.strip()
        items.append(item)

    # Create a dataframe with columns items, prices, and urls
    df = pd.DataFrame(columns=["item", "price", "url"])
    df["item"] = items
    df["price"] = prices
    df["url"] = urls
    df["img"] = "https://commons.wikimedia.org/wiki/File:Blue_Tshirt.jpg"
    df["condition"] = "unknown"

    df.to_csv(file_name, index=False)

    return df


# Run this code only if this file is run directly
if __name__ == "__main__":
    print ("Creating merged data from ebay and poshmark for 'shirt'")
    df = create_merged_df("shirt")
    print_df_info(df)
