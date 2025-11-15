import java.util.*;

public class Main {
    public static List<String> fizzBuzz(int n) {
        List<String> result = new ArrayList<>();
        for (int i = 1; i <= n; i++) {
            if (i % 15 == 0) {
                result.add("FizzBuzz");
            } else if (i % 3 == 0) {
                result.add("Fizz");
            } else if (i % 5 == 0) {
                result.add("Buzz");
            } else {
                result.add(Integer.toString(i));
            }
        }
        return result;
    }

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        int n = Integer.parseInt(scanner.nextLine().trim());
        List<String> result = fizzBuzz(n);

        System.out.print("[");
        for (int i = 0; i < result.size(); i++) {
            if (i > 0) System.out.print(",");
            System.out.print("\"" + result.get(i) + "\"");
        }
        System.out.println("]");
    }
}
