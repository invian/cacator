<p align="center">
  <img width="460" height="300" src="https://github.com/invian/cacator/assets/33404130/21d106b0-e15c-4bef-8395-1c825f0e6643">
</p>

<p align="center">
  <img alt="Tests" src="https://img.shields.io/github/actions/workflow/status/invian/invian/main.yml?style=for-the-badge&label=Tests">
  <img alt="GitHub" src="https://img.shields.io/github/license/invian/cacator?color=brown&style=for-the-badge">
  <a href="https://github.com/facebookarchive/WEASEL"><img alt="KUDOS" src="https://img.shields.io/badge/kudos-weasel-brown?style=for-the-badge"></a>
  <img alt="Code style" src="https://img.shields.io/badge/code%20style-black-black?style=for-the-badge">
</p>

# Cacator

Cacator (с лат. — "засранец"). Маячок для выявления несанкционированных копий нашего ПО. Работает через DNS covert channels.

Проект является глубокой переработкой [WEASEL](https://github.com/facebookarchive/WEASEL).

## evwsync

> "Just a weather synchronizer"

Пакет-клиент, который устанавливается в продукт и запускается из него. В него передается фактори для данных, которые будут отправляться и адреса серверов в base64:

```python
from evwsync import WeatherSynchronizer


WeatherSynchronizer(
  lambda: {"my_heart", "beating"},
  servers: ["ZXhhbXBsZS5vcmc="]
)
```

Клиент сначала проведет обмен Диффи-Хэлмана с сервером, а потом начнет слать данные.

## server

Wannabe-DNS-server, с которым соединяется клиент и начинает слать данные. 

Потенциально при правильной доработке, может стать контрольным центром для RCE. Но нам это было не надо. Реализацию такого механизма можно посмотреть здесь: [WEASEL](https://github.com/facebookarchive/WEASEL).

Получает пакеты в виде домена с шифром в сабдомене (e.g. `somereandomcryptobase64==@example.org`) и отвечает серией IP адресов, шифруя инфу в их октетах. Канал связи энкриптится через DHE. 
