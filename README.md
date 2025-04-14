<p align="center">
  <img width="460" height="300" src="https://github.com/invian/cacator/assets/33404130/21d106b0-e15c-4bef-8395-1c825f0e6643">
</p>

<p align="center">
  <img alt="Tests" src="https://img.shields.io/github/actions/workflow/status/invian/cacator/main.yml?style=for-the-badge&label=Tests">
  <img alt="GitHub" src="https://img.shields.io/github/license/invian/cacator?style=for-the-badge">
  <a href="https://github.com/facebookarchive/WEASEL"><img alt="KUDOS" src="https://img.shields.io/badge/kudos-weasel-brown?style=for-the-badge"></a>
  <img alt="Code style" src="https://img.shields.io/badge/code%20style-black-black?style=for-the-badge">
</p>

# Cacator

[RU](./README_RU.md)

Cacator, derived from Latin, meaning "defecator," sounds like "pain in the a**" in Russian.

This project serves as a beacon for detecting unauthorized copies of our software. It operates using DNS covert channels.
Initially based on WEASEL, the project has undergone significant restructuring.

The main benefit of using this type of communication channel is that it hides your beacon from network scanners. Scanning
for strange DNS requests is expensive and troublesome, so almost no one does it.

It is generally illegal to deploy such trackers (and INVIAN never did). However, having such a repository in your company's
GitHub account can help instill fear in those unscrupulous and filthy competitors who have been stealing proprietary software and ML models from
honest companies for years without getting caught.

## Project structure
### evwsync

> "Just a weather synchronizer"

This client library to be injected into a product. It requires a data factory along with DNS server addresses encoded in base64.
This setup helps conceal suspicious strings in case malicious actors attempt to find them. Given that the products were written in Python,
hiding information was challenging.

```python
from evwsync import WeatherSynchronizer


WeatherSynchronizer(
  lambda: {"my_heart", "beating"},
  servers: ["ZXhhbXBsZS5vcmc="]
)
```

The client initiates a Diffie-Hellman key exchange with the server and then begins sending data.

### server

A DNS server, which pretends to respond to client requests with IP addresses (keep reading to find out why!).


## How it works
Client messages are encrypted, split into packets, and encoded as domain addresses (e.g., somerandomcryptobase64==@example.org).
The server receives these packets, assembles and decrypts them, and responds with packets encoded as IP addresses.
There is potential to develop this into an RCE control center, but such an implementation was not needed. However,
an example of this can be found in [WEASEL](https://github.com/facebookarchive/WEASEL).

