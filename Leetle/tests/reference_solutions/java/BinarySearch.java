import java.util.*;

public class Main {
    public static int search(int[] nums, int target) {
        int left = 0, right = nums.length - 1;
        while (left <= right) {
            int mid = left + (right - left) / 2;
            if (nums[mid] == target) {
                return mid;
            } else if (nums[mid] < target) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
        return -1;
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

        int result = search(nums, target);
        System.out.println(result);
    }
}
