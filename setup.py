import setuptools

setuptools.setup(
    name="ev_weathersync",
    version="0.0.20",
    author="Invian",
    author_email="info@invian.ru",
    description="Just a weather synchronizer",
    packages=["evwsync", "shared"],
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
