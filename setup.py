from setuptools import setup, find_packages

setup(
    name='yqg-git-ai',
    version='0.1.0',
    packages=find_packages(),
    package_data={
        'yqg_git_ai': ['config.json'],  # 把 config.json 打包到 yqg_git_ai 包目录下
    },
    install_requires=[
        'GitPython',
        'prompt_toolkit',
        'openai',
    ],
    entry_points={
        'console_scripts': [
            'yqg-git = yqg_git_ai.__main__:main'
        ]
    },
    author='你的名字',
    description='智能Git分支AI助手',
    python_requires='>=3.7',
) 