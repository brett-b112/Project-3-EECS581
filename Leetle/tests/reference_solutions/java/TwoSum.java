import java.util.*;

public class Main {
    public static int[] twoSum(int[] nums, int target) {
        Map<Integer, Integer> numMap = new HashMap<>();
        for (int i = 0; i < nums.length; i++) {
            int complement = target - nums[i];
            if (numMap.containsKey(complement)) {
                return new int[]{numMap.get(complement), i};
            }
            numMap.put(nums[i], i);
        }
        return new int[0];
    }

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        // Read first line (array)
        String numsStr = scanner.nextLine().trim();
        // Parse array, removing brackets and splitting by comma
        numsStr = numsStr.substring(1, numsStr.length() - 1); // Remove [ ]
        String[] numStrs = numsStr.split(",");
        int[] nums = new int[numStrs.length];
        for (int i = 0; i < numStrs.length; i++) {
            nums[i] = Integer.parseInt(numStrs[i].trim());
        }

        // Read second line (target)
        int target = Integer.parseInt(scanner.nextLine().trim());

        int[] result = twoSum(nums, target);

        // Print result
        System.out.print("[");
        for (int i = 0; i < result.length; i++) {
            if (i > 0) System.out.print(",");
            System.out.print(result[i]);
        }
        System.out.println("]");
    }
}
