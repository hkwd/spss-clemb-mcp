# SPSS Modeler clemb.exe MCP Server

**バージョン: 0.1**

このMCPサーバーは、SPSS Modelerの`clemb.exe`コマンドラインツールを実行するための機能を提供します。

## 注意事項

- すべてのパラメーターを網羅していません
- パラメーターの組み合わせによるテストが不足しています
- 主にスクリプト実行機能のテストを行っています

## 機能

- **execute_clemb**: SPSS Modelerストリームファイル(.str)、スクリプト、またはその両方を実行
  - ストリームのみ実行
  - スクリプトのみ実行（インラインまたはファイル）
  - ストリームとスクリプトの組み合わせ実行

## インストール

### 方法 A: インストールスクリプトを使用（推奨）

PowerShell スクリプト `install-spss-clemb-mcp.ps1` を使うと、以下の手順をすべて自動で実行できます。

**実行するもの**:
1. 前提条件チェック（Python 3.10+、Git、clemb.exe の存在確認）
2. GitHubリポジトリのクローン（既存の場合は `git pull`）
3. Python 依存パッケージのインストール（`pip install -e .`）
4. `config.json` の生成（`config.example.json` をコピーして `clemb_path` を自動設定）
5. Bob の MCP 設定ファイル（`~/.bob/settings/mcp.json`）へのサーバー登録
6. サーバー起動テスト（3秒間起動確認）

**実行方法**:

```powershell
# スクリプトをダウンロードして実行
irm https://raw.githubusercontent.com/hkwd/spss-clemb-mcp/main/install-spss-clemb-mcp.ps1 | iex
```

または、スクリプトファイルを直接実行：

```powershell
.\install-spss-clemb-mcp.ps1
```

**インストール先**:
| 項目 | パス |
|------|------|
| サーバー本体 | `%USERPROFILE%\.mcp-servers\spss-clemb-mcp` |
| MCP 設定ファイル | `%USERPROFILE%\.bob\settings\mcp.json` |
| サーバー設定ファイル | `%USERPROFILE%\.mcp-servers\spss-clemb-mcp\config.json` |

**スクリプト内の設定変更**:

スクリプト冒頭の Config セクションを編集することで、インストール先などをカスタマイズできます：

```powershell
$InstallDir = "$env:USERPROFILE\.mcp-servers\spss-clemb-mcp"  # インストール先
$McpJson    = "$env:USERPROFILE\.bob\settings\mcp.json"        # MCP設定ファイル
$ClembPath  = "C:\Program Files\IBM\SPSS\Modeler\19.0\bin\clemb.exe"  # clemb.exe パス
```

> ワークスペース単位の MCP 設定を使う場合は `$McpJson = ".bob\mcp.json"` に変更してください（スクリプト内のコメントを参照）。

**インストール完了後の次のステップ**:
1. `config.json` を編集してサーバー接続情報を設定（SPSS Modeler Server を使う場合）
2. Bob を再起動
3. MCP パネルに `spss-clemb-mcp` が表示されることを確認

---

### 方法 B: 手動インストール

### 1. プロジェクトファイルのコピー

```bash
# MCPサーバー用ディレクトリを作成
mkdir "C:\Users\<ユーザー名>\.mcp-servers"

# プロジェクトファイルをコピー
# 方法1: エクスプローラーでspss-clemb-mcpフォルダ全体をコピー
# 方法2: コマンドラインでコピー（現在のディレクトリから）
xcopy /E /I spss-clemb-mcp "C:\Users\<ユーザー名>\.mcp-servers\spss-clemb-mcp"
```

### 2. 依存パッケージのインストール

```bash
# プロジェクトディレクトリに移動
cd "C:\Users\<ユーザー名>\.mcp-servers\spss-clemb-mcp"

# 開発モードでインストール（推奨）
pip install -e .
```

### 3. MCP設定への追加

#### Bobの場合
`C:\Users\<ユーザー名>\.bob\settings\mcp_settings.json`に以下を追加：

```json
{
  "mcpServers": {
    "spss-clemb-mcp": {
      "command": "python",
      "args": ["-m", "spss_clemb_mcp.server"],
      "cwd": "C:\\Users\\<ユーザー名>\\.mcp-servers\\spss-clemb-mcp"
    }
  }
}
```

**注意**: `cwd`パスは実際のプロジェクトディレクトリに合わせて変更してください。

### 4. 動作確認

サーバーが正しく起動するか確認：

```bash
python -m spss_clemb_mcp.server
```

## 必要要件

- Python 3.10以上
- SPSS Modeler 19.0がインストールされていること
- clemb.exeのパス: `C:\Program Files\IBM\SPSS\Modeler\19.0\bin\clemb.exe`

## 設定

### 設定ファイル

サーバー接続情報やデフォルト設定を管理するために、設定ファイルを使用できます。

**設定ファイルの場所**（優先順位順）:
1. カレントディレクトリの`config.json`
2. プロジェクトルートの`config.json`
3. ホームディレクトリの`~/.spss-modeler-clemb/config.json`

**設定ファイルの作成**:
```bash
# サンプル設定ファイルをコピー
cp config.example.json config.json

# 設定を編集
# config.jsonを開いて、必要な値を設定してください
```

**設定ファイルの例** (`config.json`):
```json
{
  "clemb_path": "C:\\Program Files\\IBM\\SPSS\\Modeler\\19.0\\bin\\clemb.exe",
  "server": {
    "hostname": "myserver.example.com",
    "port": 28063,
    "username": "dminer",
    "password": "your_password_here"
  },
  "defaults": {
    "timeout": 300,
    "working_directory": "C:\\projects\\analysis"
  }
}
```

**設定項目**:
- `clemb_path`: clemb.exeの絶対パス
- `server.hostname`: SPSS Modelerサーバーのホスト名（サーバーモードで実行する場合）
- `server.port`: サーバーのポート番号（デフォルト: 28063）
- `server.username`: サーバーのユーザー名
- `server.password`: サーバーのパスワード
- `server.server_directory`: サーバー上のデータディレクトリ（サーバーモードで入力/出力ファイルの基準となるディレクトリ）
- `defaults.timeout`: コマンド実行のタイムアウト秒数（デフォルト: 300）
- `defaults.working_directory`: デフォルトの作業ディレクトリ

### 環境変数

設定ファイルの代わりに、または設定ファイルと併用して環境変数を使用できます。
環境変数は設定ファイルより優先されます。

**利用可能な環境変数**:
- `SPSS_MODELER_CLEMB_PATH`: clemb.exeのパス
- `SPSS_MODELER_SERVER_HOSTNAME`: サーバーのホスト名
- `SPSS_MODELER_SERVER_PORT`: サーバーのポート番号
- `SPSS_MODELER_SERVER_USERNAME`: サーバーのユーザー名
- `SPSS_MODELER_SERVER_PASSWORD`: サーバーのパスワード
- `SPSS_MODELER_SERVER_DIRECTORY`: サーバーのデータディレクトリ
- `SPSS_MODELER_DEFAULT_TIMEOUT`: デフォルトのタイムアウト秒数
- `SPSS_MODELER_DEFAULT_WORKING_DIRECTORY`: デフォルトの作業ディレクトリ

**環境変数の設定例** (Windows PowerShell):
```powershell
$env:SPSS_MODELER_SERVER_HOSTNAME = "myserver.example.com"
$env:SPSS_MODELER_SERVER_PORT = "28063"
$env:SPSS_MODELER_SERVER_USERNAME = "dminer"
$env:SPSS_MODELER_SERVER_PASSWORD = "your_password"
```

### 設定の優先順位

設定値は以下の優先順位で適用されます（上が優先）:
1. ツール呼び出し時の引数
2. 環境変数
3. 設定ファイル
4. デフォルト値

### セキュリティに関する注意

- **パスワードの管理**: 設定ファイルにパスワードを保存する場合は、ファイルのアクセス権限を適切に設定してください
- **gitignore**: `config.json`は`.gitignore`に含まれており、Gitリポジトリにコミットされません
- **環境変数の推奨**: 本番環境では、設定ファイルよりも環境変数の使用を推奨します

## テスト

サーバーの機能をテストするには：

```bash
# テストディレクトリに移動
cd tests

# テストを実行
python test_server.py
```

詳細なテスト情報については、[tests/README.md](tests/README.md)を参照してください。

## ドキュメント

- [仕様書](SPECIFICATION.md) - `execute_clemb`ツールの詳細な技術仕様、パラメータ定義、エラーハンドリング、設定管理、トラブルシューティングガイド
- [テストガイド](tests/README.md) - テストの実行方法とカスタマイズ

## 使用例

### サーバーモードでの実行

設定ファイルまたは環境変数でサーバー接続情報を設定している場合、ツール呼び出し時に接続情報を省略できます：

```python
# 設定ファイルのサーバー情報を使用
use_mcp_tool(
    server_name="spss-modeler-clemb",
    tool_name="execute_clemb",
    arguments={
        "stream_file": "C:/models/credit_scoring.str",
        "working_directory": "C:/projects/analysis"
    }
)
```

特定の実行でサーバー情報を上書きすることもできます：

```python
# 引数でサーバー情報を指定（設定ファイルより優先）
use_mcp_tool(
    server_name="spss-clemb-mcp",
    tool_name="execute_clemb",
    arguments={
        "stream_file": "C:/models/credit_scoring.str",
        "hostname": "different-server.example.com",
        "port": 28063,
        "username": "another_user",
        "password": "another_password",
        "working_directory": "C:/projects/analysis"
    }
)
```

### ストリームファイルの実行

**基本的な使用例**:
```python
# MCPクライアントから
use_mcp_tool(
    server_name="spss-clemb-mcp",
    tool_name="execute_clemb",
    arguments={
        "stream_file": "C:/models/credit_scoring.str",
        "working_directory": "C:/projects/analysis",
        "log_file": "execution.log"
    }
)
```

**パラメータを使用する例**:
```python
use_mcp_tool(
    server_name="spss-clemb-mcp",
    tool_name="execute_clemb",
    arguments={
        "stream_file": "C:/models/credit_scoring.str",
        "parameters": {
            "threshold": "0.7"
        },
        "working_directory": "C:/projects/analysis",
        "log_file": "execution.log"
    }
)
```

**パラメータの動作**:
- `parameters`: ストリームまたはスクリプトに渡す追加パラメータ（キー・バリューのペア）
  - clembコマンドラインでは `-P key=value` 形式で渡されます
  - 複数のパラメータを指定可能（例: `{"param1": "value1", "param2": "value2"}` → `-P param1=value1 -P param2=value2`）
  - ストリーム内のノードプロパティを設定する場合は、適切なパス形式を使用してください
  - スクリプト内では、これらのパラメータを使用してストリームの動作をカスタマイズできます

### スクリプトの実行

**インラインスクリプトを実行する例**:
```python
# MCPクライアントから
use_mcp_tool(
    server_name="spss-clemb-mcp",
    tool_name="execute_clemb",
    arguments={
        "script": """
import modeler.api
stream = modeler.script.stream()
# パラメータが変数として利用可能
print(f'Processing with threshold: {threshold}')
        """,
        "parameters": {
            "threshold": "0.7"
        },
        "working_directory": "C:/projects/analysis"
    }
)
```

**スクリプトファイルを実行する例**:
```python
use_mcp_tool(
    server_name="spss-clemb-mcp",
    tool_name="execute_clemb",
    arguments={
        "script_file": "scripts/process_data.py",
        "parameters": {
            "model_type": "C5.0",
            "threshold": "0.7"
        },
        "working_directory": "C:/projects/analysis",
        "log_file": "script_execution.log"
    }
)
```

### ストリームとスクリプトの組み合わせ実行

**ストリームを読み込んでスクリプトで操作する例**:
```python
use_mcp_tool(
    server_name="spss-modeler-clemb",
    tool_name="execute_clemb",
    arguments={
        "stream_file": "models/credit_model.str",
        "script": """
import modeler.api
stream = modeler.script.stream()
# ストリームが読み込まれた状態でスクリプトを実行
nodes = stream.findAll()
print(f'Stream has {len(nodes)} nodes')
        """,
        "working_directory": "C:/projects/analysis",
        "log_file": "combined_execution.log"
    }
)
```

**パラメータの動作**:
- **ストリームのみ実行**: `stream_file`を指定、`script`と`script_file`は未指定
- **スクリプトのみ実行**: `script`または`script_file`を指定、`stream_file`は未指定
- **ストリーム + スクリプト実行**: `stream_file`と（`script`または`script_file`）の両方を指定
- `script`と`script_file`は同時に指定できません（排他的）
- `parameters`で指定した値は、スクリプト内で変数として利用可能になります
- 相対パスは`working_directory`を基準に絶対パスに変換されます

## Bobからの実行例

### 例1: スクリプトファイルの実行

**ユーザーの指示**:
```
'credit_model_ja2.py' をspss-modeler-clembで実行して
```

**Bobの実行**:
```xml
<use_mcp_tool>
<server_name>spss-clemb-mcp</server_name>
<tool_name>execute_clemb</tool_name>
<arguments>
{
  "script_file": "c:\\tests\\bkp\\credit_type_ja2.py"
}
</arguments>
</use_mcp_tool>
```

**実行結果**:
```
Exit Code: 0

=== STDOUT ===
ストリームが正常に作成され、保存されました: C:\temp6\credit_model_stream.str
```

このスクリプトは、SPSS Modelerストリームを作成し、CSVファイルを読み込むノードとフィールド定義ノードを追加して、ストリームファイルとして保存します。

### 例2: ストリームファイルの実行（ログ出力付き）

**ユーザーの指示**:
```
'spss-modeler-clemb/tests/credit_model_stream_output.str' をspss-modeler-clembで実行してlogもみせて
```

**Bobの実行**:
```xml
<use_mcp_tool>
<server_name>spss-clemb-mcp</server_name>
<tool_name>execute_clemb</tool_name>
<arguments>
{
  "stream_file": "c:\\tests\\credit_model_stream_output.str",
  "log_file": "c:\\tests\\credit_model_execution.log"
}
</arguments>
</use_mcp_tool>
```

**実行結果**:
```
Exit Code: 0

=== LOG FILE ===
IBM® SPSS® Modeler 19 - (C) Copyright IBM Corp. 1994, 2021
バッチ モードによる実行、フラグ 2026/03/26 15:43:29
情報: サーバー localhost:28063、セッション 20558-27226 に接続しました
情報: 実行を開始しています...
情報: Stream run in progress...
情報: モデル '信用度' の構築に、0 時間 0 分 0 秒かかりました
情報: モデル '信用度' を評価しています...
情報: モデル '信用度' の評価に、0 時間 0 分 0 秒かかりました
情報: ストリーム実行の成功
情報: ストリーム実行の完了 経過時間=1.0 秒、CPU=0.06 秒
情報: 実行を開始しています...
情報: Stream run in progress...
情報: ストリーム実行の成功
情報: ストリーム実行の完了 経過時間=1.0 秒、CPU=0.02 秒
```

このストリームは、信用度予測モデルを構築・評価し、2回のストリーム実行を行いました。ログファイルを指定することで、詳細な実行情報を確認できます。