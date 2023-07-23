import asyncio
from pyppeteer import launch
from bs4 import BeautifulSoup
import re
import os
# from google.cloud import storage
import requests
# Google Cloud Storage Configuration
# bucket_name = "your-bucket-name"
# storage_client = storage.Client()

def download_image(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    return None

async def scrape_data_and_links(url):
    # browser = await launch(executablePath='/usr/bin/google-chrome-stable', headless=True, args=['--no-sandbox'])

    browser = await launch()
    page = await browser.newPage()
    try:
        # Set a longer timeout, e.g., 60 seconds
        await page.goto(url, {'timeout': 240000})
        html_content = await page.content()
        soup = BeautifulSoup(html_content, 'html.parser') # get all page content
        dictionary = {'text': '', 'links': [], 'route':'', "image_links":[]}
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text_without_escape = re.sub(r'[\n\r]', '', p.text)
            text_without_consecutive_spaces = re.sub(r'\s{2,}', ' ', text_without_escape)
            dictionary['text'] += text_without_consecutive_spaces

        anchors = soup.find_all('a')
        for a in anchors:
            link_href = a.get('href')  # Get the href attribute
            dictionary['links'].append(link_href)

        images = soup.find_all("img")
        for img in images:
            image_link = img.get("src")
            if ('.png' or '.jpeg' or '.jpg' or '.svg') in image_link:
                # print('image_link',image_link)
                dictionary["image_links"].append(image_link)

        return dictionary

    finally:
        # Make sure to close the browser even if there is an exception
        await browser.close()

async def scrape_data(url):
    browser = await launch()
    # browser = await launch(executablePath='/usr/bin/google-chrome-stable', headless=True, args=['--no-sandbox'])
    page = await browser.newPage()

    try:
        # Set a longer timeout, e.g., 60 seconds
        await page.goto(url, {'timeout': 240000})
        html_content = await page.content()
        soup = BeautifulSoup(html_content, 'html.parser')

        dictionary = {'text': '', 'links': [], 'route':'', 'image_links':[]}
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text_without_escape = re.sub(r'[\n\r]', '', p.text)
            text_without_consecutive_spaces = re.sub(r'\s{2,}', ' ', text_without_escape)
            dictionary['text'] += text_without_consecutive_spaces

        images = soup.find_all("img")
        for img in images:
            image_link = img.get("src")
            if ('.png' or '.jpeg' or '.jpg' or '.svg') in image_link:
                # print('image_link',image_link)
                dictionary["image_links"].append(image_link)

        return dictionary

    finally:
        # Make sure to close the browser even if there is an exception
        await browser.close()

async def main(file_url):
    # Scrape the main URL
    try:
        data = []
        main_result = await scrape_data_and_links(file_url)
        data.append(main_result)

        if main_result["image_links"]:
            # print('image links',main_result["image_links"])
            for idx, image_link in enumerate(main_result['image_links']):
                if image_link is None:
                    continue
                image_data = download_image(image_link)
                if image_data:
                    image_blob_name = os.path.basename(image_link)
                    # print(image_blob_name,"image name")


        links_to_scrape = main_result['links']

        filter_urls = [url for url in links_to_scrape if url is not None]
        filtered_urls = [url for url in filter_urls if url.startswith('/') and (url != '/') and (url != '//') and ('.' not in url)]
        print('filtered_urls',filtered_urls)

        '''extractiin the base url'''
        # Find the index of the first occurrence of '.com'
        index_of_com = file_url.find('.com')

        # Extract the substring until '.com'
        extracted_string = file_url[:index_of_com + len('.com')]

        for i in filtered_urls:
            # print(i)
            if ('https' not in i) and (i != 'None') and ('/' in i):
                cur_url = extracted_string + i
                res = await scrape_data(cur_url)
                res['route'] = i
                data.append(res)

                # Download and upload images to GCS
                if res["image_links"]:
                    # print('image links', main_result["image_links"])
                    for idx, image_link in enumerate(res['image_links']):
                        if image_link is None:
                            continue
                        image_data = download_image(image_link)
                        if image_data:
                            image_blob_name = os.path.basename(image_link)
                            print(image_blob_name,"image name")
        return data
    except Exception as e:
        print(e)
        return 

data = {}
file_url = 'https://www.thehealthy.com/sleep/benefits-going-to-bed-earlier/'
res = asyncio.get_event_loop().run_until_complete(main(file_url)) 
print(res,'result')

'''try to save in csv file'''
import csv

def save_to_csv(data_list, file_name):
    # Check if the data_list is not empty
    if not data_list:
        print("Data list is empty. Nothing to save.")
        return

    # Extract field names from the first dictionary in the list
    field_names = data_list[0].keys()

    # Write data to CSV file
    with open(file_name, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(data_list)

# Example usage:

file_name = 'data1.csv'
save_to_csv(res, file_name)
