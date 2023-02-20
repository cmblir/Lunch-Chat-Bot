def solution(array, n):
    breakpoint()
    array.sort()
    left = 0
    right = len(array) - 1
    result = None
    if n not in array:
        low = abs(n - array[right])
        high = abs(array[left] - n)
        if low <= high: result = array[right]
        else: result = array[left]
        return result

print(solution([10, 9, 7, 13, 20, 15], 14))