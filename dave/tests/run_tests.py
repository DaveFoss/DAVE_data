import os

import pytest

from dave import dave_dir

# get path of the DaVe test directory
test_dir = os.path.join(dave_dir, "tests")


def run_all_tests():
    """
    This function execute all DaVe tests
    """
    # n_cpu = 4
    # pytest.main([test_dir, '-n', str(n_cpu)])
    exit_code = pytest.main([test_dir])


if __name__ == "__main__":
    run_all_tests()
