# SPSS Modeler clemb.exe MCPサーバー テストガイド

## 概要

このディレクトリには、SPSS Modeler clemb.exe MCPサーバーの機能をテストするためのテストプログラムが含まれています。

## テストファイル

- [`test_server.py`](test_server.py) - メインテストスイート

## テスト内容

### Test 1: ツールリストの取得
- MCPサーバーが提供するツールのリストを取得
- `execute_clemb`ツールが存在することを確認

### Test 2: 存在しないストリームファイルの実行
- 存在しないストリームファイルを指定した場合のエラーハンドリングをテスト
- 適切なエラーメッセージが返されることを確認

### Test 3: 簡単なスクリプトの実行
- 簡単なPythonスクリプト（SPSS Modeler APIを使用しない）を実行
- スクリプトが正常に実行され、結果が返されることを確認

### Test 4: パラメータなしでのスクリプト実行
- 必須パラメータ（stream_file、script、script_fileのいずれか）が指定されていない場合のエラーハンドリングをテスト
- 適切なエラーメッセージが返されることを確認

### Test 5: パラメータ付きストリーム実行（サーバーモード）
- サーバーモードでストリームファイルを実行
- `server_directory`、`working_directory`、`log_file`パラメータを使用
- コマンドが正しく構築され、実行されることを確認

### Test 6: ローカルモードでのストリーム実行
- ローカルモード（サーバーに接続しない）でストリームファイルを実行
- ログファイルの内容が結果に含まれることを確認

### Test 7: スクリプトファイルを使用した実行
- 外部スクリプトファイル（.py）を使用した実行をテスト
- 一時スクリプトファイルを作成し、実行後に削除
- ログファイルの内容が結果に含まれることを確認

### Test 8: スクリプトファイルを使用したローカルモード実行
- ローカルモードで外部スクリプトファイルを実行
- `working_directory`を指定してファイルパスを解決
- ログファイルの内容が結果に含まれることを確認

### Test 9: 存在しないツール名の呼び出し
- 存在しないツール名を指定した場合のエラーハンドリングをテスト
- `ValueError`例外が適切に発生することを確認

## 実行方法

### 前提条件

1. Python 3.10以上がインストールされていること
2. MCPサーバーがインストールされていること
   ```bash
   cd spss-clemb-mcp
   pip install -e .
   ```

### テストの実行

```bash
# テストディレクトリに移動
cd spss-modeler-clemb/tests

# テストを実行
python test_server.py
```

または、プロジェクトルートから実行:

```bash
python spss-modeler-clemb/tests/test_server.py
```

## テスト結果の見方

テストは色付きで結果を表示します：

- ✓ **緑色**: テスト成功
- ✗ **赤色**: テスト失敗
- ℹ **シアン色**: 情報メッセージ
- ⚠ **黄色**: 警告メッセージ

### 成功例

```
============================================================
Test 1: ツールリストの取得
============================================================

ℹ 取得したツール数: 1
✓ ツール 'execute_clemb' が見つかりました
✓ ツールリストの取得テスト: 成功
```

### 失敗例

```
============================================================
Test 2: 存在しないストリームファイルの実行
============================================================

ℹ テスト引数: {
  "stream_file": "nonexistent_file.str"
}
✗ テスト実行中にエラー: ...
```

## 注意事項

### SPSS Modelerのインストール

これらのテストの多くは、実際にclemb.exeを実行しようとします。SPSS Modeler 19.0がインストールされていない場合、以下のようなエラーが発生します：

```
Error: clemb.exe not found at C:\Program Files\IBM\SPSS\Modeler\19.0\bin\clemb.exe
```

これは正常な動作です。テストはエラーハンドリングが正しく機能していることを確認します。

### タイムアウト

各テストには5分のタイムアウトが設定されています。長時間実行されるストリームやスクリプトをテストする場合は、[`server.py`](../spss_modeler_clemb/server.py:124)のタイムアウト値を調整してください。

### 一時ファイル

Test 6では一時スクリプトファイル（`test_script_temp.py`）を作成します。テスト終了後に自動的に削除されますが、テストが中断された場合は手動で削除する必要がある場合があります。

## トラブルシューティング

### ImportError: No module named 'mcp'

MCPパッケージがインストールされていません：

```bash
pip install mcp
```

または、開発モードでプロジェクトをインストール：

```bash
cd spss-modeler-clemb
pip install -e .
```

### ModuleNotFoundError: No module named 'spss_modeler_clemb'

プロジェクトルートからテストを実行するか、PYTHONPATHを設定してください：

```bash
# Windowsの場合
set PYTHONPATH=%PYTHONPATH%;C:\path\to\spss-modeler-clemb
python tests\test_server.py

# Linux/macOSの場合
export PYTHONPATH=$PYTHONPATH:/path/to/spss-modeler-clemb
python tests/test_server.py
```

### 文字化け

Windowsのコマンドプロンプトで文字化けが発生する場合：

```bash
chcp 65001
python test_server.py
```

## カスタムテストの追加

新しいテストを追加する場合は、以下のテンプレートを使用してください：

```python
async def test_your_new_test():
    """テストの説明"""
    print_header("Test X: テスト名")
    
    try:
        # テストロジック
        arguments = {
            # テスト引数
        }
        
        print_info(f"テスト引数: {json.dumps(arguments, indent=2, ensure_ascii=False)}")
        
        result = await call_tool("tool_name", arguments)
        
        # 結果の検証
        if result and len(result) > 0:
            print(f"\n{TestColors.OKBLUE}実行結果:{TestColors.ENDC}")
            print(result[0].text)
            
            # 検証ロジック
            if "expected_output" in result[0].text:
                print_success("テスト: 成功")
                return True
            else:
                print_error("テスト: 失敗")
                return False
        else:
            print_error("結果が返されませんでした")
            return False
            
    except Exception as e:
        print_error(f"テスト実行中にエラー: {str(e)}")
        return False
```

そして、[`run_all_tests()`](test_server.py:318)関数の`tests`リストに追加：

```python
tests = [
    # 既存のテスト...
    ("新しいテスト", test_your_new_test),
]
```

## CI/CD統合

### GitHub Actions

```yaml
name: Test SPSS Modeler MCP Server

on: [push, pull_request]

jobs:
  test:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          cd spss-modeler-clemb
          pip install -e .
      - name: Run tests
        run: |
          python spss-modeler-clemb/tests/test_server.py
```

## 参考資料

- [MCPサーバー仕様書](../SPECIFICATION.md)
- [MCPプロトコル仕様](https://modelcontextprotocol.io/)
- [SPSS Modeler公式ドキュメント](https://www.ibm.com/docs/ja/spss-modeler/19.0.0)

---

**最終更新日**: 2026-02-26  
**作成者**: Bob (AI Assistant)