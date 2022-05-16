"""RequestHelper module."""

import http
import json
import logging
from typing import Optional

import aiohttp

logging.basicConfig(level=logging.INFO)


class RequestHelper(object):
    """Request helper."""

    @classmethod
    async def get(cls, url: str, req_params: Optional[dict] = None) -> dict:
        """
        Get request.

        Args:
            url (str): url.
            req_params (Optional[dict]): params of request.

        Returns:
            dict: result of request.

        Raises:
            Exception: if status code not equal 200.
        """
        if not req_params:
            req_params = {}

        async with aiohttp.ClientSession() as session:
            async with session.get(url=url, params=req_params) as resp:
                logging.info(f'Request send to {url}. Status: {resp.status}')
                if resp.status != http.HTTPStatus.OK:
                    raise Exception(f'Bad response status: {resp.status}')
                json_data = await resp.text()
                return json.loads(json_data)
