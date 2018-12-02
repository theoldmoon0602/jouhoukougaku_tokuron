# 情報工学特論

のやつ

- server.py   server部分です
- simulator.exe  release をみて
- learner_example.py  学習プログラムサンプル
- q_example.py  サンプルAgent
- random_example.py Randomに学習するAgent
- battle_example.py 学習せず戦わせるだけのプログラム 


## 使い方

サーバ準備

```
$ python server.py localhost 8000 simulator/simulator.exe
```

1. 学習する（larner_example)

 勝手に10エピソードくらい回ります。回ったあと学習したデータのjsonを吐く。

```
$ python learner_example.py localhost 8000
```

 q_example.py のAgentを使ってます。q_example.pyのAgentをまねして独自Agentを作るといい感じになりそう

2. randomを動かす

 random agent を動かす場合は 4つ動かしてね

```
$ python random_example.py localhost 8000
```

3. viewer を動かす

viewer プロトコルを実装した上で、サーバにつなぐとOK
