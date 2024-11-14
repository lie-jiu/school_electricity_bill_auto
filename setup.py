from setuptools import setup, find_packages

setup(
    name='电费检测',
    version='1.0',
    packages=find_packages(),
    # 其他参数...
    setup_requires=['setuptools>=40.6.0'],
    install_requires=[
        # 您的依赖列表...
    ],
    # 如果您需要构建 wheel，确保包含以下行
    # 注意：如果您使用的是 Python 3.7 或更高版本，bdist_wheel 可能不需要
    # bdist_wheel={"universal": True},
)