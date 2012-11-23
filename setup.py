try:
    from setuptools import setup
except ImportError:
    from distribute_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

setup(
    d2to1=True,
    package_data={
    },
)
