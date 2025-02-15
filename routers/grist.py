from datetime import datetime
from quart import Blueprint, jsonify, render_template, request
from other.grist_tools import grist_manager, MTLGrist
from loguru import logger

blueprint = Blueprint('grist', __name__)


# wijets

@blueprint.route('/grist/tg_info.html', methods=('GET',))
async def grist_tg_info():  #
    return await render_template('grist_tg_info.html')


# js points


from db.mongo import get_all_chats_by_user


@blueprint.route('/grist/groups/<user_id>', methods=('GET',))
async def grist_tg_info_groups(user_id):
    # Получаем ключ из заголовка
    auth_key = request.headers.get('X-Auth-Key')

    # Проверяем ключ с логированием
    key_check = await check_grist_key(
        auth_key,
        log_info=f'grist_tg_info_groups {user_id}'
    )
    if key_check['status'] != 'success':
        return jsonify(key_check), 403

    # Получаем данные о чатах пользователя
    try:
        user_id_int = int(user_id)
        chats = await get_all_chats_by_user(user_id_int)

        # Подготавливаем данные для шаблона
        chat_data = []
        for chat in chats:
            user_data = chat.users.get(str(user_id_int))
            if not user_data:
                continue

            chat_data.append({
                'title': chat.title or f"ID: {chat.chat_id}",
                'joined': user_data.created_at.strftime('%Y-%m-%d %H:%M') if user_data.created_at else '-',
                'left': user_data.left_at.strftime('%Y-%m-%d %H:%M') if user_data.left_at else '-'
            })

        return await render_template(
            'grist_tg_groups.html',
            chats=chat_data
        )

    except Exception as e:
        logger.error(f"Error getting chat info: {e}")
        return jsonify({
            "status": "error",
            "message": "Ошибка при получении данных о чатах"
        }), 500


async def check_grist_key(key: str, log_info: str = None) -> dict:
    """Проверка ключа доступа к Grist"""
    if not key:
        return {"status": "error", "message": "Необходимо указать ключ"}

    try:
        # Получаем данные из таблицы GRIST_access
        access_records = await grist_manager.load_table_data(MTLGrist.GRIST_access)

        # Ищем запись по ключу
        record = next((r for r in access_records if r.get('key') == key), None)

        if not record:
            return {
                "status": "error",
                "message": "Неверный ключ"
            }

        # Логируем запрос если указана информация для логирования
        if log_info:
            await grist_manager.post_data(
                MTLGrist.GRIST_use_log,
                json_data={
                    "records": [{
                        "fields": {
                            "user_id": record.get('user_id'),
                            "dt_use": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            "info": log_info
                        }
                    }]
                }
            )

        return {
            "status": "success",
            "message": "Ключ действителен",
            "data": {
                "dt_update": record.get('dt_update'),
                "user_id": record.get('user_id')
            }
        }

    except Exception as e:
        logger.error(f"Grist key check error: {e}")
        return {
            "status": "error",
            "message": "Ошибка при проверке ключа"
        }


@blueprint.route('/grist/menu', methods=('GET',))
async def grist_tg_info_menu():
    # Получаем ключ из заголовка
    auth_key = request.headers.get('X-Auth-Key')

    # Проверяем ключ
    key_check = await check_grist_key(auth_key)
    if key_check['status'] != 'success':
        return jsonify(key_check), 403

    menu_data = {
        "buttons": [
            {
                "title": "Группы",
                "endpoint": "https://eurmtl.me/grist/groups/$user_id$"
            },
            {
                "title": "Связь со скаей",
                "endpoint": "https://eurmtl.me/grist/sky_test/$user_id$"
            }
        ]
    }
    return jsonify(menu_data)


@blueprint.route('/grist/sky_test/<user_id>', methods=('GET',))
async def grist_sky_test(user_id: str):
    # Проверяем ключ доступа с логированием
    auth_key = request.headers.get('X-Auth-Key')
    key_check = await check_grist_key(
        auth_key,
        log_info=f'grist_sky_test {user_id}'
    )
    if key_check['status'] != 'success':
        return jsonify(key_check), 403

    # Проверяем наличие user_id
    if not user_id:
        return jsonify({
            "status": "error",
            "message": "Необходимо указать user_id"
        }), 400

    try:
        # Преобразуем user_id в int
        user_id_int = int(user_id)

        # Получаем skynet_bot из telegram_tools
        from other.telegram_tools import skynet_bot

        # Проверяем подписку
        try:
            chat = await skynet_bot.get_chat(user_id_int)
            return """
                <div class="alert alert-success" role="alert">
                    <h4 class="alert-heading">Успешно!</h4>
                    <p>Пользователь подписан на SkyNet</p>
                </div>
            """
        except Exception as e:
            return """
                <div class="alert alert-danger" role="alert">
                    <h4 class="alert-heading">Ошибка!</h4>
                    <p>Пользователь не подписан на SkyNet</p>
                </div>
            """
    except ValueError:
        return jsonify({
            "status": "error",
            "message": "Некорректный формат user_id"
        }), 400
    except Exception as e:
        logger.error(f"SkyNet test error: {e}")
        return jsonify({
            "status": "error",
            "message": "Ошибка при проверке подписки"
        }), 500


if __name__ == '__main__':
    pass
    # print(asyncio.run(remote_need_sign('GDLTH4KKMA4R2JGKA7XKI5DLHJBUT42D5RHVK6SS6YHZZLHVLCWJAYXI')))
