# Copyright (c) 2022-2023 by Fraunhofer Institute for Energy Economics and Energy System Technology (IEE)
# Kassel and individual contributors (see AUTHORS file for details). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

import os

import pytest

from dave.settings import dave_settings

# get path of the DaVe test directory
test_dir = os.path.join(dave_settings()["dave_dir"], "tests")


def run_all_tests():
    """
    This function execute all DaVe tests
    """
    # n_cpu = 4
    # pytest.main([test_dir, '-n', str(n_cpu)])
    exit_code = pytest.main([test_dir])


if __name__ == "__main__":
    run_all_tests()
