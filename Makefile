# ------------------
# Makefile for Development
# ------------------

# .PHONY宣言: 実際のファイル/ディレクトリとタスク名が重複した場合に、
# タスクの方を優先することを明示します
.PHONY: up down restart logs ps clean rebuild update-deps restart-streamlit help

# デフォルトのターゲット: makeコマンドを引数なしで実行した時の動作を定義
# helpコマンドを実行して使用可能なコマンド一覧を表示します
.DEFAULT_GOAL := help

# ------------------
# Docker 基本操作
# ------------------

# Dockerコンテナを起動します
up:
	@echo "Dockerfileをビルドしてコンテナを起動"
	docker compose up --build

# 実行中のコンテナを停止し、関連リソースを削除します
# コンテナ、ネットワークは削除されますが、ボリュームは維持されます
down:
	@echo "Stopping and removing containers..."
	docker-compose down

# アプリケーションコンテナのみを再起動します
# 設定変更やアプリケーションの再起動が必要な場合に使用します
restart:
	@echo "Restarting application container..."
	docker-compose restart app

# ------------------
# 状態確認
# ------------------

# 実行中のコンテナの状態を表示します
# コンテナ名、ステータス、ポートなどの情報が確認できます
ps:
	@echo "Showing container status..."
	docker-compose ps

# ------------------
# クリーンアップと再構築
# ------------------

# 全てのDocker関連リソースを削除します
# -v: 名前付きボリュームも削除
# --rmi all: 全てのイメージを削除
clean:
	@echo "Cleaning up all Docker resources..."
	docker-compose down -v --rmi all

# イメージを完全に再構築します
# --no-cache: ビルドキャッシュを使用しない（完全なクリーンビルド）
rebuild:
	@echo "Rebuilding images from scratch..."
	docker-compose build --no-cache

# ------------------
# 依存関係管理
# ------------------

# requirements.txtの変更を既存のコンテナに反映します
# execを使用してコンテナ内でpip installを実行
update-deps:
	@echo "Updating Python dependencies..."
	docker-compose exec app pip install -r requirements.txt

# ------------------
# ヘルプ
# ------------------

# 利用可能なコマンドの一覧と説明を表示します
# @記号: コマンド自体を出力しない
# %-20s: 左寄せで20文字分のスペースを確保
help:
	@echo "利用可能なコマンドの一覧と説明を表示します:"
	@echo "  make up               - コンテナ＆アプリを立ち上げます"
	@echo "  make down             - コンテナを停止し、関連リソースを削除します" 
	@echo "  make restart          - アプリを再起動します"
	@echo ""
	@echo "status:"
	@echo "  make ps               - 実行中のコンテナの状態を表示します"
	@echo ""
	@echo "Cleanup and rebuild:"
	@echo "  make clean            - 全てのDocker関連リソースを削除します"
	@echo "  make rebuild          - イメージを完全に再構築します"
	@echo ""
	@echo "Development commands:"
	@echo "  make update-deps      - requirements.txtの変更を既存のコンテナに反映します"