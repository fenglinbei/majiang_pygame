import time

def run_time(function):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = function(*args, **kwargs)
        end_time = time.time()
        print(f"{function.__name__} 运行时间为 {end_time - start_time} 秒")
        return result
    return wrapper

def test(fun, count: int = 100000):
        def runner(*args, **kwargs):
            start_time = time.time()
            for i in range(count - 1):
                result = fun(*args, **kwargs)
            result = fun(*args, **kwargs)
            end_time = time.time()
            print(f"{fun.__name__} 共运行{count}次，运行时间为 {(end_time - start_time) * 1000} 毫秒， 平均每次 {(end_time - start_time) * 1000 / count} 毫秒")
            return result
        return runner