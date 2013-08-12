# LogCAS

## はじめに

このツールは OpenStack 各コンポーネント用のログ収集・解析システムです。
本ツールを使用する事で障害発生時のログ解析作業が迅速に行えるようになり、
原因究明の工数を削減する事が出来ます。

LogCAS は Log Collecting and Analyzing System for OpenStack の略ですが、
略称ではつまらないので OpenStack の各コンポーネントのように良い名前を募
集中です。


## 主要機能

LogCAS には以下の機能があります。

* ログ一覧：OpenStack のログを時系列に一覧表示
* ログ詳細：１つのログの詳細情報を表示
* リクエスト一覧：OpenStack のログをユーザリクエストID単位で一覧表示
* リクエスト詳細：同一リクエストIDの一連のログを一覧表示
* アーカイブ機能：WARNING 以上のログとその時刻に処理中だったユーザ操作
  関連ログを MongoDB の同一データベース上の別コレクション(SQL DBのテー
  ブルのようなもの）にコピー

各一覧機能には以下の機能があります。

* ページャ: １画面辺りの表示件数を指定し、ページ間を移動
* 時刻フィルタ：特定の時刻の前後一定時間(デフォルトは10秒)のログのみ表示
* ホストフィルタ：特定のホストのログ一覧のみ表示
* ログレベルフィルタ：表示するログの最低レベルを指定
* テーマセレクタ：画面の配色を選択


## スクリーンショット

https://github.com/yosshy/logcas/tree/master/screenshots を参照して下さ
い。


## 基本構成

LogCAS はOpenStack コンポーネントのログファイルをFluentd 又は LogCabin
によって MongoDB に保存し、それを Flask の Web アプリケーションで表示す
るという構成になっています。

Fluentd と LogCabin は併用可能ではありますが、通常はいずれかしか使用し
ません。個人的には、各ログのタイムスタンプをログサーバ上のタイムスタン
プで上書き出来る LogCabin をおすすめします（制限事項あり）。

* MongoDB: http://www.mongodb.org/
* Fluentd: http://fluentd.org/
* LogCabin: https://github.com/artirix/logcabin
* Flask: http://flask.pocoo.org/
* PyMongo：http://api.mongodb.org/python/current/
* Flask-PyMongo: http://flask-pymongo.readthedocs.org/
* Flask-WTF: http://pythonhosted.org/Flask-WTF/
* Flask-Testing: http://pythonhosted.org/Flask-Testing/


## インストールと設定

### LogCAS WebAP サーバ

LogCAS の WebAP は基本的に Flask アプリケーションですので、Flask と
Flask-WTF, Flask-PyMongo パッケージをインストールします。ユニットテスト
を実施する場合には Flask-Testing、blinker もインストールする必要があり
ます。

```
# sudo pip install Flask
# sudo pip install Flask-PyMongo
# sudo pip install Flask-WTF
```

現時点では LogCAS 自身に特別なインストーラはありません。tar.gz ファイル
の場合は tarで、ZIP ファイルの場合は unzip コマンド等でファイルを解凍し、
適当なディレクトリ下に移動させて下さい。

ディレクトリ構成

```
logcas/
    + app.py : プログラム本体
    + static/ : Web 静的コンテンツディレクトリ
    |    \ *.css : Web スタイルシート群
    \ templates/ : Web テンプレートディレクトリ
         \ *.html : Web テンプレート群
```

app.py 中に MongoDB の設定を行う箇所がありますので、お使いの MongoDB に
合わせて設定を行なって下さい。

```
MONGO_DBNAME = 'logcas'
MONGO_HOST = 'localhost'
MONGO_PORT = '27017'
MONGO_USERNAME = 'foo'
MONGO_PASSWORD = 'bar'
```

設定が終わったら、app.py を実行して下さい。

```
# python logcas/app.py
```

### ログサーバ

ログサーバにMongoDB をインストールします(別ホストの MongoDB も使用可能
です)。詳しくは
http://docs.mongodb.org/manual/tutorial/install-mongodb-on-linux/ を参
照して下さい。

Fluentd の場合、ログ用コレクションの作成オプションに capped を選択出来
ます。Capped コレクションとは一種のリングバッファで、コレクション（SQL
DB におけるレコード）が指定されたサイズを超えると一番古いコレクションか
ら破棄します。これによりログのサイズ管理から開放されます。

現時点では LogCabin に同様のオプションはないため、手作業で capped コレ
クションを作成して下さい。これをしないとログ用コレクションが通常のコレ
クションとして作成され、データベースファイルが際限なく肥大化します。

Capped コレクション作成例：

```
# mongo
MongoDB shell version: 2.4.5
connecting to: test
> use logcas
switched to db logcas
> db.createCollection('logs', {size: 742203392, capped: true })
{ "ok" : 1 }
```

上記のサイズはバイト単位です。アーカイバを使うのであれば、マシンのメモ
リ容量より少ないサイズにしてディスクI/O負荷を下げた方が良いでしょう。

* Fluentd を使用する場合

  Fluentd をインストールして下さい。細かい手順は Fluentd のドキュメント
  を参照して下さい。

* LogCabin を使用する場合

  LogCabin をインストールします。

  ```
  # sudo pip install logcabin
  ```

  logcas/tools/logcabin/mongosaver.py を適当なディレクトリにインストー
  ルし、以下の設定を編集します。

  ```
  Mongodb(database='logcas', collection='logs')`
  ```

  設定の詳細は
  http://logcabin.readthedocs.org/en/latest/outputs.html#module-logcabin.outputs.mongodb
  にあります。
  設定が終わったら LogCabin を実行します。

  ```
  # logcabin -c mongosaver.py &
  ```

アーカイバを使う場合は、logcas/tools/archiver/archiver.py の設定を
WebAP と同様に行い、cron やシェルスクリプト等で一定時間単位で実行するよ
うにします。


### OpenStack 各サーバ

WebAP サーバと同様に LogCAS のファイルを展開し、logcas/logger 配下を
Python のパスが通っている場所に配置して下さい。
/usr/local/lib/python2.7/dist-packages/logcas/logger 辺りが良いと思いま
す。但し、__init__.py ファイルが必要ですので注意して下さい。

ディレクトリ構成例
```
/usr/local/lib/python2.7/dist-packages/logcas/
    + __init__.py … 空ファイル
    \logger/
        + __init__.py … 空ファイル
        + fluent_logger.py …Fluentd 用 Python ロギングハンドラ
        \ zmq_logger.py …LogCabin 用 Python ロギングハンドラ
```

次に、logcas/logger/etc_nova_logging.conf を /etc/nova/logging.conf に
コピーし、必要な箇所を修正して下さい。

* Fluentd を使用する場合

  ```
  [loggers]
  keys = root, fluent

  [handler_fluent]
  class = logcas.logger.fluent_logger.FluentHandler
  # (カテゴリ名, ログサーバ名, ポート番号)
  args = ('app.nova', 'logserver.example.com', 24224)
  ```
  
* LogCabin を使用する場合

  ```
  [loggers]
  keys = root, zmq

  [handler_zmq]
  class = logcas.logger.zmq_logger.ZmqHandler
  # (ログサーバの ZeroMQ URL,)
  # () 最後の, に注意！
  args = ('tcp://localhost:2120',)
  ```
    
次に、これらが依存するパッケージやモジュールをインストールして下さい。
使用する方のみで結構です。

* Fluentd 用ロギングハンドラ

  fluent-logger (https://github.com/fluent/fluent-logger-python) に依存
  しています。これを pip でインストールすると、環境によっては kombu パッ
  ケージケージが古くて nova 各サービスが起動しなくなります。この場合、
  kombu を最新版に更新して下さい。
  
  ```
  # sudo apt-get install python-pip python-dev build-essential
  # sudo pip install fluent-logger
  # sudo pip install -U kombu
  ```
  
* LogCabin 用ロギングハンドラ

  pyzmq に依存していますが、これが最新の distribute や gevent を要求し
  ます。一緒にインストールして下さい。

  ```
  # sudo apt-get install python-pip python-dev build-essential \
                          libzmq-dev libevent-dev
  # sudo pip install -U distribute
  # sudo pip install gevent
  # sudo pip install pyzmq
  ```
  
設定が終わったら、nova サービスを実行します。まずはコマンドラインで試し
てみて、正常に動作するか確認します。

```
# sudo nova-scheduler
```

LogCabin の場合、ZeroMQ の fork() 関連バグが原因で nova-api の実行に失
敗します。仕方ないので、nova-api-os-compute やnova-api-metadata 等を使
用して下さい。

正常に動作したら service コマンドで nova サービスを再起動して下さい。

```
# sudo service nova-scheduler start
```

## 動作確認

ログサーバ上で mongo コマンドを実行し、当該データベース上にログがあるか
調べます。

```
# mongo
MongoDB shell version: 2.4.5
connecting to: test
> show dbs
local   0.078125GB
logcas  4.451171875GB
test    0.203125GB
> use logcas
switched to db logcas
> db.logs.find().count()
770
```

## 使用法

Web ブラウザで http://WebAPサーバ:5000/ にアクセスしてみます。

タイトルの下にタブがあります。左から順に以下のようになっています。

* Requests: ユーザリクエスト毎のログ一覧
* Logs: ログ一覧
* Requests(Archived): アーカイブされたユーザリクエスト毎のログ一覧
* Logs(Archived): アーカイブされたログ一覧

※アーカイバを動かしていない限り、(Archived) のタブにはログが表示されま
せん。

### ページャ、ログレベルフィルタ

タブの下には１ページ辺りの表示件数と、表示するログの最低レベルを指定す
る為のフォームがあります。これらを設定したら送信ボタンを押します。

ログ件数が１ページに収まらない場合、上記フォームの直下とページの最下部
にページ番号を指定する為のリンクが表示されます。現在のページの前後9ペー
ジと、最初と最後のページ、10ページ前／後のページ用のリンクがページ数に
応じて表示されます。

### リクエスト詳細

ログ一覧中の各リクエストIDにはリンクが設定されており、クリックすると当
該リクエストIDを持つ一連のログが一覧表示されます。

### 時刻フィルタ

ログ一覧表示中の時刻にはリンクが設定されており、クリックするとその時刻
の前後一定時間（デフォルトでは 10秒）のログが表示されます。この場合のみ
画面上部のフォーム部分に前後の時間範囲を秒数で指定する為のテキストフォー
ムが表示されます。

### ホストフィルタ

ログ一覧表示とリクエスト詳細一覧表示中のホスト名にはリンクが設定されて
おり、クリックすると当該ホストのログのみ一覧表示します。

### テーマセレクタ

画面右上にプルダウン型のフォームがあり、これを選択して「送信」ボタンを
押すと画面の配色等が変更されます。

## ライセンス

Apache License ver.2.0
