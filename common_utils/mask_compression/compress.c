#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>


int compress(const uint8_t *image_np_arr, size_t in_size, int *encoded_arr, size_t out_size) {
        /* compress an int array image_np_arr to show number and count of that number
           i.e. [0,0,0,1,1,1,1] => [0,3,1,4]

           returns the ending index in encoded_arr
         */

        size_t i;
        int j = 0;
        int ccount = 0;
        uint8_t prev = image_np_arr[0];
        size_t esize = 1;

        for (i = 0; i < in_size; i++) {
                if (image_np_arr[i] == prev) {
                        ccount++;
                }
                else {
                        encoded_arr[j++] = prev;
                        if (j > out_size) return -1;
                        encoded_arr[j++] = ccount;
                        if (j > out_size) return -1;
                        ccount = 1;
                }
                prev = image_np_arr[i];
        }
        encoded_arr[j++] = prev;
        if (j > out_size) return -1;
        encoded_arr[j++] = ccount;
        if (j > out_size) return -1;

        return j; // return end index in encoded_arr
}

int main() {
        uint8_t a[] = {1,1,1,1,0,0,0,2,2,2,2};
        size_t asz = 11;
        int b[] = {0,0,0,0,0,0,0};
        size_t bsz = 7;
        size_t idx = compress(a, asz, b, bsz);
        for (size_t i = 0; i < 6; i++) {
                printf("%d\n", b[i]);
        }
        printf("value of end index is %zu\n", idx);
        return 0;
}
