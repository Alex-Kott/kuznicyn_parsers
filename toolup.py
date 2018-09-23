import asyncio
from time import sleep

from aiohttp import ClientSession
from bs4 import BeautifulSoup


def delay(f):
    async def wrapper(*args, **kwargs):
        sleep(1)
        await f(*args, **kwargs)
    return wrapper


@delay
async def parse_category(session: ClientSession, category_url: str):
    async with session.get(category_url) as response:
        category_page = await response.text()
        soup = BeautifulSoup(category_page, 'lxml')
        tools_menu = soup.find(class_='well-body')
        for tool in tools_menu.find_all("li"):
            print(tool.a['href'])


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