@echo off

set STACK_NAME=learning-platform

echo Удаление stack '%STACK_NAME%'...
docker stack rm %STACK_NAME%

echo.
echo Ожидание завершения удаления...
timeout /t 10 /nobreak >nul

echo.
echo Проверка статуса:
docker stack services %STACK_NAME% 2>nul || echo Stack удален

echo.
echo Удаление секрета JWT (опционально):
echo docker secret rm jwt_secret
pause

