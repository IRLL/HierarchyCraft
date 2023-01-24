import pytest_check as check
import numpy as np


def check_np_equal(array: np.ndarray, expected_array: np.ndarray):
    check.is_true(
        np.all(array == expected_array),
        msg=f"Got:\n{array}\nExpected:\n{expected_array}\nDiff:{array-expected_array}",
    )
