
import math;

# returns the time to compute the proof using Argon Design's algorithm, with 
# parameters gamma and kappa as in their report
def cost_of_proof(T, gamma,kappa, parameters):
    return math.ceil(parameters['mult_square_ratio']*(T / kappa + gamma * (2**kappa)));


# finds the optimal parameters gamma and kappa for time parameter T, to minimize 
# the time to compute the proof given a bound on the available memory
def optimize(T,parameters):
    bestGamma = 0
    bestKappa = 0
    bestCost = 0
    
    for kappa in range(1,math.ceil(math.log(T)/math.log(2))):
        if parameters['memory_bound'] > 0:
            # smallest gamma such that:
            # T/(gamma*kappa)*parameters['modulus_length'] < parameters['memory_bound']
            gamma = math.ceil(T/(parameters['memory_bound']*kappa)*parameters['modulus_length']);
        else:
            gamma = 1;
        time_cost = cost_of_proof(T,gamma,kappa, parameters);
        if bestCost == 0 or bestCost > time_cost:
            bestGamma = gamma
            bestKappa = kappa
            bestCost = time_cost

    return bestCost; #[bestKappa, bestGamma, bestCost, (T / bestCost).n()]


# given a first ckeckpoint, find the other points (the next checkpoint is the
# point at which the prover finishes the proof for the previous checkpoint;
# i.e., after the first checkpoint, the prover is always busy)
def find_checkpoints(first_checkpoint, n, parameters):
    L = [first_checkpoint];
    for x in range(0,n-1):
        L.append(optimize(L[x], parameters));
    return L;


# find the optimal way to place n checkpoints (n-Wesolowski) to minimise the
# final prover overhead
# returns the list of checkpoints (integers between 0 and T) and the 
# fraction overhead/T
def optimize_iterated(T,n, parameters):
    if n == 1:
        return [[0], optimize(T, parameters)];

    checkpoint = T//2;
    step = T//4;

    while step != 0:
        L = find_checkpoints(checkpoint,n, parameters);
        total_time = sum(L);

        while total_time < T:
            checkpoint += step;
            total_time = sum(find_checkpoints(checkpoint,n, parameters));
        
        while total_time > T:
            checkpoint -= step;
            total_time = sum(find_checkpoints(checkpoint,n, parameters));

        step = step//2;

    L = find_checkpoints(checkpoint,n, parameters);
    return [L, optimize(L.pop(), parameters)];


# returns the time to compute the proof using Argon Design's algorithm, with 
# parameters gamma and kappa as in their report
def cost_of_proof_for_hybrid(T, N, gamma,kappa, parameters):
    t = math.ceil(T/2**N);
    return math.ceil(parameters['mult_square_ratio']*(t / kappa + gamma * (2**kappa) \
        + 1.5* parameters['security_level']*2**N*t/(kappa*gamma) ));

# finds the optimal parameters gamma and kappa for time parameter T, to minimize 
# the time to compute the proof given a bound on the available memory
def optimize_hybrid(T,N,parameters):
    bestGamma = 0
    bestKappa = 0
    bestCost = 0
    
    for kappa in range(1,math.ceil(math.log(T)/math.log(2))):
        if parameters['memory_bound'] > 0:
            # smallest gamma such that:
            # T/(gamma*kappa)*parameters['modulus_length'] < parameters['memory_bound']
            gamma = math.ceil(T/(parameters['memory_bound']*kappa)*parameters['modulus_length']);
        else:
            gamma = 1;
        time_cost = cost_of_proof_for_hybrid(T,N,gamma,kappa, parameters);
        if bestCost == 0 or bestCost > time_cost:
            bestGamma = gamma
            bestKappa = kappa
            bestCost = time_cost

    return bestCost; #[bestKappa, bestGamma, bestCost, (T / bestCost).n()]


def test(T, parameters):
    print ("T =", T);
    print (parameters);

    for N in range(1,8):
        print ("Hybrid prover with", N-1, "Pietrzak rounds");
        print ("Size of proofs: ", ((N)*parameters['modulus_length'])/8, "B");
        print ("Overhead: ", (100*optimize_hybrid(T,N-1, parameters)/T), "%\n");

    for N in range(1,8):
        print ("%d-iterated prover" % N);
        print ("Size of proofs: ", (N*parameters['modulus_length'] \
                                  + (N-1)*2*parameters['security_level'])/8, "B");
        print ("Overhead: ", (100*optimize_iterated(T,N, parameters)[1]/T), "%\n");


parameters = {
    'mult_square_ratio': 1.2/4, # relative cost of multiplication vs squaring
    # (as an example, I say that the latency of multiplication is 1.2 times
    # the lattency of squaring, but one can do 4 multiplications in parallel)

    'modulus_length': 2048, # binary length of RSA modulus
    'memory_bound': 8 * 8 * 2**20, # allowed to store 8 MB of precomputed data
    'security_level': 128 # number of bits of security
};


# assuming a squaring latency of 1ns, then T = 2**39 leads to around 
# 9 minutes of evaluation time
T = 2**39;
test(T, parameters);



