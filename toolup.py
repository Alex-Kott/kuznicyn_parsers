import asyncio
from time import sleep

from aiohttp import ClientSession
from bs4 import BeautifulSoup


def delay(f):
    async def wrapper(*args, **kwargs):
        sleep(0)
        await f(*args, **kwargs)
    return wrapper


@delay
async def parse_tool_items(session: ClientSession, tool_items_url: str):
    params = {
        'show': 60,
        'page': 1
    }
    while True:
        async with session.get(tool_items_url, params=params) as response:
            page_html = await response.text()
            soup = BeautifulSoup(page_html, 'lxml')

            span4s = soup.find_all(class_='span4')
            for i in span4s:
                product_link = i.find('a', itemprop='url')
                try:
                    href = product_link['href']
                except:
                    print(i)




@delay
async def parse_category(session: ClientSession, category_url: str):
    async with session.get(category_url) as response:
        category_page = await response.text()
        soup = BeautifulSoup(category_page, 'lxml')
        tools_menu = soup.find(class_='well-body')
        for tool in tools_menu.find_all("li"):
            print(tool.a['href'])
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
    asyncio.run(main())