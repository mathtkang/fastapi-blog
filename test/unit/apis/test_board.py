import pytest_asyncio
import pytest
from httpx import AsyncClient
from app.settings import AppSettings
from test.helper import with_app_ctx, ensure_fresh_env
from test.mock.user import create_user
from test.utils import search_board


BOARD_TITLE="This is a board title for the test"
UPDATED_BOARD_TITLE="This is a updated board title for the testf"

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
            await create_user(app_client)


    @pytest.mark.asyncio
    async def test_create_board(app_client: AsyncClient, user_access_token: str):
        response = await app_client.post(
            "/boards/",
            json={
                "title": BOARD_TITLE,
            },
            headers={
                "Authorization": f"Bearer {user_access_token}"
            }
        )

        assert response.status_code == 200
        assert response.json() == {
            "message": "Success created board"
        }


    @pytest.mark.asyncio
    async def test_get_board(app_client: AsyncClient):
        board_id = (
            await search_board(app_client, BOARD_TITLE)
        )['id']

        response = await app_client.get(
            f"/boards/{board_id}",
        )

        assert response.status_code == 200
        assert response.json()['id'] == board_id
        assert response.json()['title'] == BOARD_TITLE


    # DONE: 여기부터
    @pytest.mark.asyncio
    async def test_update_board(app_client: AsyncClient, user_access_token: str):
        board_id = (
            await search_board(app_client, BOARD_TITLE)
        )['id']

        response = await app_client.put(
            f"/boards/{board_id}",
            json={
                "title": UPDATED_BOARD_TITLE,
            },
            headers={
                "Authorization": f"Bearer {user_access_token}"
            }
        )
        assert response.status_code == 200
        assert response.json() == {
            "message": "Success updated board"
        }


    @pytest.mark.asyncio
    async def test_delete_board(app_client: AsyncClient, user_access_token: str):
        board_id = (
            await search_board(app_client, UPDATED_BOARD_TITLE)  # Question: UPDATED_BOARD_TITLE 으로 하는게 더 좋을까요?
        )['id']

        response = await app_client.delete(
            f"/boards/{board_id}",
            headers={
                "Authorization": f"Bearer {user_access_token}"
            }
        )
        assert response.status_code == 200
        assert response.json() == {
            "message": "Success deleted board"
        }