# Swaps_helper
Параметры в settings.json

- **DecryptType** - Метод чем шифровали приватники. Параметры: Flash | Password
- **0xKey** - ключ от https://0x.org/
- **TaskNumber** - Пока что 2 варианта: 1 (основной), 11 (шифрование приватников)
- **TaskSleep** - мин\макс время сна после каждого выполненного действия
- **SwapsAmount** - мин\макс кол-во свопов которые будут рандомно сделаны

Самое интересное, настройка "TOKENS". Сюда указываются токены которые будут обмениваться в каждой сети. Примером уже я указал токены для 2х сетей
~~~python
 "TOKENS": {
            "arbitrum": {
                "USDT" : "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9",
                "USDC" : "0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8",
                "DAI"  : "0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1",
                "WETH" : "0x82af49447d8a07e3bd95bd0d56f35241523fbab1"
            },
            "polygon": {
                "USDT" : "0xc2132D05D31c914a87C6611C10748AEb04B58e8F",
                "DAI"  : "0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063",
                "UNI"  : "0xb33eaad8d922b1083446dc23f610c2567fb5180f",
                "STG"  : "0x2F6F07CDcf3588944Bf4C42aC74ff24bF56e7590",
                "USDC" : "0x2791bca1f2de4661ed88a30c99a7a9449aa84174"
            }
        }

~~~
