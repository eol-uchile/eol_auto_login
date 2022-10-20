import setuptools

setuptools.setup(
    name="eol_auto_login",
    version="0.0.1",
    author="Luis Santana",
    author_email="luis.santana@uchile.cl",
    url="https://eol.uchile.cl",
    packages=setuptools.find_packages(),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "lms.djangoapp": ["eol_auto_login = eol_auto_login.apps:AutoLoginConfig"],
        "cms.djangoapp": ["eol_auto_login = eol_auto_login.apps:AutoLoginConfig"]
    },
)
