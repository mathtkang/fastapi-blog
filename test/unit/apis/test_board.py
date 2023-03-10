from test.constants import BOARD_TITLE, UPDATED_BOARD_TITLE
from test.helper import ensure_fresh_env, with_app_ctx
from test.mock.user import create_owner, create_user
from test.utils import search_board

import pytest
import pytest_asyncio
from httpx import AsyncClient

from app.settings import AppSettings


class TestBoard:
    # 테스트 함수 실행시, 필요한 미리 정의된 입력값
    @pytest_asyncio.fixture(scope="class", autouse=True)
    async def _init_env(
        self,
        app_client: AsyncClient,
        app_settings: AppSettings,
    ) -> None:
        async with with_app_ctx(app_settings):
            await ensure_fresh_env()
            await create_user(app_client=app_client)
            await create_owner(app_client=app_client)

    @pytest.mark.asyncio
    async def test_create_board(self, app_client: AsyncClient, owner_access_token: str):
        response = await app_client.post(
            "/boards/",
            json={
                "title": BOARD_TITLE,
            },
            headers={"Authorization": f"Bearer {owner_access_token}"},
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_board(self, app_client: AsyncClient):
        board_id = (await search_board(app_client, BOARD_TITLE))["id"]

        response = await app_client.get(
            f"/boards/{board_id}",
        )

        assert response.status_code == 200
        assert response.json()["id"] == board_id
        assert response.json()["title"] == BOARD_TITLE

    @pytest.mark.asyncio
    async def test_update_board(self, app_client: AsyncClient, owner_access_token: str):
        board_id = (await search_board(app_client, BOARD_TITLE))["id"]

        response = await app_client.put(
            f"/boards/{board_id}",
            json={
                "title": UPDATED_BOARD_TITLE,
            },
            headers={"Authorization": f"Bearer {owner_access_token}"},
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_delete_board(self, app_client: AsyncClient, owner_access_token: str):
        board_id = (await search_board(app_client, UPDATED_BOARD_TITLE))["id"]

        response = await app_client.delete(
            f"/boards/{board_id}",
            headers={"Authorization": f"Bearer {owner_access_token}"},
        )
        assert response.status_code == 200
