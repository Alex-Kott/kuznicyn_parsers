import asyncio
import json
from time import sleep
from typing import Dict, Any
from random import randint

import backoff as backoff
from aiohttp import ClientSession
from bs4 import BeautifulSoup


def delay(f):
    async def wrapper(*args, **kwargs):
        sleep(randint(1, 1))
        return await f(*args, **kwargs)
    return wrapper


def save_product(product_info: Dict[str, Any]):
    parsed_products.append(product_info)
    with open("data.json", "w") as file:
        json.dump(parsed_products, file)


def save_failed_product(e, product_url):
    with open("failed_products.txt", 'a') as file:
        file.write(f"{product_url}\n")


@delay
@backoff.on_exception(backoff.expo, Exception, max_tries=3)
async def parse_product(session: ClientSession, product_url: str) -> Dict[str, Any]:
    data = {}
    print(product_url)
    async with session.get(product_url) as response:
        page_html = await response.text()
        soup = BeautifulSoup(page_html, 'lxml')

        data['product_url'] = product_url

        breadcrumbs = soup.find(class_="breadcrumb").find_all('li')
        data['category'] = " > ".join([crumb.text.capitalize().strip('/') for crumb in breadcrumbs])

        title = soup.find('h1', {"data-type": "social-description"}).text.strip(' ')
        data['title'] = title

        product_id = soup.find('span', {'itemprop': 'mpn'}).text
        data['product_id'] = product_id

        manufacturer = title[:title.find(product_id)]
        data['manufacturer'] = manufacturer

        data['description'] = soup.find("span", {'itemprop': 'description'}).text
        data['availability'] = soup.find_all("link", {'itemprop': 'availability'})[1].parent.text.strip(' ')
        data['price'] = soup.find(class_='list-price-large').text

        try:
            slider = soup.find(class_="bxslider")
            imgs = []
            for img in slider.find_all('img'):
                imgs.append(img['src'])
            data['img'] = '; '.join(imgs)
        except:
            img_container = soup.find(class_="item-detailed-image-container")
            data['img'] = img_container.find('img')['src']

        return data


def count_pages(soup: BeautifulSoup) -> int:
    pagination_links = soup.find(class_="pagination-links")
    try:
        list_items = pagination_links.find_all("li")
        return len(list_items) - 2
    except AttributeError:
        return 1


@delay
async def parse_tool_items(session: ClientSession, tool_items_url: str):
    pages = 10
    current_page = 1
    params = {
        'show': 60,
        'page': current_page
    }
    while current_page <= pages:
        async with session.get(tool_items_url, params=params) as response:
            page_html = await response.text()
            soup = BeautifulSoup(page_html, 'lxml')
            pages = count_pages(soup)

            item_cells = soup.find_all(class_='item-cell')
            for item_cell in item_cells:
                product_link = item_cell.find('a', itemprop='url')

                try:
                    product_url = f"{main_url}{product_link['href']}"
                    if product_url not in parsed_products_links:
                        product_info = await parse_product(session, product_url)
                        print(product_info, end='\n\n')
                        save_product(product_info)
                except Exception as e:
                    print(e, product_link['href'], end='\n\n')
                    save_failed_product(e, product_url)

        params['page'] += 1
        current_page += 1



@delay
async def parse_category(session: ClientSession, category_url: str):
    async with session.get(category_url) as response:
        category_page = await response.text()
        soup = BeautifulSoup(category_page, 'lxml')
        tools_menu = soup.find(class_='well-body')
        for tool in tools_menu.find_all("li"):
            await parse_tool_items(session, f"{main_url}{tool.a['href']}")


async def main() -> None:
    async with ClientSession() as session:
        async with session.get(main_url) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'lxml')
            categories_menu = soup.find(class_='categories-menu')
            for item in categories_menu.find_all('li'):
                await parse_category(session, f"{main_url}{item.a['href']}")


if __name__ == "__main__":
    main_url = 'https://www.toolup.com'

    with open("data.json") as file:
        parsed_products = json.loads(file.read())

    print(len(parsed_products))

    parsed_products_links = [product['product_url'] for product in parsed_products]

    with open("failed_products.txt") as file:
        failed_product_links = {link for link in file.readlines()}

    asyncio.run(main())