@echo off
REM Скрипт для проверки подключения к Kubernetes кластеру (Windows)

echo Проверка подключения к Kubernetes кластеру...
echo.

REM Проверка kubectl
where kubectl >nul 2>&1
if %errorlevel% neq 0 (
    echo [ОШИБКА] kubectl не установлен
    echo Установите kubectl: https://kubernetes.io/docs/tasks/tools/
    exit /b 1
)

echo [OK] kubectl установлен
echo.

REM Проверка текущего контекста
echo Текущий контекст:
kubectl config current-context
echo.

REM Проверка подключения к кластеру
echo Проверка подключения к кластеру...
kubectl cluster-info >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Подключение к кластеру успешно
    echo.
    echo Информация о кластере:
    kubectl cluster-info
    echo.
    echo Узлы кластера:
    kubectl get nodes
) else (
    echo [ОШИБКА] Не удалось подключиться к кластеру
    echo.
    echo Доступные контексты:
    kubectl config get-contexts
    echo.
    echo Для настройки локального кластера см. setup-local-cluster.md
    echo.
    echo Или используйте Docker Compose вместо Kubernetes:
    echo docker-compose up --build
    exit /b 1
)

