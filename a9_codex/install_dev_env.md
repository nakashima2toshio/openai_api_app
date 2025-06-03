対処まとめ

1. Node.jsバージョンアップ (v22以上)
公式 から最新版をダウンロード
または nvm を利用してアップグレード
```bash
nvm install 22
nvm use 22
node -v  # v22.x.xになること確認
```

2. npmアップグレード
```bash
npm install -g npm@latest
```
3. 権限エラー対応 (EACCES)
グローバルインストールにはsudoが必要 (ただしnvm使用なら不要)
nvmを使っているなら、そのまま npm i -g @openai/codex
それ以外は sudo で：
```bash
sudo npm i -g @openai/codex
```
例: nvmで最新nodeにしてcodexインストール
```bash
nvm install 22
nvm use 22
npm install -g npm@latest
npm i -g @openai/codex
```

参考：nvmインストール（未導入の場合）
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
# いったんターミナル再起動 or
source ~/.nvm/nvm.sh
```
解説
Node.js本体のバージョンを必ず22以上に
権限エラーはnvm利用で原則出ません
既存Nodeがシステムグローバルならsudo要

