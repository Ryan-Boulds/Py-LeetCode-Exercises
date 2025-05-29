class Solution(object):
    def twoSum(self, nums, target):
        i = 0
        totalNums = len(nums)
        while i < totalNums:
            j = 0
            while j < totalNums:

                if i != j and nums[i] + nums[j] == target:
                    return [i, j]
                j += 1
            i += 1

solution = Solution()

print(solution.twoSum([2, 7, 11, 15], 9))
print(solution.twoSum([3, 2, 4], 6))
print(solution.twoSum([3, 3], 6))
