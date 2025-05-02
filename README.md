# bamboo麻雀 🎋

ソーズ牌のみを使用した、2人対戦型の簡易麻雀アプリです。  
シンプルで高速な対戦を楽しめるよう設計されています。

---

## 🚩 ルール概要

| 項目               | 内容                          |
|--------------------|-------------------------------|
| プレイヤー数       | 2人                           |
| 使用牌             | ソーズ（1〜9）× 各4枚 = 36枚 |
| 配牌               | 各プレイヤー13枚              |
| リーチ             | 可能（0点、リーチ棒なし）     |
| 点数設定           | 5万点持ちスタート             |
| 終了条件           | どちらかの飛び（0点以下）まで |
| 親ルール           | 親の和了で連荘、流局で流れ   |
| ドラ               | なし                          |
| 鳴き               | なし（ポン・チー・カン）      |
| 積み棒・供託・罰符 | なし                          |

---

## 📁 リポジトリ構造

bamboo
├── bamboo_cli.py（CLIによるテストプレイ）
├── requirements.txt
├── src
│ ├── bamboo_core（ゲームロジック）
│ │ ├── game.py
│ │ ├── player.py
│ │ └── utils.py
│ ├── client.py（クライアントWebSocket処理）
│ └── server.py（サーバーWebSocket処理、FastAPI）

yaml
コピーする
編集する

---

## 🛠 使用技術スタック

- Python 3.10+
- FastAPI（WebSocket通信）
- Redis（Pub/Subによるゲーム状態管理）
- Uvicorn（サーバー起動用）
- WebSockets（クライアント・サーバー間通信）

---

## 🚀 開発・実行方法

### 依存関係のインストール
```bash
pip install -r requirements.txt
ローカル起動方法
サーバー起動

bash
コピーする
編集する
uvicorn src.server:app --reload
クライアント起動

bash
コピーする
編集する
python src/client.py
CLIテストプレイ
bash
コピーする
編集する
python bamboo_cli.py
🧩 開発ロードマップ
 ゲームロジック（配牌・ツモ・アガリ判定）

 WebSocketによる通信対戦機能

 Redis導入によるゲーム状態管理

 フロントエンドとの連携（任意）