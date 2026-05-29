# Git: репозиторий и правила выкладки

**Remote:** https://github.com/alexevil1979/kioskbackend  

## Обязательное правило

После **любых** правок в проекте киоска — **commit + push** в `kioskbackend`, если в diff нет чувствительных данных.

Исключения (не коммитить):

| Файл / паттерн | Причина |
|----------------|---------|
| `config/settings.yaml` | API-ключи, пароли |
| `.env` | Секреты |
| `logs/`, `*.log` | Локальные логи |
| `media/products/*` | Кэш фото |
| `.venv/` | Виртуальное окружение |

В репозитории только: `config/settings.yaml.example`, `.env.example`.

## Первичная настройка (один раз)

```powershell
cd "c:\Users\1\Documents\киоск"
git init
git remote add origin https://github.com/alexevil1979/kioskbackend.git
copy config\settings.yaml.example config\settings.yaml
# заполнить settings.yaml локально — не пушить
```

## Каждая сессия разработки

```powershell
cd "c:\Users\1\Documents\киоск"
git status
git add -A
git status   # убедиться: нет settings.yaml, .env, logs
git commit -m "Краткое описание изменений"
git push -u origin main
```

Если ветка `master`:

```powershell
git push -u origin master
```

## Проверка перед push

```powershell
git diff --cached --name-only
```

Не должно быть: `settings.yaml`, `.env`, файлов из `logs/`.

## Аутентификация GitHub

- HTTPS: Personal Access Token вместо пароля  
- или SSH: `git@github.com:alexevil1979/kioskbackend.git`
