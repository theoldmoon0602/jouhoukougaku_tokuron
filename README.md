# 情報工学特論

のやつ

- server.py   server部分です
- simulator   simulatorです。server.pyと一緒に使う。D言語製
- client\_example.py   clientのサンプル実装です

## 使い方

```
$ python server.py localhost 8000 simulator/simulator.exe
```

としてサーバを起動した上で、

```
$ python client_example.py localhost 8000
```

とクライアントを起動します。Viewerは未対応
