import os
import pytest

@pytest.fixture(autouse=True)
def change_to_tests_dir():
    orig = os.getcwd()
    os.chdir(os.path.dirname(__file__))
    yield
    os.chdir(orig)
