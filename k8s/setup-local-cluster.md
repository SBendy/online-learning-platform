# Настройка локального Kubernetes кластера

## Проблема: kubectl не может подключиться к кластеру

Если вы видите ошибку:
```
Unable to connect to the server: dial tcp [::1]:8080: connectex: No connection could be made
```

Это означает, что Kubernetes кластер не запущен или kubectl не настроен.

## Решения

### Вариант 1: Использовать Minikube (Рекомендуется для Windows)

#### Установка Minikube:
1. Скачайте Minikube: https://minikube.sigs.k8s.io/docs/start/
2. Или через Chocolatey:
```powershell
choco install minikube
```

#### Запуск:
```bash
# Запустить minikube
minikube start

# Проверить статус
minikube status

# Настроить kubectl
kubectl config use-context minikube
```

#### Проверка:
```bash
kubectl get nodes
kubectl get pods --all-namespaces
```

### Вариант 2: Использовать Docker Desktop Kubernetes

1. Откройте Docker Desktop
2. Перейдите в Settings → Kubernetes
3. Включите "Enable Kubernetes"
4. Нажмите "Apply & Restart"
5. Дождитесь запуска Kubernetes

#### Проверка:
```bash
kubectl config get-contexts
kubectl get nodes
```

### Вариант 3: Использовать Kind (Kubernetes in Docker)

#### Установка:
```bash
# Windows (через Chocolatey)
choco install kind

# Или скачайте с https://kind.sigs.k8s.io/docs/user/quick-start/
```

#### Создание кластера:
```bash
kind create cluster --name learning-platform

# Проверка
kubectl cluster-info --context kind-learning-platform
```

### Вариант 4: Использовать Docker Compose (Без Kubernetes)

Если вы не хотите использовать Kubernetes, просто используйте Docker Compose:

```bash
docker-compose up --build
```

Это проще и не требует настройки Kubernetes кластера.

## Проверка подключения

После настройки кластера проверьте:

```bash
# Проверить текущий контекст
kubectl config current-context

# Проверить узлы
kubectl get nodes

# Проверить все поды
kubectl get pods --all-namespaces
```

## Развертывание после настройки кластера

После того как кластер запущен:

```bash
cd k8s
./deploy.sh

# Или вручную
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f persistent-volumes.yaml
kubectl apply -f auth-service-deployment.yaml
kubectl apply -f course-service-deployment.yaml
kubectl apply -f learning-service-deployment.yaml
kubectl apply -f api-gateway-deployment.yaml
kubectl apply -f frontend-service-deployment.yaml
```

## Troubleshooting

### Проблема: kubectl показывает неправильный контекст

```bash
# Посмотреть все контексты
kubectl config get-contexts

# Переключиться на нужный
kubectl config use-context <context-name>
```

### Проблема: Minikube не запускается

```bash
# Удалить и пересоздать
minikube delete
minikube start

# С драйвером Docker (если доступен)
minikube start --driver=docker
```

### Проблема: Docker Desktop Kubernetes не работает

1. Перезапустите Docker Desktop
2. Проверьте, что Docker работает: `docker ps`
3. Включите Kubernetes в настройках заново

