##### pip install git+https://github.com/Codium-ai/cover-agent.git
#### Cover-Agent (TestGen‑LLM代替) のインストールと実行
##### 3.1 pipによるインストール
```bash
pip install git+https://github.com/Codium-ai/cover-agent.git
```
最も簡単な方法です
DEV Community

##### 3.2 Poetryによるセットアップ（ソースから実行する場合）
```bash
git clone https://github.com/Codium-ai/cover-agent.git
cd cover-agent
poetry install
```
Poetry管理の依存解決を利用できます

3.3 CLI実行例
```bash
cover-agent \
  --source-file-path "app.py" \
  --test-file-path "tests/test_app.py" \
  --code-coverage-report-path "coverage.xml" \
  --test-command "pytest --cov=. --cov-report=xml" \
  --test-command-dir "." \
  --coverage-type "cobertura" \
  --desired-coverage 80 \
  --max-iterations 3 \
  --openai-model "gpt-4o"
```
##### 4. Dockerコンテナでの実行（オプション）
Qodo Coverリポジトリには Dockerfile が用意されており、コンテナ内でCover-Agentをビルド・実行可能です。

dockerfile
```bash
FROM python:3.12-bullseye
WORKDIR /app
COPY . .
RUN poetry install
CMD ["make", "installer"]
```
