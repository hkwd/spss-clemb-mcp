#!/usr/bin/env python3
"""
設定ファイルの読み込みと管理
"""
import json
import os
from typing import Optional, Dict, Any
from pathlib import Path


class Config:
    """設定管理クラス"""

    def __init__(self):
        self.clemb_path: str = r"C:\Program Files\IBM\SPSS\Modeler\19.0\bin\clemb.exe"
        self.server_hostname: Optional[str] = None
        self.server_port: Optional[int] = None
        self.server_username: Optional[str] = None
        self.server_password: Optional[str] = None
        self.server_directory: Optional[str] = None
        self.default_timeout: int = 300
        self.default_working_directory: Optional[str] = None

        self._load_config()

    def _load_config(self):
        """設定ファイルと環境変数から設定を読み込む"""
        # 1. 設定ファイルから読み込み
        config_paths = [
            Path("config.json"),  # カレントディレクトリ
            Path(__file__).parent.parent / "config.json",  # プロジェクトルート
            Path.home() / ".spss-modeler-clemb" / "config.json",  # ホームディレクトリ
        ]

        for config_path in config_paths:
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                        self._apply_config(config_data)
                        break
                except Exception as e:
                    print(f"Warning: Failed to load config from {config_path}: {e}")

        # 2. 環境変数から読み込み（設定ファイルより優先）
        self._load_from_env()

    def _apply_config(self, config_data: Dict[str, Any]):
        """設定データを適用"""
        if "clemb_path" in config_data:
            self.clemb_path = config_data["clemb_path"]

        if "server" in config_data:
            server = config_data["server"]
            if "hostname" in server and server["hostname"]:
                self.server_hostname = server["hostname"]
            if "port" in server and server["port"]:
                self.server_port = server["port"]
            if "username" in server and server["username"]:
                self.server_username = server["username"]
            if "password" in server and server["password"]:
                self.server_password = server["password"]
            if "server_directory" in server and server["server_directory"]:
                self.server_directory = server["server_directory"]

        if "defaults" in config_data:
            defaults = config_data["defaults"]
            if "timeout" in defaults:
                self.default_timeout = defaults["timeout"]
            if "working_directory" in defaults and defaults["working_directory"]:
                self.default_working_directory = defaults["working_directory"]

    def _load_from_env(self):
        """環境変数から設定を読み込む"""
        clemb_path = os.getenv("SPSS_MODELER_CLEMB_PATH")
        if clemb_path:
            self.clemb_path = clemb_path

        hostname = os.getenv("SPSS_MODELER_SERVER_HOSTNAME")
        if hostname:
            self.server_hostname = hostname

        port_str = os.getenv("SPSS_MODELER_SERVER_PORT")
        if port_str:
            try:
                self.server_port = int(port_str)
            except ValueError:
                pass

        username = os.getenv("SPSS_MODELER_SERVER_USERNAME")
        if username:
            self.server_username = username

        password = os.getenv("SPSS_MODELER_SERVER_PASSWORD")
        if password:
            self.server_password = password

        server_dir = os.getenv("SPSS_MODELER_SERVER_DIRECTORY")
        if server_dir:
            self.server_directory = server_dir

        timeout_str = os.getenv("SPSS_MODELER_DEFAULT_TIMEOUT")
        if timeout_str:
            try:
                self.default_timeout = int(timeout_str)
            except ValueError:
                pass

        working_dir = os.getenv("SPSS_MODELER_DEFAULT_WORKING_DIRECTORY")
        if working_dir:
            self.default_working_directory = working_dir

    def get_server_config(self,
                          hostname: Optional[str] = None,
                          port: Optional[int] = None,
                          username: Optional[str] = None,
                          password: Optional[str] = None,
                          server_directory: Optional[str] = None) -> Dict[str, Any]:
        """
        サーバー設定を取得（引数で指定された値が優先）

        Args:
            hostname: ホスト名（指定された場合は設定ファイルより優先）
            port: ポート番号（指定された場合は設定ファイルより優先）
            username: ユーザー名（指定された場合は設定ファイルより優先）
            password: パスワード（指定された場合は設定ファイルより優先）
            server_directory: サーバーディレクトリ（指定された場合は設定ファイルより優先）

        Returns:
            サーバー設定の辞書
        """
        # 空文字列が明示的に渡された場合はNoneとして扱う（ローカルモードを強制）
        final_hostname = None if hostname == "" else (hostname if hostname is not None else self.server_hostname)
        final_username = None if username == "" else (username if username is not None else self.server_username)
        final_password = None if password == "" else (password if password is not None else self.server_password)
        final_server_directory = None if server_directory == "" else (server_directory if server_directory is not None else self.server_directory)

        return {
            "hostname": final_hostname,
            "port": port if port is not None else self.server_port,
            "username": final_username,
            "password": final_password,
            "server_directory": final_server_directory,
        }


# グローバル設定インスタンス
_config: Optional[Config] = None


def get_config() -> Config:
    """設定インスタンスを取得"""
    global _config
    if _config is None:
        _config = Config()
    return _config

# Made with Bob
