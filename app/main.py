from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.routes import auth, notifications_router
from app.database import init_db


app = FastAPI(title="Notifications Service")


@app.on_event("startup")
async def startup():
    await init_db()


"""Просто красивый вывод главной страницы c ссылками:)"""
@app.get("/", response_class=HTMLResponse)
async def root():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Сервис Уведомлений API</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                line-height: 1.6;
            }
            .status {
                padding: 10px;
                background-color: #dff0d8;
                border: 1px solid #d6e9c6;
                border-radius: 4px;
                color: #3c763d;
                margin-bottom: 20px;
            }
            h1, h2 {
                color: #333;
            }
            .endpoint {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 4px;
                padding: 15px;
                margin-bottom: 10px;
            }
            .method {
                display: inline-block;
                padding: 3px 6px;
                border-radius: 3px;
                font-size: 12px;
                font-weight: bold;
                margin-right: 10px;
            }
            .get { background-color: #61affe; color: white; }
            .post { background-color: #49cc90; color: white; }
            .delete { background-color: #f93e3e; color: white; }
            .endpoint-link {
                color: #0366d6;
                text-decoration: none;
            }
            .endpoint-link:hover {
                text-decoration: underline;
            }
            .endpoint-description {
                display: flex;
                align-items: center;
                gap: 10px;
            }
        </style>
    </head>
    <body>
        <h1>Сервис Уведомлений API</h1>
        
        <div class="status">
            ✅ Статус Сервера: Работает
        </div>

        <h2>Доступные Эндпоинты:</h2>
        
        <h3>Аутентификация:</h3>
        <div class="endpoint">
            <div class="endpoint-description">
                <span class="method post">POST</span>
                <code>/auth/register</code> - 
                <a href="/docs#/Auth/register_auth_register_post" class="endpoint-link">Регистрация нового пользователя</a>
            </div>
        </div>
        <div class="endpoint">
            <div class="endpoint-description">
                <span class="method post">POST</span>
                <code>/auth/login</code> - 
                <a href="/docs#/Auth/login_auth_login_post" class="endpoint-link">Вход в систему</a>
            </div>
        </div>
        <div class="endpoint">
            <div class="endpoint-description">
                <span class="method post">POST</span>
                <code>/auth/refresh</code> - 
                <a href="/docs#/Auth/refresh_auth_refresh_post" class="endpoint-link">Обновление токена доступа</a>
            </div>
        </div>

        <h3>Уведомления:</h3>
        <div class="endpoint">
            <div class="endpoint-description">
                <span class="method get">GET</span>
                <code>/notifications/</code> - 
                <a href="/docs#/Notifications/list_notifs_notifications__get" class="endpoint-link">Получить список уведомлений</a>
            </div>
        </div>
        <div class="endpoint">
            <div class="endpoint-description">
                <span class="method post">POST</span>
                <code>/notifications/</code> - 
                <a href="/docs#/Notifications/create_notif_notifications__post" class="endpoint-link">Создать новое уведомление</a>
            </div>
        </div>
        <div class="endpoint">
            <div class="endpoint-description">
                <span class="method delete">DELETE</span>
                <code>/notifications/{notif_id}</code> - 
                <a href="/docs#/Notifications/delete_notif_notifications__notif_id__delete" class="endpoint-link">Удалить уведомление</a>
            </div>
        </div>

        <h3>Документация API:</h3>
        <div class="endpoint">
            <div class="endpoint-description">
                <span class="method get">GET</span>
                <code>/docs</code> - 
                <a href="/docs" class="endpoint-link">Swagger UI документация</a>
            </div>
        </div>
        <div class="endpoint">
            <div class="endpoint-description">
                <span class="method get">GET</span>
                <code>/redoc</code> - 
                <a href="/redoc" class="endpoint-link">ReDoc документация</a>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content


app.include_router(auth.router)
app.include_router(notifications_router.router)