import java.util.Random;
import java.util.concurrent.ThreadLocalRandom;

public class Utils {

	public static int randInt(int min, int max) {

		// Random int in range [min, max].

		Random rand = new Random();

		int randomNum = rand.nextInt((max - min) + 1) + min;

		return randomNum;
	}

	public static double randDouble(double min, double max) {
		return ThreadLocalRandom.current().nextDouble(min, max);
	}

	public static void printMatrix(int[][] matrix, int citySize) {
		for (int i = 0; i < citySize; i++) {
			for (int j = 0; j < citySize; j++) {
				System.out.print((matrix[i][j] == 0 ? " " : "#") + "\t");
			}
			System.out.println();
		}
	}

}