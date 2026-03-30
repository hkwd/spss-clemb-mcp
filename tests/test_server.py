#!/usr/bin/env python3
"""
SPSS Modeler clemb.exe MCPサーバーのテストプログラム
"""
from mcp.types import TextContent
from spss_clemb_mcp.server import execute_clemb, list_tools, call_tool
import asyncio
import json
import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加（インポートより前に実行）
project_root = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(project_root))

# パス追加後にインポート


class TestColors:
    """テスト結果の色付け用"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """ヘッダーを表示"""
    print(f"\n{TestColors.HEADER}{TestColors.BOLD}{'=' * 60}{TestColors.ENDC}")
    print(f"{TestColors.HEADER}{TestColors.BOLD}{text}{TestColors.ENDC}")
    print(f"{TestColors.HEADER}{TestColors.BOLD}{'=' * 60}{TestColors.ENDC}\n")


def print_success(text: str):
    """成功メッセージを表示"""
    print(f"{TestColors.OKGREEN}[OK] {text}{TestColors.ENDC}")


def print_error(text: str):
    """エラーメッセージを表示"""
    print(f"{TestColors.FAIL}[ERROR] {text}{TestColors.ENDC}")


def print_info(text: str):
    """情報メッセージを表示"""
    print(f"{TestColors.OKCYAN}[INFO] {text}{TestColors.ENDC}")


def print_warning(text: str):
    """警告メッセージを表示"""
    print(f"{TestColors.WARNING}[WARNING] {text}{TestColors.ENDC}")


async def test_list_tools():
    """ツールリストの取得テスト"""
    print_header("Test 1: ツールリストの取得")

    try:
        tools = await list_tools()
        print_info(f"取得したツール数: {len(tools)}")

        # 期待されるツール名（統合後は1つのみ）
        expected_tools = ["execute_clemb"]
        tool_names = [tool.name for tool in tools]

        for expected in expected_tools:
            if expected in tool_names:
                print_success(f"ツール '{expected}' が見つかりました")
            else:
                print_error(f"ツール '{expected}' が見つかりません")
                return False

        # 各ツールの詳細を表示
        for tool in tools:
            print(f"\n{TestColors.OKBLUE}ツール名:{TestColors.ENDC} {tool.name}")
            print(f"{TestColors.OKBLUE}説明:{TestColors.ENDC} {tool.description}")
            print(f"{TestColors.OKBLUE}必須パラメータ:{TestColors.ENDC} {tool.inputSchema.get('required', [])}")

        print_success("ツールリストの取得テスト: 成功")
        return True

    except Exception as e:
        print_error(f"ツールリストの取得テスト: 失敗 - {str(e)}")
        return False


async def test_execute_clemb_with_invalid_file():
    """存在しないストリームファイルでのテスト"""
    print_header("Test 2: 存在しないストリームファイルの実行")

    try:
        arguments = {
            "stream_file": "nonexistent_file.str"
        }

        print_info(f"テスト引数: {json.dumps(arguments, indent=2, ensure_ascii=False)}")

        result = await call_tool("execute_clemb", arguments)

        # 結果を表示
        if result and len(result) > 0:
            print(f"\n{TestColors.OKBLUE}実行結果:{TestColors.ENDC}")
            print(result[0].text)

            # エラーが適切に処理されているか確認
            if "Error" in result[0].text or "Exit Code:" in result[0].text:
                print_success("エラーハンドリングテスト: 成功")
                return True
            else:
                print_warning("予期しない結果が返されました")
                return False
        else:
            print_error("結果が返されませんでした")
            return False

    except Exception as e:
        print_error(f"テスト実行中にエラー: {str(e)}")
        return False


async def test_execute_clemb_script_with_simple_script():
    """簡単なスクリプトの実行テスト"""
    print_header("Test 3: 簡単なスクリプトの実行")

    try:
        # 簡単なPythonスクリプト（SPSS Modeler APIを使用しない）
        test_script = """
print("Hello from SPSS Modeler Script Test")
print("This is a test script")
import sys
print(f"Python version: {sys.version}")
"""

        arguments = {
            "script": test_script
        }

        print_info("テストスクリプト:")
        print(test_script)

        result = await call_tool("execute_clemb", arguments)

        # 結果を表示
        if result and len(result) > 0:
            print(f"\n{TestColors.OKBLUE}実行結果:{TestColors.ENDC}")
            print(result[0].text)

            # 実行が完了したか確認
            if "Exit Code:" in result[0].text:
                print_success("スクリプト実行テスト: 成功")
                return True
            else:
                print_warning("予期しない結果が返されました")
                return False
        else:
            print_error("結果が返されませんでした")
            return False

    except Exception as e:
        print_error(f"テスト実行中にエラー: {str(e)}")
        return False


async def test_execute_clemb_script_without_params():
    """パラメータなしでのスクリプト実行テスト"""
    print_header("Test 4: パラメータなしでのスクリプト実行")

    try:
        arguments = {}

        print_info("テスト引数: (空)")

        result = await call_tool("execute_clemb", arguments)

        # 結果を表示
        if result and len(result) > 0:
            print(f"\n{TestColors.OKBLUE}実行結果:{TestColors.ENDC}")
            print(result[0].text)

            # エラーメッセージが適切に返されているか確認
            if "Error" in result[0].text and ("script" in result[0].text or "script_file" in result[0].text):
                print_success("パラメータ検証テスト: 成功")
                return True
            else:
                print_warning("予期しない結果が返されました")
                return False
        else:
            print_error("結果が返されませんでした")
            return False

    except Exception as e:
        print_error(f"テスト実行中にエラー: {str(e)}")
        return False


async def test_execute_clemb_with_parameters():
    """パラメータ付きストリーム実行のテスト（サーバーモード）"""
    print_header("Test 5: パラメータ付きストリーム実行（サーバーモード）")

    try:
        # testsディレクトリのパスを取得
        tests_dir = os.path.dirname(os.path.abspath(__file__))

        arguments = {
            "stream_file": "credit_model_stream_output.str",
            "server_directory": "/home/dsuser1",
            "working_directory": tests_dir,
            "log_file": "test_execution.log"
        }

        print_info(f"テスト引数: {json.dumps(arguments, indent=2, ensure_ascii=False)}")
        print_info(f"作業ディレクトリ: {tests_dir}")

        result = await call_tool("execute_clemb", arguments)

        # 結果を表示
        if result and len(result) > 0:
            print(f"\n{TestColors.OKBLUE}実行結果:{TestColors.ENDC}")
            print(result[0].text)

            # 実行が成功したかどうかを確認
            if "Exit Code: 0" in result[0].text or "情報: ストリーム実行の完了" in result[0].text:
                print_success("サーバーモード実行テスト: 成功")
                return True
            else:
                print_error("実行が失敗しました")
                return False
        else:
            print_error("結果が返されませんでした")
            return False

    except Exception as e:
        print_error(f"テスト実行中にエラー: {str(e)}")
        return False


async def test_execute_clemb_local_mode():
    """ローカルモードでのストリーム実行テスト"""
    print_header("Test 6: ローカルモードでのストリーム実行")

    log_file = "test_execution_local_mode.log"

    try:
        # testsディレクトリのパスを取得
        tests_dir = os.path.dirname(os.path.abspath(__file__))
        log_path = os.path.join(tests_dir, log_file)

        # 既存のログファイルを削除
        if os.path.exists(log_path):
            os.remove(log_path)

        arguments = {
            "stream_file": "credit_model_stream_output.str",
            "working_directory": tests_dir,
            "log_file": log_file,
            "hostname": "",  # ローカルモードを強制（サーバーに接続しない）
            "port": None,
            "username": "",
            "password": ""
        }

        print_info(f"テスト引数: {json.dumps(arguments, indent=2, ensure_ascii=False)}")
        print_info(f"作業ディレクトリ: {tests_dir}")
        print_info(f"ログファイル: {log_path}")

        result = await call_tool("execute_clemb", arguments)

        # 結果を表示
        if result and len(result) > 0:
            print(f"\n{TestColors.OKBLUE}実行結果:{TestColors.ENDC}")
            print(result[0].text)

            # 実行が成功したかどうかを確認
            if "Exit Code: 0" in result[0].text or "情報: ストリーム実行の完了" in result[0].text:
                # ログファイルの内容が結果に含まれているか確認
                if f"=== LOG FILE ({log_file}) ===" in result[0].text:
                    print_success("ローカルモード実行テスト: 成功（ログファイル内容が結果に含まれています）")
                    return True
                else:
                    print_warning("ログファイルの内容が結果に含まれていません")
                    return False
            else:
                print_error("実行が失敗しました")
                return False
        else:
            print_error("結果が返されませんでした")
            return False

    except Exception as e:
        print_error(f"テスト実行中にエラー: {str(e)}")
        return False


async def test_execute_clemb_script_with_file():
    """スクリプトファイルを使用した実行テスト"""
    print_header("Test 7: スクリプトファイルを使用した実行")

    test_script_path = "test_script_temp.py"
    log_file = "test_execution_script_file.log"

    try:
        # testsディレクトリのパスを取得
        tests_dir = os.path.dirname(os.path.abspath(__file__))
        log_path = os.path.join(tests_dir, log_file)

        # 既存のログファイルを削除
        if os.path.exists(log_path):
            os.remove(log_path)

        # テスト用のスクリプトファイルを作成
        test_script_content = """
print("Test script from file")
print("Script execution successful")
"""

        # 一時スクリプトファイルを作成（tests_dirに作成）
        script_full_path = os.path.join(tests_dir, test_script_path)
        with open(script_full_path, 'w', encoding='utf-8') as f:
            f.write(test_script_content)

        print_info(f"一時スクリプトファイルを作成: {test_script_path}")
        print_info(f"ログファイル: {log_path}")

        arguments = {
            "script_file": test_script_path,
            "log_file": log_file,
            "working_directory": tests_dir
        }

        print_info(f"テスト引数: {json.dumps(arguments, indent=2, ensure_ascii=False)}")

        result = await call_tool("execute_clemb", arguments)

        # 結果を表示
        if result and len(result) > 0:
            print(f"\n{TestColors.OKBLUE}実行結果:{TestColors.ENDC}")
            print(result[0].text)

            if "Exit Code:" in result[0].text:
                # ログファイルの内容が結果に含まれているか確認
                result_text = result[0].text
                log_section = f"=== LOG FILE ({log_file}) ==="

                print_info(f"ログセクションを検索: '{log_section}'")
                print_info(f"結果に含まれているか: {log_section in result_text}")

                if log_section in result_text:
                    print_success("スクリプトファイル実行テスト: 成功（ログファイル内容が結果に含まれています）")
                    success = True
                else:
                    print_warning("ログファイルの内容が結果に含まれていません")
                    # デバッグ: 結果に含まれるセクションを表示
                    if "=== LOG FILE" in result_text:
                        print_info("結果には別のログファイルセクションが含まれています")
                    success = False
            else:
                print_warning("予期しない結果が返されました")
                success = False
        else:
            print_error("結果が返されませんでした")
            success = False

        # 一時ファイルを削除
        try:
            os.remove(test_script_path)
            print_info(f"一時スクリプトファイルを削除: {test_script_path}")
        except:
            pass

        return success

    except Exception as e:
        print_error(f"テスト実行中にエラー: {str(e)}")
        # クリーンアップ
        try:
            if os.path.exists(test_script_path):
                os.remove(test_script_path)
        except:
            pass
        return False


async def test_execute_clemb_script_with_file_local_mode():
    """スクリプトファイルを使用したローカルモード実行テスト"""
    print_header("Test 8: スクリプトファイルを使用したローカルモード実行")

    test_script_path = "test_script_temp_local.py"
    log_file = "test_execution_script_file_local_mode.log"

    try:
        # testsディレクトリのパスを取得
        tests_dir = os.path.dirname(os.path.abspath(__file__))
        log_path = os.path.join(tests_dir, log_file)

        # 既存のログファイルを削除
        if os.path.exists(log_path):
            os.remove(log_path)

        # テスト用のスクリプトファイルを作成
        test_script_content = """
print("Test script from file (Local Mode)")
print("Local mode script execution successful")
"""

        # 一時スクリプトファイルを作成（tests_dirに作成）
        script_full_path = os.path.join(tests_dir, test_script_path)
        with open(script_full_path, 'w', encoding='utf-8') as f:
            f.write(test_script_content)

        print_info(f"一時スクリプトファイルを作成: {test_script_path}")
        print_info(f"ログファイル: {log_path}")

        arguments = {
            "script_file": test_script_path,
            "log_file": log_file,
            "working_directory": tests_dir,  # 作業ディレクトリを指定
            "hostname": "",  # ローカルモードを強制（サーバーに接続しない）
            "port": None,
            "username": "",
            "password": ""
        }

        print_info(f"テスト引数: {json.dumps(arguments, indent=2, ensure_ascii=False)}")

        result = await call_tool("execute_clemb", arguments)

        # 結果を表示
        if result and len(result) > 0:
            print(f"\n{TestColors.OKBLUE}実行結果:{TestColors.ENDC}")
            print(result[0].text)

            if "Exit Code:" in result[0].text:
                # ログファイルの内容が結果に含まれているか確認
                result_text = result[0].text
                log_section = f"=== LOG FILE ({log_file}) ==="

                print_info(f"ログセクションを検索: '{log_section}'")
                print_info(f"結果に含まれているか: {log_section in result_text}")

                if log_section in result_text:
                    print_success("ローカルモードスクリプトファイル実行テスト: 成功（ログファイル内容が結果に含まれています）")
                    success = True
                else:
                    print_warning("ログファイルの内容が結果に含まれていません")
                    # デバッグ: 結果に含まれるセクションを表示
                    if "=== LOG FILE" in result_text:
                        print_info("結果には別のログファイルセクションが含まれています")
                    success = False
            else:
                print_warning("予期しない結果が返されました")
                success = False
        else:
            print_error("結果が返されませんでした")
            success = False

        # 一時ファイルを削除
        try:
            os.remove(test_script_path)
            print_info(f"一時スクリプトファイルを削除: {test_script_path}")
        except:
            pass

        return success

    except Exception as e:
        print_error(f"テスト実行中にエラー: {str(e)}")
        # クリーンアップ
        try:
            if os.path.exists(test_script_path):
                os.remove(test_script_path)
        except:
            pass
        return False


async def test_invalid_tool_name():
    """存在しないツール名でのテスト"""
    print_header("Test 9: 存在しないツール名の呼び出し")

    try:
        arguments = {}

        print_info("テストツール名: invalid_tool_name")

        try:
            result = await call_tool("invalid_tool_name", arguments)
            print_error("例外が発生しませんでした")
            return False
        except ValueError as e:
            if "Unknown tool" in str(e):
                print_success(f"適切なエラーが発生: {str(e)}")
                return True
            else:
                print_error(f"予期しないエラー: {str(e)}")
                return False

    except Exception as e:
        print_error(f"テスト実行中にエラー: {str(e)}")
        return False


async def test_auto_working_directory_from_stream():
    """ストリームファイルからworking_directoryを自動設定するテスト"""
    print_header("Test 10: ストリームファイルからworking_directory自動設定")

    try:
        # testsディレクトリのストリームファイルを使用
        tests_dir = os.path.dirname(os.path.abspath(__file__))
        stream_file = "credit_model_stream.str"
        stream_path = os.path.join(tests_dir, stream_file)

        print_info(f"テストディレクトリ: {tests_dir}")
        print_info(f"ストリームファイル: {stream_file}")
        print_info(f"ストリームファイルの絶対パス: {stream_path}")

        # ストリームファイルの存在確認
        if not os.path.exists(stream_path):
            print_warning(f"ストリームファイルが存在しません: {stream_path}")
            print_info("このテストはスキップされます")
            return True  # ファイルがない場合はテストをスキップ

        # テスト1: 相対パスのストリームファイル、working_directory未指定
        print_info("\n--- テスト1: 相対パス + working_directory未指定 ---")
        arguments = {
            "stream_file": stream_file,
            # working_directoryは指定しない
            # hostnameも指定しない（ローカルモード）
        }

        print_info(f"テスト引数: {json.dumps(arguments, indent=2, ensure_ascii=False)}")
        print_info("期待される動作: カレントディレクトリからの相対パスでstream_fileのディレクトリがworking_directoryになる")

        result = await call_tool("execute_clemb", arguments)

        if result and len(result) > 0:
            print(f"\n{TestColors.OKBLUE}実行結果（抜粋）:{TestColors.ENDC}")
            result_text = result[0].text
            # コマンド部分のみ表示
            if "=== COMMAND ===" in result_text:
                cmd_start = result_text.find("=== COMMAND ===")
                cmd_end = result_text.find("===", cmd_start + 20)
                if cmd_end > cmd_start:
                    print(result_text[cmd_start:cmd_end + 3])

            print_success("テスト1: 実行成功")
        else:
            print_error("テスト1: 結果が返されませんでした")
            return False

        # テスト2: 絶対パスのストリームファイル、working_directory未指定
        print_info("\n--- テスト2: 絶対パス + working_directory未指定 ---")
        arguments = {
            "stream_file": stream_path,  # 絶対パス
            # working_directoryは指定しない
        }

        print_info(f"テスト引数: {json.dumps(arguments, indent=2, ensure_ascii=False)}")
        print_info(f"期待される動作: {tests_dir} がworking_directoryになる")

        result = await call_tool("execute_clemb", arguments)

        if result and len(result) > 0:
            print(f"\n{TestColors.OKBLUE}実行結果（抜粋）:{TestColors.ENDC}")
            result_text = result[0].text
            if "=== COMMAND ===" in result_text:
                cmd_start = result_text.find("=== COMMAND ===")
                cmd_end = result_text.find("===", cmd_start + 20)
                if cmd_end > cmd_start:
                    print(result_text[cmd_start:cmd_end + 3])

            print_success("テスト2: 実行成功")
        else:
            print_error("テスト2: 結果が返されませんでした")
            return False

        # テスト3: working_directoryを明示的に指定（優先されることを確認）
        print_info("\n--- テスト3: working_directory明示指定（優先確認） ---")
        custom_dir = os.path.dirname(tests_dir)  # 親ディレクトリ
        arguments = {
            "stream_file": stream_file,
            "working_directory": custom_dir  # 明示的に指定
        }

        print_info(f"テスト引数: {json.dumps(arguments, indent=2, ensure_ascii=False)}")
        print_info(f"期待される動作: 指定された {custom_dir} がworking_directoryになる")

        result = await call_tool("execute_clemb", arguments)

        if result and len(result) > 0:
            print(f"\n{TestColors.OKBLUE}実行結果（抜粋）:{TestColors.ENDC}")
            result_text = result[0].text
            if "=== COMMAND ===" in result_text:
                cmd_start = result_text.find("=== COMMAND ===")
                cmd_end = result_text.find("===", cmd_start + 20)
                if cmd_end > cmd_start:
                    print(result_text[cmd_start:cmd_end + 3])

            print_success("テスト3: 実行成功")
        else:
            print_error("テスト3: 結果が返されませんでした")
            return False

        print_success("working_directory自動設定テスト: すべて成功")
        return True

    except Exception as e:
        print_error(f"テスト実行中にエラー: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_tests():
    """すべてのテストを実行"""
    print_header("SPSS Modeler clemb.exe MCPサーバー テストスイート")

    tests = [
        ("スクリプトファイル実行", test_execute_clemb_script_with_file),
        ("スクリプトファイル実行（ローカルモード）", test_execute_clemb_script_with_file_local_mode),
        ("working_directory自動設定", test_auto_working_directory_from_stream),
        ("サーバーモード実行", test_execute_clemb_with_parameters),
        ("ローカルモード実行", test_execute_clemb_local_mode),
        ("ツールリストの取得", test_list_tools)
        # ("存在しないストリームファイル", test_execute_clemb_with_invalid_file),
        # ("簡単なスクリプトの実行", test_execute_clemb_script_with_simple_script),
        # ("パラメータなしスクリプト実行", test_execute_clemb_script_without_params),
        # ("存在しないツール名", test_invalid_tool_name),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"テスト '{test_name}' で予期しないエラー: {str(e)}")
            results.append((test_name, False))

    # 結果サマリーを表示
    print_header("テスト結果サマリー")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        if result:
            print_success(f"{test_name}: 成功")
        else:
            print_error(f"{test_name}: 失敗")

    print(f"\n{TestColors.BOLD}合計: {passed}/{total} テストが成功{TestColors.ENDC}")

    if passed == total:
        print(f"{TestColors.OKGREEN}{TestColors.BOLD}すべてのテストが成功しました！{TestColors.ENDC}")
        return 0
    else:
        print(f"{TestColors.FAIL}{TestColors.BOLD}一部のテストが失敗しました{TestColors.ENDC}")
        return 1


def main():
    """メイン関数"""
    print(f"{TestColors.OKCYAN}Python version: {sys.version}{TestColors.ENDC}")
    print(f"{TestColors.OKCYAN}Working directory: {os.getcwd()}{TestColors.ENDC}")

    # テストを実行
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

# Made with Bob
