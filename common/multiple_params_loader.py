import os
import importlib.util

def load_params_module(path):
    module_name = os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if not hasattr(module, "params"):
        raise AttributeError(f"{path} に `params` が定義されていません")

    return module.params
"""
def load_multiple_params(paths):
    results = []
    for path in paths:
        try:
            params = load_params_module(path)
            
            results.append((path, params))
        except Exception as e:
            print(f" {path} の読み込みに失敗しました: {e}")
    return results
"""

def load_multiple_params(filenames, base_dir):
    """
    パラメータファイル名のリストと基準ディレクトリを受け取り、
    各ファイルから (path, params) を読み込んで返す。
    filenames: ["testcase.py", "testcase2.py", ...]
    base_dir: 省略時は "analytical/params"
    """
    results = []
    for name in filenames:
        if "/" in name or "\\" in name:
            print(f" 無効なファイル名（パスを含めないでください）: {name}")
            continue

        path = os.path.join(base_dir, name)
        try:
            params = load_params_module(path)
            results.append((path, params))
        except Exception as e:
            print(f"{path} の読み込みに失敗しました: {e}")
    
    return results
