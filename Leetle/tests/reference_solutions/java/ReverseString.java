import java.util.*;

public class Main {
    public static void reverseString(char[] s) {
        int left = 0, right = s.length - 1;
        while (left < right) {
            char temp = s[left];
            s[left] = s[right];
            s[right] = temp;
            left++;
            right--;
        }
    }

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        String input = scanner.nextLine().trim();

        // Parse array, removing brackets and splitting
        input = input.substring(1, input.length() - 1); // Remove [ ]
        String[] parts = input.split(",");
        char[] s = new char[parts.length];
        for (int i = 0; i < parts.length; i++) {
            // Remove quotes if present
            String part = parts[i].trim();
            part = part.substring(1, part.length() - 1); // Remove quotes
            s[i] = part.charAt(0);
        }

        reverseString(s);

        // Print result
        System.out.print("[");
        for (int i = 0; i < s.length; i++) {
            if (i > 0) System.out.print(",");
            System.out.print("\"" + s[i] + "\"");
        }
        System.out.println("]");
    }
}
