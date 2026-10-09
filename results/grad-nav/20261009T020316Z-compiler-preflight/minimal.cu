#include <cuda_runtime.h>
#include <cstdio>
__global__ void add(int* x){*x=2+3;}
int main(){int* d; int h=0; if(cudaMalloc(&d,sizeof(int))!=cudaSuccess)return 1;add<<<1,1>>>(d);if(cudaDeviceSynchronize()!=cudaSuccess)return 2;if(cudaMemcpy(&h,d,sizeof(int),cudaMemcpyDeviceToHost)!=cudaSuccess)return 3;cudaFree(d);printf("cuda11-ok %d\n",h);return h==5?0:4;}
