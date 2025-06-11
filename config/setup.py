from setuptools import setup, find_packages

setup(
    name='student_dbms',
    version='1.0.0',
    description='Industry-grade Student Database Management System',
    author='Rushikesh Atole and Team',
    packages=find_packages(),
    install_requires=[
        'python-dotenv',
        'Pillow',
        'reportlab',
        'matplotlib',
        'ttkbootstrap',
    ],
    include_package_data=True,
    python_requires='>=3.8',
)
