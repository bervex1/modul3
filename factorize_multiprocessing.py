import multiprocessing
import time

def factorize_sync(number):
    factors = []
    for i in range(1, number + 1):
        if number % i == 0:
            factors.append(i)
    return factors

def factorize(number):
    factors = []
    for i in range(1, number + 1):
        if number % i == 0:
            factors.append(i)
    return factors

def factorize_parallel(numbers):
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        results = pool.map(factorize, numbers)
    return results

if __name__ == "__main__":
    numbers = [128, 255, 99999, 10651060]
    
    start_time_sync = time.time()
    results_sync = [factorize_sync(num) for num in numbers]
    end_time_sync = time.time()
    print("Synchronous Execution Time:", end_time_sync - start_time_sync)

    start_time_parallel = time.time()
    results_parallel = factorize_parallel(numbers)
    end_time_parallel = time.time()
    print("Parallel Execution Time:", end_time_parallel - start_time_parallel)
