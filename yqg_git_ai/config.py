import os
import json
import sys

def load_config():
    # 1. 先找包目录（安装后和开发时都在这里）
    package_dir = os.path.dirname(__file__)  # yqg_git_ai 包目录
    install_config = os.path.join(package_dir, 'config.json')
    if os.path.exists(install_config):
        with open(install_config, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    # 2. 再找当前目录（兼容用户自定义配置）
    current_config = os.path.join(os.getcwd(), 'config.json')
    if os.path.exists(current_config):
        with open(current_config, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    # 3. 都找不到就报错，并给出清晰的错误信息
    raise ValueError(f"找不到配置文件！请确保以下任一位置存在 config.json:\n"
                    f"1. 包安装目录: {install_config}\n"
                    f"2. 当前目录: {current_config}") 