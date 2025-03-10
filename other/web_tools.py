import aiohttp
import asyncio
import time
from dataclasses import dataclass
from typing import Optional, Dict, Any, Union

from loguru import logger

# Датакласс для ответа
@dataclass
class WebResponse:
    status: int  # Статус код ответа
    data: Union[Dict[str, Any], str]  # Данные ответа (JSON или текст)
    headers: Optional[Dict[str, str]] = None  # Заголовки ответа
    elapsed_time: Optional[float] = None  # Время выполнения запроса (в секундах)


class HTTPSessionManager:
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.session_start_time: float = 0.0
        self.max_session_duration = 3600  # 1 час в секундах
        self._lock = asyncio.Lock()  # Асинхронный lock для синхронизации

    async def get_session(self) -> aiohttp.ClientSession:
        async with self._lock:  # Блокируем доступ к сессии
            current_time = time.monotonic()
            if (
                    self.session is None
                    or self.session.closed
                    or current_time - self.session_start_time > self.max_session_duration
            ):
                if self.session and not self.session.closed:
                    await self.session.close()
                self.session = aiohttp.ClientSession()
                self.session_start_time = current_time
                logger.info("Сессия создана или пересоздана.")
            return self.session

    async def close(self):
        async with self._lock:  # Блокируем доступ к сессии
            if self.session and not self.session.closed:
                await self.session.close()
                logger.info("Сессия закрыта.")

    async def get_web_request(
            self,
            method: str,
            url: str,
            json: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            data: Optional[Union[Dict[str, Any], str]] = None,
            return_type: Optional[str] = None,
    ) -> WebResponse:
        """
        Выполняет HTTP-запрос с использованием текущей сессии.

        :param method: HTTP-метод (GET, POST, PUT и т.д.).
        :param url: URL для запроса.
        :param json: JSON-данные для отправки (для POST/PUT).
        :param headers: Заголовки запроса.
        :param data: Данные для отправки (для GET/POST).
        :param return_type: Ожидаемый тип ответа ('json' или None).
        :return: Экземпляр WebResponse.
        """
        session = await self.get_session()
        start_time = time.monotonic()

        try:
            async with session.request(
                    method.upper(), url, json=json, headers=headers, data=data
            ) as response:
                content_type = response.headers.get("Content-Type", "")
                elapsed_time = time.monotonic() - start_time

                # Определяем, как обрабатывать ответ
                if "application/json" in content_type or return_type == "json":
                    data = await response.json()
                else:
                    data = await response.text()

                return WebResponse(
                    status=response.status,
                    data=data,
                    headers=dict(response.headers),
                    elapsed_time=elapsed_time,
                )
        except aiohttp.ClientError as e:
            raise Exception(f"Ошибка при выполнении запроса: {e}")


http_session_manager = HTTPSessionManager()


# Пример использования
async def main():
    try:
        # GET-запрос
        response = await http_session_manager.get_web_request(
            "GET", "https://example.com", return_type="json"
        )
        print(f"GET Response: {response}")

        # POST-запрос
        post_data = {"key": "value"}
        response = await http_session_manager.get_web_request(
            "POST", "https://example.com", json=post_data
        )
        print(f"POST Response: {response}")

    finally:
        await http_session_manager.close()


async def get_eurmtl_xdr(url):
    try:
        url = 'https://eurmtl.me/remote/get_xdr/' + url.split('/')[-1]
        response = await http_session_manager.get_web_request('GET', url=url)

        if 'xdr' in response.data:
            return response.data['xdr']
        else:
            return 'Invalid response format: missing "xdr" field.'
    except Exception as ex:
        logger.info(['get_eurmtl_xdr', ex])
        return 'An error occurred during the request.'


if __name__ == "__main__":
    asyncio.run(main())
