// gcc blankprover.c -o blankprover

#include <stdio.h>
#include <stdlib.h>


// fake functions for counting operations
#define MULTIPLY(RES,X,Y)  ++total_mul
#define SQUARE(RES,X)  ++total_squ
#define EXPONENTIATION(RES,X,E) increment_operation_counters(&total_squ,&total_mul,E)
#define GET_BLOCK(B)
#define SET_TO_NEUTRAL(X)
#define RETURN(X)


// counts the number of squarings and multiplications performed by a simple square and multiply 
// (which is not the optimal method, but good enough)
void increment_operation_counters(unsigned long int *squarings, unsigned long int *multiplications, unsigned long int n) {
	unsigned int squ = 0, mul = n&1;
	n >>= 1;
	while (n != 0) {++squ; mul += n&1; n >>= 1;} 
	if (mul != 0) --mul; // the most significant 1 does not induce a multiplication
	*squarings += squ;
	*multiplications += mul;
}

void evaluate(unsigned long int *squarings, unsigned long int *multiplications, unsigned long int tau,
	unsigned long int block_size, unsigned long int blocks_per_checkpoint){

	unsigned long int total_squ = 0, total_mul = 0;

	unsigned long int checkpoint_interval = (block_size*blocks_per_checkpoint);
	unsigned long int k1 = block_size/2, k0 = block_size - k1;

	// the following bound is just tau/checkpoint_interval rounded up
	unsigned int bound = (tau + checkpoint_interval - 1)/checkpoint_interval; 

	for (int k = blocks_per_checkpoint-1; k >= 0; k--) {

		for (int i = 0; i < block_size; ++i) {
			SQUARE(result,result);
		}

		for (int i = 0; i < ((unsigned long int)1<<block_size); ++i) {
	        SET_TO_NEUTRAL(boxes[i]);
	    }


		for (int i = 0; i < bound; ++i) {
			GET_BLOCK(block)
			MULTIPLY(boxes[block], boxes[block], checkpoint[i]);
		}

		for (unsigned int i = 0; i < ((unsigned long int)1<<k1); ++i) {
			SET_TO_NEUTRAL(tmp);

			for (unsigned int j = 0; j < ((unsigned long int)1<<k0); ++j) {
				MULTIPLY(tmp, tmp, boxes[(i<<k0) + j]);
			}
			EXPONENTIATION(tmp, tmp, (i<<k0));
			MULTIPLY(result, result, tmp);

		}

		for (unsigned int j = 0; j < ((unsigned long int)1<<k0); ++j) {
			SET_TO_NEUTRAL(tmp);

			for (unsigned int i = 0; i < ((unsigned long int)1<<k1); ++i) {
				MULTIPLY(tmp, tmp, boxes[(i<<k0) + j]);
			}
			EXPONENTIATION(tmp, tmp, j);
			MULTIPLY(result, result, tmp);

		}
	}

	*squarings = total_squ;
	*multiplications = total_mul;

	RETURN(result);
}



int main(int argc, char **argv){
	if (argc < 4) { printf("3 arguments are required: log_2(T), the size of a block (in bits), and the number of blocks per stored checkpoint.\n"); return 0; }

	unsigned long int tau = ((unsigned long int)1 << atoi(argv[1])); // 2^36
	unsigned long int block_size = atoi(argv[2]); // 22
	unsigned long int blocks_per_checkpoint = atoi(argv[3]); // 16

	unsigned long int total_mul = 0;
	unsigned long int total_squ = 0;

	evaluate(&total_mul, &total_squ, tau, block_size, blocks_per_checkpoint);

	printf("T = %lu	\nsquarings: S = %lu\nmultiplications: M = %lu \nratio: T/(M+S) = %f\n", tau, total_squ, total_mul, (double)tau / (total_squ + total_mul));

	return 0;
}
