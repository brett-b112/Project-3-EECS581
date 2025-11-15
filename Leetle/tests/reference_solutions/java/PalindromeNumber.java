import java.util.*;

public class Main {
    public static boolean isPalindrome(int x) {
        if (x < 0) return false;
        String str = Integer.toString(x);
        String reversed = new StringBuilder(str).reverse().toString();
        return str.equals(reversed);
    }

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        int x = Integer.parseInt(scanner.nextLine().trim());
        boolean result = isPalindrome(x);
        System.out.println(result);
    }
}
