import setuptools

project_homepage = "https://github.com/RaihanStark/instalivecli"

with open("README.md", "r", encoding="utf8") as fh:
    long_description = fh.read()

with open("requirements.txt") as f:
    dependencies = f.read().splitlines()

setuptools.setup(
    name='InstaLiveCLI',
    version='1.0.2',
    packages=setuptools.find_packages(),
    url='https://github.com/RaihanStark/instalivecli',
    license='GPL-3.0',
    author='Raihan Yudo Saputra',
    author_email='raihanyudosaputra30@gmail.com',
    description='InstaLiveCLI is a Python CLI that create a Instagram Live and provide you a rtmp server '
                'and stream key to streaming using sofwares like OBS-Studio.',
    project_urls={
        "Example": (project_homepage + "/blob/master/live_broadcast.py"),
        "Bug Reports": (project_homepage + "/issues"),
    },
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires='>=3.8',
    install_requires=dependencies,
)
