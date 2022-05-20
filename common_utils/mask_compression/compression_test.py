#  compresses segmentation masks

import ctypes
import timeit
import numpy as np
from numpy.ctypeslib import ndpointer


def encode_np_array(arr):
    arr = arr.tolist()
    prev = arr[0]
    ccount = 0
    encoded_arr = []
    append = encoded_arr.append
    for n in arr:
        if n == prev:
            ccount += 1
        else:
            append(prev)
            append(ccount)
            ccount = 1
        prev = n
    append(prev)
    append(ccount)
    return encoded_arr


def decode_np_array(arr):
    if isinstance(arr, np.ndarray):
        arr = arr.tolist()
    decoded_arr = []
    for a, b in zip(arr[0::2], arr[1::2]):
        decoded_arr.extend([a for _ in range(b)])
    return decoded_arr


def _get_encoding_func(shared_lib_path="./libcompress.so"):
    """ input array must be contiguous, i.e. send a flattened array
    """
    lib = ctypes.cdll.LoadLibrary(shared_lib_path)
    compress_func = lib.compress
    compress_func.restype = ctypes.c_int32
    compress_func.argtypes = [ndpointer(ctypes.c_uint8, flags="C_CONTIGUOUS"),
                              ctypes.c_size_t,
                              ndpointer(ctypes.c_int, flags="C_CONTIGUOUS"),
                              ctypes.c_size_t]
    return compress_func


def encode_np_array_c(indata, compress_func, outdata_size=None):
    """args: indata: a contiguous list/numpy.ndarray that needs to be compressed
             compress_func: compression function to use
             outdata_size: size of outdata buffer
    """
    if outdata_size is None:
        outdata_size = len(indata) if len(
            indata) < 100000 else int(len(indata) // 1.5)

    outdata = np.full(outdata_size, -1, dtype=np.int32)
    end_idx = compress_func(indata, len(indata), outdata, len(outdata))

    if end_idx == -1:
        # outdata_buffer size / outdata_size was not enough,
        # so use the max possible size of outdata_buffer
        print("outdata_size is too small. Retrying with max possible size")
        return encode_np_array_c(indata, compress_func, len(indata) * 2)

    outdata = outdata[:end_idx]
    return outdata


def main():
    indata = np.load('sample_img_mask.npy').astype(np.uint8)
    print("Input data sent to both funcs", indata, indata.size)

    outdata_c = encode_np_array_c(indata, _get_encoding_func())
    time_taken = timeit.timeit("indata = np.load('image.npy').astype(np.uint8); encode_np_array_c(indata, _get_encoding_func())",
                               number=10, globals=globals()) / 10
    print(f"c and python {time_taken:.4f}s or {time_taken*1000:.2f}ms")
    print("Output from c func", outdata_c, len(outdata_c))

    # check if encoded arr matches the orig image
    dec = decode_np_array(outdata_c)
    print("Encoded img matches original img"
          if dec == indata.tolist() else "Error: Encoded img DOES NOT matches original img")

    outdata_python = encode_np_array(indata)
    time_taken = timeit.timeit("indata = np.load('image.npy').astype(np.uint8); encode_np_array(indata)",
                               number=10, globals=globals()) / 10
    print(f"python {time_taken:.4f}s or {time_taken*1000:.2f}ms")
    print("Output from c func", np.array(outdata_python), len(outdata_python))

    # check if encoded arr matches the orig image
    dec = decode_np_array(outdata_python)
    print("Encoded img matches original img"
          if dec == indata.tolist() else "Error: Encoded img DOES NOT matches original img")


if __name__ == "__main__":
    main()
