#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>


// n must be passed before the 2D array, C99 compitable compiler required
void cumsum_2d(size_t r, size_t c, double matrix[][c])
{
    // cum sum in first col
    for (int i = 1; i < r; i++)
        matrix[i][0] = matrix[i - 1][0] + matrix[i][0];
    // cum sum in first row
    for (int i = 1; i < c; i++)
        matrix[0][i] = matrix[0][i - 1] + matrix[0][i];

    for (int i = 1; i < r; i++) {
      for (int j = 1; j < c; j++)
        if (i > j)  {
          matrix[i][j] = matrix[j][i];
        }
        else {
          matrix[i][j] = matrix[i- 1][j] + matrix[i][j- 1] - matrix[i- 1][j- 1] + matrix[i][j];
        }
      }
}


int main() {
        double arr[][3] = {{1, 2, 3}, {2, 5, 4}, {3, 4, 10}};
        size_t r = 3, c = 3;
        cumsum_2d(r, c, arr);
        int i, j;
        for (i = 0; i < r; i++) {
            for (j = 0; j < c; j++) {
                printf("%f ", arr[i][j]);
              }
          printf("\n");
        }

        return 0;
}
