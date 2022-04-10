#  compresses segmentation masks

import ctypes
import timeit
import numpy as np
from numpy.ctypeslib import ndpointer


def _get_cumsum_func(shared_lib_path="./libcumsum.so"):
    lib = ctypes.cdll.LoadLibrary(shared_lib_path)
    cumsum_func = lib.cumsum_2d
    cumsum_func.argtypes = [ctypes.c_size_t,
                            ctypes.c_size_t,
                            ndpointer(ctypes.c_double)]
    return cumsum_func


def cumsum_calc(in_matrix, func):
    r, c = in_matrix.shape
    func(r, c, in_matrix)


def main():
    # N = 5
    # temp = np.random.random_integers(0, 10, size=(N, N))
    # matrix_sym = (temp + temp.T) / 2
    #
    # matrix = matrix_sym
    matrix1 = np.array([[1, 2, 3], [2, 5, 4], [3, 4, 10]]).astype(np.double)
    print("orig", matrix1, "\n")
    cumsum_calc(matrix1, _get_cumsum_func())
    print("C cumsum", matrix1)
    time_taken = timeit.timeit("cumsum_calc(np.array([[1, 2, 3], [2, 5, 4], [3, 4, 10]], dtype=np.double), _get_cumsum_func())",
                               number=10, globals=globals()) / 10
    print(f"C cumsum time: {time_taken:.4f}s or {time_taken*1000:.2f}ms")

    matrix2 = np.array([[1, 2, 3], [2, 5, 4], [3, 4, 10]]).astype(np.double)
    print("numpy cumsum", np.cumsum(np.cumsum(matrix2, 0), 1))
    time_taken = timeit.timeit("np.cumsum(np.cumsum(np.array([[1, 2, 3], [2, 5, 4], [3, 4, 10]], dtype=np.double), 0), 1)",
                               number=10, globals=globals()) / 10
    print(f"C cumsum time: {time_taken:.4f}s or {time_taken*1000:.2f}ms")


if __name__ == "__main__":
    main()
