"""
data.py - get data from eBay and Poshmark and merge into a single dataframe

Main method: create_merged_df(item : str) -> pd.DataFrame
item - what you are searching for
this method will cache the results in a file named item.csv and use that
(instead of a call to the web sites) if it is less than 1 day old
"""

import requests
from bs4 import BeautifulSoup
from sys import exit
from os import path
import pandas as pd

def create_merged_df (item : str) -> pd.DataFrame:
    """Create a merged dataframe of item listings from eBay and Poshmark
    sorted by price (least expensive first)"""

    # Used cached results if they exist and are less than 1 day old
    file_name = item + ".csv"
    if path.exists(file_name) and path.getmtime(file_name) > 86400:
        return pd.read_csv(file_name)

    # Else get the data from sites, merge them, cache results
    ebay_df = get_ebay_df(item)
    posh_df = get_poshmark_df(item)
    if (ebay_df.columns != posh_df.columns).any():
        print("Columns don't match")
        print("Ebay columns:", ebay_df.columns)
        print(ebay_df.dtypes)
        print("Posh columns:", posh_df.columns)
        print(posh_df.dtypes)
    df = pd.concat([ebay_df, posh_df], ignore_index=True)
    df = df.sort_values(by=['price'])
    df.to_csv(file_name, index=False)
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

def get_ebay_df(item : str):
    """Get the eBay dataframe for a given item"""
    url = "https://www.ebay.com/sch/" + item

    soup = get_soup(url)
    tagscost = soup.findAll(class_ = "s-item__price")
    tagsname = soup.findAll(class_ = "s-item__title")
    tagsimage = soup.findAll(class_ = "s-item__image")
    secondhand = soup.findAll(class_ = "SECONDARY_INFO")

    items = []
    prices = []
    images = []
    urls = []
    for i in range (1, len(tagsname)):
        item = tagsname[i].text + "(" + secondhand[i].text + ")"
        items.append(item)
        price = tagscost[i].text
        price = price.strip()
        price = price.split()[0]
        price = price.strip().strip('$')
        price = float(price)
        prices.append(price)
        img = tagsimage[i].find('img')["src"]
        images.append(img)
        url = tagsimage[i].find('a')["href"]
        if "?" in url:
            url = url.split("?")[0]
        urls.append(url)

    df = pd.DataFrame()
    df["item"] = items
    df["price"] = prices
    df["url"] = urls
    df["img"] = images

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

def get_poshmark_df (item : str) -> pd.DataFrame:
    """Get the Poshmark dataframe for a given item"""
    url = "https://poshmark.com/search?query=" + item + "%20&type=listings&src=dir"
    
    soup = get_soup(url)
    cards = soup.find_all("div", class_ = "card card--small")

    items = []
    prices = []
    urls = []
    images = []
    for card in cards:
        imagetag = card.find("img")
        if imagetag.has_attr("src"):
            image = imagetag["src"]
        elif imagetag.has_attr("data-src"):
            image = imagetag["data-src"]
        else:
            print(f"No image found, skipping")
            continue
        images.append(image)
        item = card.find('div', class_ = 'item__details')
        price = item.find('span', class_ = 'p--t--1 fw--bold').text
        price = price.strip().strip('$')
        price = float(price)
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
    df["img"] = images
    
    return df


# Run this code only if this file is run directly
if __name__ == "__main__":
    print ("Creating merged data from ebay and poshmark for 'shirt'")
    df = create_merged_df("shirt")
    print_df_info(df)
