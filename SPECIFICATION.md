# SPSS Modeler clemb.exe MCPサーバー 仕様書

## 1. 概要

### 1.1 目的
このMCPサーバーは、IBM SPSS Modelerのコマンドラインツール [`clemb.exe`](C:\Program Files\IBM\SPSS\Modeler\19.0\bin\clemb.exe) を実行するための標準化されたインターフェースを提供します。AIアシスタントやその他のMCPクライアントから、SPSS Modelerのストリームファイルやスクリプトを実行できるようにします。

### 1.2 バージョン
- **バージョン**: 0.1.0
- **対応MCPバージョン**: 0.9.0以上
- **対応Pythonバージョン**: 3.10以上

### 1.3 依存関係
- **必須**: IBM SPSS Modeler 19.0がインストールされていること
- **clemb.exeパス**: `C:\Program Files\IBM\SPSS\Modeler\19.0\bin\clemb.exe`
- **Pythonパッケージ**: mcp>=0.9.0

## 2. アーキテクチャ

### 2.1 通信方式
- **プロトコル**: MCP (Model Context Protocol)
- **通信方法**: stdio (標準入出力)
- **サーバータイプ**: ローカル実行型

### 2.2 コンポーネント構成
```
spss-modeler-clemb/
├── spss_modeler_clemb/
│   ├── __init__.py
│   └── server.py          # メインサーバー実装
├── pyproject.toml         # プロジェクト設定
└── README.md              # 使用方法
```

### 2.3 実行フロー
```
MCPクライアント
    ↓ (stdio)
MCPサーバー (server.py)
    ↓ (subprocess)
clemb.exe
    ↓
SPSS Modeler実行エンジン
```

## 3. 提供ツール

### 3.1 execute_clemb

#### 概要
SPSS Modelerのストリームファイル(.str)、スクリプト、またはその両方を実行します。

#### 実行モード
1. **ストリームのみ**: ストリームファイルを実行
2. **スクリプトのみ**: Pythonスクリプトを実行（インラインまたはファイル）
3. **ストリーム + スクリプト**: ストリームを読み込んでからスクリプトで操作

#### パラメータ

| パラメータ名 | 型 | 必須 | 説明 |
|------------|-----|------|------|
| `stream_file` | string | - | 実行するSPSS Modelerストリームファイル(.str)のパス |
| `script` | string | - | 実行するSPSS Modelerスクリプト（文字列）。`script_file`と同時指定不可 |
| `script_file` | string | - | 実行するスクリプトファイル(.py)のパス。`script`と同時指定不可 |
| `hostname` | string | - | SPSS Modelerサーバーのホスト名（サーバーモード） |
| `port` | integer | - | サーバーのポート番号 |
| `username` | string | - | サーバーのユーザー名 |
| `password` | string | - | サーバーのパスワード |
| `server_directory` | string | - | サーバーのデータディレクトリ |
| `parameters` | object | - | ストリームまたはスクリプトに渡すパラメータ |
| `working_directory` | string | - | 作業ディレクトリのパス |
| `log_file` | string | - | ログファイルの出力パス |

**パラメータ検証**:
- 少なくとも`stream_file`、`script`、`script_file`のいずれか1つが必須
- `script`と`script_file`は同時に指定できません（排他的）

#### 実行コマンド形式

**ストリームのみ**:
```bash
clemb.exe -stream <stream_file> -execute [-P key=value ...] [-log <log_file>]
```

**スクリプトのみ**:
```bash
clemb.exe -script <script_file> -execute [-log <log_file>]
```

**ストリーム + スクリプト**:
```bash
clemb.exe -stream <stream_file> -script <script_file> -execute [-log <log_file>]
```

#### 使用例

**ストリームのみ実行**:
```json
{
  "stream_file": "C:/models/credit_model.str",
  "parameters": {
    "threshold": "0.7"
  },
  "working_directory": "C:/projects/analysis",
  "log_file": "execution.log"
}
```

**スクリプトのみ実行**:
```json
{
  "script": "import modeler.api\nstream = modeler.script.stream()\nprint('Hello')",
  "working_directory": "C:/projects/analysis"
}
```

**ストリーム + スクリプト実行**:
```json
{
  "stream_file": "models/credit_model.str",
  "script": "import modeler.api\nstream = modeler.script.stream()\nprint(len(stream.findAll()))",
  "working_directory": "C:/projects/analysis",
  "log_file": "combined.log"
}
```

#### 戻り値
- **型**: TextContent
- **内容**:
  - Exit Code (終了コード)
  - COMMAND (実行されたコマンド、スクリプト実行時のみ)
  - STDOUT (標準出力)
  - STDERR (標準エラー出力)
  - LOG FILE (ログファイルの内容、指定時のみ)

#### エラーハンドリング
- **タイムアウト**: 5分（300秒）で実行を中断
- **ファイル不在**: clemb.exeまたはスクリプトファイルが見つからない場合はエラー
- **パラメータエラー**: 必須パラメータが未指定、または排他的パラメータが同時指定された場合はエラー
- **実行エラー**: 例外が発生した場合はエラー詳細を返す

## 4. 設定管理

### 4.1 設定ファイル

サーバー接続情報やデフォルト設定を管理するために、JSON形式の設定ファイルを使用できます。

#### 設定ファイルの検索順序

設定ファイルは以下の順序で検索され、最初に見つかったファイルが使用されます：

1. カレントディレクトリの`config.json`
2. プロジェクトルート（[`spss-modeler-clemb/`](spss-modeler-clemb/)）の`config.json`
3. ホームディレクトリの`~/.spss-modeler-clemb/config.json`

#### 設定ファイルの形式

```json
{
  "clemb_path": "C:\\Program Files\\IBM\\SPSS\\Modeler\\19.0\\bin\\clemb.exe",
  "server": {
    "hostname": "myserver.example.com",
    "port": 28053,
    "username": "dminer",
    "password": "your_password_here"
  },
  "defaults": {
    "timeout": 300,
    "working_directory": "C:\\projects\\analysis"
  }
}
```

#### 設定項目

| 項目 | 型 | 説明 | デフォルト値 |
|------|-----|------|-------------|
| `clemb_path` | string | clemb.exeの絶対パス | `C:\Program Files\IBM\SPSS\Modeler\19.0\bin\clemb.exe` |
| `server.hostname` | string | SPSS Modelerサーバーのホスト名 | なし（ローカルモード） |
| `server.port` | integer | サーバーのポート番号 | なし |
| `server.username` | string | サーバーのユーザー名 | なし |
| `server.password` | string | サーバーのパスワード | なし |
| `defaults.timeout` | integer | コマンド実行のタイムアウト秒数 | 300 |
| `defaults.working_directory` | string | デフォルトの作業ディレクトリ | なし |

### 4.2 環境変数

設定ファイルの代わりに、または設定ファイルと併用して環境変数を使用できます。

#### 利用可能な環境変数

| 環境変数名 | 説明 |
|-----------|------|
| `SPSS_MODELER_CLEMB_PATH` | clemb.exeのパス |
| `SPSS_MODELER_SERVER_HOSTNAME` | サーバーのホスト名 |
| `SPSS_MODELER_SERVER_PORT` | サーバーのポート番号 |
| `SPSS_MODELER_SERVER_USERNAME` | サーバーのユーザー名 |
| `SPSS_MODELER_SERVER_PASSWORD` | サーバーのパスワード |
| `SPSS_MODELER_DEFAULT_TIMEOUT` | デフォルトのタイムアウト秒数 |
| `SPSS_MODELER_DEFAULT_WORKING_DIRECTORY` | デフォルトの作業ディレクトリ |

### 4.3 設定の優先順位

設定値は以下の優先順位で適用されます（上が優先）：

1. **ツール呼び出し時の引数** - 最優先
2. **環境変数** - 設定ファイルより優先
3. **設定ファイル** - デフォルト値より優先
4. **デフォルト値** - 最低優先

例：
- `hostname`がツール引数、環境変数、設定ファイルの全てで指定されている場合、ツール引数の値が使用されます
- `hostname`が環境変数と設定ファイルで指定されている場合、環境変数の値が使用されます

### 4.4 セキュリティ考慮事項

#### パスワード管理
- 設定ファイルにパスワードを保存する場合は、ファイルのアクセス権限を適切に設定してください
- `config.json`は`.gitignore`に含まれており、Gitリポジトリにコミットされません
- 本番環境では、設定ファイルよりも環境変数の使用を推奨します

#### 設定ファイルの保護
```bash
# Windowsでファイルのアクセス権限を制限
icacls config.json /inheritance:r /grant:r "%USERNAME%:F"
```

## 5. 技術仕様

### 5.1 文字エンコーディング対応

#### 問題
SPSS Modelerおよびclemb.exeは日本語などのマルチバイト文字の処理に課題があります。

#### 解決策
以下の多層的なエンコーディング設定を実装:

1. **環境変数設定**:
```python
env['JAVA_TOOL_OPTIONS'] = '-Dfile.encoding=UTF-8 -Dclient.encoding.override=UTF-8 -Dsun.jnu.encoding=UTF-8'
env['PYTHONIOENCODING'] = 'utf-8'
```

2. **PowerShell経由実行** (execute_clemb_scriptのみ):
```powershell
chcp 65001 > $null
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

3. **Python subprocess設定**:
```python
# execute_clembの場合
subprocess.run(..., encoding='utf-8', errors='replace')

# execute_clemb_scriptの場合
subprocess.run(..., text=False)  # バイナリモードで取得
stdout.decode('utf-8', errors='replace')  # UTF-8でデコード
```

### 5.2 タイムアウト設定
- **デフォルト**: 300秒（5分）
- **理由**: 大規模なデータ処理や複雑なモデル実行に対応
- **変更方法**: 設定ファイルの`defaults.timeout`または環境変数`SPSS_MODELER_DEFAULT_TIMEOUT`で変更可能

### 5.3 一時ファイル管理
- **作成場所**: `working_directory`が指定されている場合はそのディレクトリ、未指定の場合はシステムのtempディレクトリ
- **命名規則**: `tmp<random>.py`
- **削除タイミング**: スクリプト実行完了後（成功・失敗に関わらず）
- **エンコーディング**: UTF-8

### 5.4 エラーハンドリング戦略

| エラータイプ | 検出方法 | 対応 |
|------------|---------|------|
| タイムアウト | `subprocess.TimeoutExpired` | エラーメッセージを返す |
| ファイル不在 | `FileNotFoundError` | clemb.exeのパスを含むエラーメッセージ |
| スクリプトファイル不在 | `os.path.exists()` | ファイルパスを含むエラーメッセージ |
| 一般的な例外 | `Exception` | 例外の詳細を含むエラーメッセージ |

## 6. インストールと設定

### 6.1 インストール手順

```bash
# リポジトリのクローン
cd spss-modeler-clemb

# 開発モードでインストール
pip install -e .
```

### 6.2 設定ファイルのセットアップ

```bash
# サンプル設定ファイルをコピー
cp config.example.json config.json

# 設定を編集（必要に応じて）
# エディタでconfig.jsonを開き、サーバー接続情報などを設定
```

### 6.3 MCP設定

**Cline設定ファイル** (`cline_mcp_settings.json`):
```json
{
  "mcpServers": {
    "spss-modeler-clemb": {
      "command": "python",
      "args": ["-m", "spss_modeler_clemb.server"]
    }
  }
}
```

**Claude Desktop設定ファイル** (Windows):
```json
{
  "mcpServers": {
    "spss-modeler-clemb": {
      "command": "python",
      "args": ["-m", "spss_modeler_clemb.server"]
    }
  }
}
```

### 6.4 動作確認

```bash
# サーバーが正しく起動するか確認
python -m spss_modeler_clemb.server
```

## 7. 使用例

### 7.1 ストリームのみ実行

```python
use_mcp_tool(
    server_name="spss-modeler-clemb",
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

### 7.2 スクリプトのみ実行

**インラインスクリプト**:
```python
use_mcp_tool(
    server_name="spss-modeler-clemb",
    tool_name="execute_clemb",
    arguments={
        "script": """
import modeler.api
stream = modeler.script.stream()
print('Hello from SPSS Modeler')
        """,
        "working_directory": "C:/projects/analysis"
    }
)
```

**スクリプトファイル**:
```python
use_mcp_tool(
    server_name="spss-modeler-clemb",
    tool_name="execute_clemb",
    arguments={
        "script_file": "scripts/batch_process.py",
        "working_directory": "C:/projects/batch",
        "log_file": "batch_process.log"
    }
)
```

### 7.3 ストリーム + スクリプト実行

```python
use_mcp_tool(
    server_name="spss-modeler-clemb",
    tool_name="execute_clemb",
    arguments={
        "stream_file": "models/credit_model.str",
        "script": """
import modeler.api
stream = modeler.script.stream()
nodes = stream.findAll()
print(f'Stream has {len(nodes)} nodes')
        """,
        "working_directory": "C:/projects/analysis",
        "log_file": "combined.log"
    }
)
```

## 8. 制限事項と注意点

### 8.1 プラットフォーム
- **対応OS**: Windows のみ
- **理由**: clemb.exeはWindows専用のバイナリ

### 8.2 SPSS Modelerバージョン
- **対応バージョン**: 19.0
- **パス**: 異なるバージョンを使用する場合は、設定ファイルの`clemb_path`または環境変数`SPSS_MODELER_CLEMB_PATH`で変更可能

### 8.3 実行時間
- **最大実行時間**: デフォルト5分
- **長時間処理**: 設定ファイルの`defaults.timeout`または環境変数`SPSS_MODELER_DEFAULT_TIMEOUT`でタイムアウト値を調整可能

### 8.4 並行実行
- **制限**: 複数のツール呼び出しを同時に実行する場合、SPSS Modelerのライセンスや実行環境の制約に注意が必要です

### 8.5 パス指定
- **推奨**: 絶対パスの使用
- **相対パス**: `working_directory`を基準に解決されます

## 9. トラブルシューティング

### 9.1 clemb.exeが見つからない

**エラー**: `Error: clemb.exe not found at C:\Program Files\IBM\SPSS\Modeler\19.0\bin\clemb.exe`

**解決策**:
1. SPSS Modeler 19.0がインストールされているか確認
2. インストールパスが異なる場合は、設定ファイルの`clemb_path`または環境変数`SPSS_MODELER_CLEMB_PATH`を設定

### 9.2 日本語の文字化け

**症状**: 出力やログに日本語が正しく表示されない

**解決策**:
- 環境変数が正しく設定されているか確認
- PowerShellのコードページが65001（UTF-8）になっているか確認
- ログファイルをUTF-8対応のエディタで開く

### 9.3 タイムアウトエラー

**エラー**: `Error: clemb.exe execution timed out after 5 minutes`

**解決策**:
1. 処理を最適化して実行時間を短縮
2. 設定ファイルの`defaults.timeout`または環境変数`SPSS_MODELER_DEFAULT_TIMEOUT`でタイムアウト値を増やす

### 9.4 サーバー接続エラー

**症状**: サーバーモードでの実行が失敗する

**確認事項**:
1. サーバー接続情報（hostname、port、username、password）が正しいか
2. サーバーが起動しているか
3. ネットワーク接続が正常か
4. ファイアウォールがポートをブロックしていないか

### 9.5 スクリプトエラー

**症状**: スクリプトが正しく実行されない

**確認事項**:
1. スクリプトの構文が正しいか
2. SPSS Modeler APIの使用方法が正しいか
3. 必要なストリームやノードが存在するか
4. ログファイルを確認してエラー詳細を把握

## 10. セキュリティ考慮事項

### 10.1 設定ファイルのセキュリティ
- 設定ファイルにパスワードを保存する場合は、適切なファイルアクセス権限を設定
- `config.json`は`.gitignore`に含まれており、バージョン管理から除外されます
- 本番環境では環境変数の使用を推奨

### 10.2 ファイルアクセス
- サーバーは指定されたパスのファイルに対して読み書きアクセスを持ちます
- 信頼できないソースからのパス指定には注意が必要です

### 10.3 コマンド実行
- clemb.exeを通じてシステムコマンドが実行される可能性があります
- スクリプト内容の検証が推奨されます

### 10.4 一時ファイル
- 一時ファイルは実行後に削除されますが、実行中は機密情報が含まれる可能性があります
- 適切なファイルシステム権限の設定が推奨されます

## 11. 今後の拡張予定

### 11.1 機能拡張
- [ ] 非同期実行のサポート
- [ ] 進捗状況のリアルタイム報告
- [ ] 複数バージョンのSPSS Modelerサポート
- [ ] Linux/macOS対応（該当バージョンが利用可能な場合）

### 11.2 改善項目
- [x] 設定ファイルによるclemb.exeパスのカスタマイズ
- [x] サーバー接続情報の設定ファイル管理
- [ ] より詳細なエラーメッセージ
- [ ] 実行履歴の記録
- [ ] パフォーマンスメトリクスの収集
- [ ] 設定ファイルの暗号化サポート

## 12. 参考資料

### 12.1 関連ドキュメント
- [MCP仕様](https://modelcontextprotocol.io/)
- [SPSS Modeler公式ドキュメント](https://www.ibm.com/docs/ja/spss-modeler/19.0.0)
- [clemb.exeコマンドリファレンス](https://www.ibm.com/docs/ja/spss-modeler/19.0.0?topic=modeler-batch-execution-mode)

### 12.2 サポート
- **Issue報告**: GitHubリポジトリのIssuesセクション
- **質問**: プロジェクトのDiscussionsセクション

---

**最終更新日**: 2026-02-26  
**作成者**: Bob (AI Assistant)  
**バージョン**: 1.0.0