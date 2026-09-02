#!/usr/bin/env python3
"""
SPSS Modeler clemb.exe を実行するMCPサーバー
"""
import asyncio
import subprocess
import functools
import json
import sys
import os
from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent
from .config import get_config

# MCPサーバーのインスタンスを作成
app = Server("spss-modeler-clemb")


def _get_server_config(arguments: dict, config) -> dict:
    """サーバー設定を取得する共通ヘルパー関数

    Args:
        arguments: ツールの引数辞書
        config: 設定オブジェクト

    Returns:
        サーバー設定を含む辞書
    """
    return config.get_server_config(
        hostname=arguments.get("hostname"),
        port=arguments.get("port"),
        username=arguments.get("username"),
        password=arguments.get("password"),
        server_directory=arguments.get("server_directory")
    )


@app.list_tools()
async def list_tools() -> list[Tool]:
    """利用可能なツールのリストを返す"""
    return [
        Tool(
            name="execute_clemb",
            description="SPSS Modelerのclemb.exeを実行します。ストリームファイル、スクリプト、またはその両方を実行できます",
            inputSchema={
                "type": "object",
                "properties": {
                    "stream_file": {
                        "type": "string",
                        "description": "実行するSPSS Modelerストリームファイル(.str)のパス（オプション）"
                    },
                    "script": {
                        "type": "string",
                        "description": "実行するSPSS Modelerスクリプト（オプション）。script_fileと同時に指定できません"
                    },
                    "script_file": {
                        "type": "string",
                        "description": "実行するSPSS Modelerスクリプトファイル(.py)のパス（オプション）。scriptと同時に指定できません"
                    },
                    "hostname": {
                        "type": "string",
                        "description": "SPSS Modelerサーバーのホスト名（オプション）。指定するとサーバーモードで実行されます"
                    },
                    "port": {
                        "type": "integer",
                        "description": "SPSS Modelerサーバーのポート番号（オプション）"
                    },
                    "username": {
                        "type": "string",
                        "description": "SPSS Modelerサーバーのユーザー名（オプション）"
                    },
                    "password": {
                        "type": "string",
                        "description": "SPSS Modelerサーバーのパスワード（オプション）"
                    },
                    "server_directory": {
                        "type": "string",
                        "description": "SPSS Modelerサーバーのデータディレクトリ（オプション）。サーバーモードでのデータファイルの場所を指定します"
                    },
                    "parameters": {
                        "type": "object",
                        "description": "ストリームまたはスクリプトに渡す追加パラメータ（オプション）",
                        "additionalProperties": {"type": "string"}
                    },
                    "working_directory": {
                        "type": "string",
                        "description": "作業ディレクトリ（オプション）"
                    },
                    "log_file": {
                        "type": "string",
                        "description": "ログファイルのパス（オプション）。指定すると-logオプションでログを出力します"
                    }
                },
                "required": []
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """ツールを実行する"""

    if name == "execute_clemb":
        return await execute_clemb(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")


async def execute_clemb(arguments: dict) -> list[TextContent]:
    """clemb.exeを実行（ストリーム、スクリプト、またはその両方）"""
    config = get_config()

    # パラメータ取得
    stream_file = arguments.get("stream_file")
    script = arguments.get("script")
    script_file_path = arguments.get("script_file")
    parameters = arguments.get("parameters", {})
    log_file = arguments.get("log_file")

    # working_directoryの決定
    working_directory = arguments.get("working_directory")

    # ローカル実行時かつstream_fileが指定されている場合、
    # working_directoryが未指定ならstream_fileのディレクトリを使用
    if not working_directory and stream_file and not arguments.get("hostname"):
        if os.path.isabs(stream_file):
            # 絶対パスの場合
            working_directory = os.path.dirname(stream_file)
        else:
            # 相対パスの場合、絶対パス化してからディレクトリを取得
            abs_stream_path = os.path.abspath(stream_file)
            working_directory = os.path.dirname(abs_stream_path)

    # それでもNoneの場合はデフォルト値を使用
    if not working_directory:
        working_directory = config.default_working_directory

    # パラメータ検証
    if not (stream_file or script or script_file_path):
        return [TextContent(
            type="text",
            text="Error: At least one of 'stream_file', 'script', or 'script_file' must be provided"
        )]

    if script and script_file_path:
        return [TextContent(
            type="text",
            text="Error: 'script' and 'script_file' cannot be specified at the same time"
        )]

    # サーバー設定を取得
    server_config = _get_server_config(arguments, config)
    hostname = server_config["hostname"]
    port = server_config["port"]
    username = server_config["username"]
    password = server_config["password"]
    server_directory = server_config["server_directory"]

    # 一時ファイル管理
    use_temp_file = False
    actual_script_file = None

    # スクリプト処理
    if script:
        # インラインスクリプトの場合は一時ファイルを作成
        import tempfile
        try:
            if working_directory and os.path.exists(working_directory):
                temp_dir = working_directory
            else:
                temp_dir = None

            # スクリプトの先頭にパラメータ定義を追加
            script_with_params = ""
            for key, value in parameters.items():
                script_with_params += f'{key} = u"{value}"\n'
            if script_with_params:
                script_with_params += "\n"
            script_with_params += script

            temp_file = tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.py',
                delete=False,
                encoding='utf-8',
                dir=temp_dir
            )
            temp_file.write(script_with_params)
            temp_file.flush()
            actual_script_file = temp_file.name
            temp_file.close()
            use_temp_file = True
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error creating temporary script file: {str(e)}"
            )]
    elif script_file_path:
        # スクリプトファイルの存在確認
        if os.path.isabs(script_file_path):
            check_path = script_file_path
        else:
            check_path = os.path.join(working_directory or os.getcwd(), script_file_path)

        if not os.path.exists(check_path):
            return [TextContent(
                type="text",
                text=f"Error: Script file not found: {script_file_path} (checked: {check_path})"
            )]

        actual_script_file = script_file_path

    # ストリームファイルのパス解決（ローカルモードの場合）
    if stream_file and not hostname:
        def _resolve_local_path(file_path: str, working_dir: str | None) -> str:
            if not os.path.isabs(file_path):
                if working_dir:
                    return os.path.abspath(os.path.join(working_dir, file_path))
                else:
                    return os.path.abspath(file_path)
            return file_path

        stream_file = _resolve_local_path(stream_file, working_directory)

    try:
        # clemb.exe を直接 subprocess で実行（スクリプトあり・なし共通）
        # PowerShell経由だと chcp 等の差異で非同期問題が再発するため直接呼び出しに統一
        cmd = [config.clemb_path]

        # サーバー接続パラメータ
        if hostname:
            cmd.extend(["-server", "-hostname", hostname])
            if port:
                cmd.extend(["-port", str(port)])
            if username:
                cmd.extend(["-username", username])
            if password:
                cmd.extend(["-password", password])
            if server_directory:
                cmd.extend(["-server_directory", server_directory])

        # ストリームファイル
        if stream_file:
            cmd.extend(["-stream", stream_file])

        # スクリプトファイル
        if actual_script_file:
            cmd.extend(["-script", actual_script_file])
        elif not stream_file:
            return [TextContent(
                type="text",
                text="Error: 'stream_file' is required when script is not provided"
            )]

        # パラメータ
        for key, value in parameters.items():
            cmd.extend(["-P", f"{key}={value}"])

        # 実行
        cmd.append("-execute")

        # ログファイル
        if log_file:
            cmd.extend(["-log", log_file])

        env = os.environ.copy()
        env['JAVA_TOOL_OPTIONS'] = '-Dfile.encoding=UTF-8 -Dclient.encoding.override=UTF-8 -Dsun.jnu.encoding=UTF-8'
        env['PYTHONIOENCODING'] = 'utf-8'

        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            None,
            functools.partial(
                subprocess.run,
                cmd,
                cwd=working_directory,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=config.default_timeout,
                env=env,
            )
        )

        cmd_str = " ".join(f'"{c}"' if " " in c else c for c in cmd)
        output = f"Exit Code: {result.returncode}\n\n"
        output += f"=== COMMAND ===\n{cmd_str}\n\n"
        output += "=== STDOUT ===\n"
        output += (result.stdout if result.stdout else "(empty)") + "\n"
        output += "\n=== STDERR ===\n"
        output += (result.stderr if result.stderr else "(empty)") + "\n"

        # ログファイルの内容を追加
        if log_file:
            log_path = log_file if os.path.isabs(log_file) else os.path.join(working_directory or os.getcwd(), log_file)
            if os.path.exists(log_path):
                try:
                    with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
                        log_content = f.read()
                    output += f"\n=== LOG FILE ({log_file}) ===\n"
                    output += log_content if log_content else "(empty)\n"
                except Exception as e:
                    output += f"\n=== LOG FILE ({log_file}) ===\n"
                    output += f"Error reading log file: {str(e)}\n"
            else:
                output += f"\n=== LOG FILE ({log_file}) ===\n"
                output += "Log file not found\n"

        return [TextContent(type="text", text=output)]

    except subprocess.TimeoutExpired:
        return [TextContent(
            type="text",
            text="Error: clemb.exe execution timed out after 5 minutes"
        )]
    except FileNotFoundError:
        return [TextContent(
            type="text",
            text=f"Error: clemb.exe not found at {config.clemb_path}"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error executing clemb.exe: {str(e)}"
        )]
    finally:
        # 一時ファイルを削除
        if use_temp_file and actual_script_file:
            try:
                if os.path.exists(actual_script_file):
                    os.unlink(actual_script_file)
            except OSError:
                pass


async def main():
    """サーバーを起動"""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())

# Made with Bob
