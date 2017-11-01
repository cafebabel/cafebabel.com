from setuptools import setup


def is_pkg(line):
    return line and not line.startswith(('-', 'git', '#'))


def load_packages(filepath):
    with open(filepath, encoding='utf-8') as reqs:
        return [l for l in reqs.read().split('\n') if is_pkg(l)]


setup(
    name='cafebabel',
    packages=['cafebabel'],
    include_package_data=True,
    install_requires=load_packages('requirements.txt'),
)
