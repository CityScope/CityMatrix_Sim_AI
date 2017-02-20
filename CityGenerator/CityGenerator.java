import java.io.File;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayList;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

public class CityGenerator {

	// Properties configuration.

	public static int numberCities = 100;
	public static int citySize = 16;
	public static double roadDensity = 0.2; // Vary 0.15 to 0.3.
	public static double extProbability = 0.9; // Vary 0.75 to 0.95;
	public static int[][] matrix;
	public static String prefix = "/out/city_";
	public int numDensity = 6;
	public int maxDensity = 30;
	public int lowType = -1;
	public int highType = 5;
	public int roadId = 6;
	public static double buildingProb = 0.8; // Vary 0.6 (sparse) to 1.0 (dense).

	public static void main(String[] args) {

		// Generate cities.
		
		long start = System.currentTimeMillis();

		CityGenerator g = new CityGenerator();

		for (int i = 0; i < numberCities; i++) {
			matrix = new int[citySize][citySize];
			// Varying parameters here.
			roadDensity = Utils.randDouble(0.15, 0.3);
			extProbability = Utils.randDouble(0.755, 0.95);
			buildingProb = Utils.randDouble(0.6, 1.0);
			g.generate();
			g.outputCity(prefix + Integer.toString(i) + ".json");
			System.out.println(i);
		}
		
		long time = System.currentTimeMillis() - start;
		
		System.out.println("Total run time for " + numberCities + " cities = " + time + ".");

	}

	public void generate() {

		// Init queue.
		ArrayList<Road> queue = new ArrayList<Road>();
		int roadCount = (int)(roadDensity * Math.pow(citySize, 2) / 2);
		int numberRoads = 1;
		int minRoadCount = citySize / 2;

		// Generate first road
		Road firstRoad = generateFirstRoad();
		queue.add(firstRoad);

		while (queue.size() > 0 && numberRoads < roadCount) {

			// Pop earliest road off queue.
			Road current = queue.get(0);
			queue.remove(0);

			// Extend this road and add more to queue.
			ArrayList<Pair> startPoints = getRoadStartPoints(current);

			if (startPoints != null) {
				for (Pair p : startPoints) {
					p.start.print();
					Road n = new Road();
					if (extendRoad(n, p.d, p.start)) {
						numberRoads += 1;
						queue.add(n);
					}
				} 
			}

			// Make sure we do not have a sparse road network.
			if (queue.isEmpty() && numberRoads < minRoadCount) {
				Road another = generateFirstRoad();
				queue.add(another);
			}
		}
		
		printMatrix();
	}

	public Road generateFirstRoad() {
		Direction d = Direction.values()[Utils.randInt(0, 3)];
		Road r = new Road();
		r.direction = d;
		int x = -1, y = -1;
		switch (d) {
		case Left:
			x = citySize - 1;
			y = Utils.randInt(0, citySize - 1);
			break;
		case Right:
			x = 0;
			y = Utils.randInt(0, citySize - 1);
			break;
		case Up:
			x = Utils.randInt(0, citySize - 1);
			y = citySize - 1;
			break;
		case Down:
			x = Utils.randInt(0, citySize - 1);
			y = 0;
		default:
			break;
		}
		Point start = new Point(x, y);
		if (extendRoad(r, d, start))
			return r;
		return null;
	}

	public boolean extendRoad(Road r, Direction d, Point start) {
		// System.out.println("Expanding in direction " + d.toString() + " from start " + start.print() + ".");
		r.direction = d;
		int rowStart = start.y;
		int colStart = start.x;
		ArrayList<Point> newPoints = new ArrayList<Point>();
		if (d == Direction.Right) {
			matrix[rowStart][colStart] = -1;
			newPoints.add(new Point(colStart, rowStart));
			for (int col = colStart + 1; col < citySize; col++) {
				if (col == citySize - 1) {
					matrix[rowStart][col] = -1;
					newPoints.add(new Point(col, rowStart));
					break;
				}
				if (isValidRoadPoint(rowStart, col, d)) {
					matrix[rowStart][col] = -1;
					newPoints.add(new Point(col, rowStart));
					if (col != citySize - 1 && matrix[rowStart][col + 1] == -1) {
						double rand = Utils.randDouble(0, 1);
						if (rand <= extProbability)
							col++;
						else
							break;
					}
				} else {
					break;
				}
			}
		} else if (d == Direction.Down) {
			matrix[rowStart][colStart] = -1;
			newPoints.add(new Point(colStart, rowStart));
			for (int row = rowStart + 1; row < citySize; row++) {
				if (row == citySize - 1) {
					matrix[row][colStart] = -1;
					newPoints.add(new Point(colStart, row));
					break;
				}
				if (isValidRoadPoint(row, colStart, d)) {
					matrix[row][colStart] = -1;
					newPoints.add(new Point(colStart, row));
					if (row != citySize - 1 && matrix[row + 1][colStart] == -1) {
						double rand = Utils.randDouble(0, 1);
						if (rand <= extProbability)
							row++;
						else
							break;
					}
				} else {
					break;
				}
			}
		} else if (d == Direction.Left) {
			matrix[rowStart][colStart] = -1;
			newPoints.add(new Point(colStart, rowStart));
			for (int col = colStart - 1; col >= 0; col--) {
				if (col == 0) {
					matrix[rowStart][col] = -1;
					newPoints.add(new Point(col, rowStart));
					break;
				}
				if (isValidRoadPoint(rowStart, col, d)) {
					matrix[rowStart][col] = -1;
					newPoints.add(new Point(col, rowStart));
					if (col != 0 && matrix[rowStart][col - 1] == -1) {
						double rand = Utils.randDouble(0, 1);
						if (rand <= extProbability)
							col++;
						else
							break;
					}
				} else {
					break;
				}
			}
		} else if (d == Direction.Up) {
			matrix[rowStart][colStart] = -1;
			newPoints.add(new Point(colStart, rowStart));
			for (int row = rowStart - 1; row >= 0; row--) {
				if (row == 0) {
					matrix[row][colStart] = -1;
					newPoints.add(new Point(colStart, row));
					break;
				}
				if (isValidRoadPoint(row, colStart, d)) {
					matrix[row][colStart] = -1;
					newPoints.add(new Point(colStart, row));
					if (row != 0 && matrix[row - 1][colStart] == -1) {
						double rand = Utils.randDouble(0, 1);
						if (rand <= extProbability)
							row++;
						else
							break;
					}
				} else {
					break;
				}
			}
		}
		if (newPoints.size() == 0) {
			return false;
		}
		else {
			r.roadPoints = new ArrayList<Point>();
			for (int i = 0; i < newPoints.size(); i++) {
				r.roadPoints.add(newPoints.get(i));
			}
			return true;
		}
	}

	public boolean isValidRoadPoint(int row, int col, Direction d) {
		if (d == Direction.Right || d == Direction.Left) {
			try {
				boolean oneAbove = matrix[row - 1][col] == -1;
				boolean oneBelow = matrix[row + 1][col] == -1;
				return ! (oneAbove || oneBelow);
			} catch (Exception e) {
				return true;
			}
		} else if (d == Direction.Down || d == Direction.Up) {
			try {
				boolean oneRight = matrix[row][col + 1] == -1;
				boolean oneLeft = matrix[row][col - 1] == -1;
				return ! (oneRight || oneLeft);
			} catch (Exception e) {
				return true;
			}
		} else return false;
	}

	public ArrayList<Pair> getRoadStartPoints(Road r) {
		ArrayList<Pair> list = new ArrayList<Pair>();

		int roadLength = r.roadPoints.size();

		if (roadLength < citySize / 4) {
			// Don't even bother...
			return null;
		}

		int randomCount = Utils.randInt(1, (int)(roadLength / Utils.randDouble(2, 3)));

		ArrayList<Integer> distArray = new ArrayList<Integer>();
		ArrayList<Direction> dirArray = new ArrayList<Direction>();

		Direction[] options;

		if (r.horizontal()) {
			options = new Direction[]{ Direction.Up, Direction.Down };
		} else {
			options = new Direction[]{ Direction.Left, Direction.Right };
		}

		// Load distances and directions.
		for (int i = 0; i < randomCount; i++) {
			int randomStart = Utils.randInt(2, roadLength - 1);
			while (distArray.indexOf(randomStart) > -1) {
				randomStart = Utils.randInt(2, roadLength - 1);
			}
			distArray.add(randomStart);
			dirArray.add(options[Utils.randInt(0, 1)]);
		}

		try {

			for (int j = 0; j < randomCount; j++) {
				Direction d = dirArray.get(j);
				Point start = new Point();
				int x = -1, y = -1;
				if (dirArray.get(j) == Direction.Left || dirArray.get(j) == Direction.Right) {
					x = r.roadPoints.get(0).x;
					if (r.direction == Direction.Up) {
						y = Math.max(r.roadPoints.get(0).y - distArray.get(j), 0);
					} else {
						y = Math.min(r.roadPoints.get(0).y + distArray.get(j), citySize - 1);
					}
				} else {
					y = r.roadPoints.get(0).y;
					if (r.direction == Direction.Left) {
						x = Math.max(r.roadPoints.get(0).x - distArray.get(j), 0);
					} else {
						x = Math.min(r.roadPoints.get(0).x + distArray.get(j), citySize - 1);
					}
				}
				start = new Point(x, y);
				Pair p = new Pair(d, start);
				list.add(p);
			}

		} catch (Exception e) {
			// Move on, we don't need that segment.
		}

		return list;
	}

	public void printMatrix() {
		Utils.printMatrix(matrix, citySize);
	}

	public void outputCity(String filename) {

		// Goal: output to JSON.

		JSONObject city = new JSONObject();

		try {
			city.put("objects", generateProperties());
			city.put("grid", getGrid());
			try{
				String root = new File(".").getCanonicalPath();
				PrintWriter writer = new PrintWriter(root + filename, "UTF-8");
				writer.println(city.toString());
				writer.close();
			} catch (IOException e) {
				// do something
				e.printStackTrace();
			}
		} catch (JSONException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

	}

	public JSONObject generateProperties() {
		JSONObject properties = new JSONObject();

		try {

			properties.put("pop_young", -1);
			properties.put("pop_mid", -1);
			properties.put("pop_old", -1);

			properties.put("toggle1", -1);
			properties.put("toggle2", -1);
			properties.put("toggle3", -1);

			properties.put("slider1", -1);
			properties.put("dockRotation", -1);
			properties.put("gridIndex", -1);
			properties.put("dockID", -1);
			properties.put("IDMax", -1);
			
			properties.put("density", generateDensityArray());

		} catch (JSONException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

		return properties;
	}

	public JSONObject jsonBuilding(int x, int y, int type) {
		JSONObject json = new JSONObject();
		try {
			json.put("x", x);
			json.put("y", y);
			json.put("type", type);
			json.put("rot", Utils.randInt(0, 3) * 90);
			json.put("magnitude", -1);
		} catch (JSONException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

		return json;
	}

	public boolean touchesRoad(int row, int col) {
		// Make sure that one of its 8 neighbors is a road.
		int[] rowChange = {-1, 0, 1};
		int[] colChange = {-1, 0, 1};
		boolean found = false;
		outer:
			for (int r : rowChange) {
				for (int c: colChange) {
					try {
						if (matrix[row + r][col + c] == -1) {
							found = true;
							break outer;
						}
					} catch (Exception e) {
						// Move on, we are in a corner/edge
						found = true;
						break outer;
					}

				}
			}
		return found;
	}
	
	public JSONArray generateDensityArray() {
		JSONArray d = new JSONArray();
		for (int i = 0; i < numDensity; i++) {
			d.put((int)(Math.pow(Utils.randDouble(0, 1), 2) * (maxDensity - 1) + 1));
		}
		System.out.println(d);
		return d;
	}

	public JSONArray getGrid() {

		JSONArray grid = new JSONArray();

		// Loop over matrix and add items to the grid.
		for (int i = 0; i < citySize; i++) {
			for (int j = 0; j < citySize; j++) {
				if (matrix[i][j] == -1)
					grid.put(jsonBuilding(j, i, 6));
				else {
					// Add building only if we touch a road and with 60 % probability.
					if (touchesRoad(i, j) && Utils.randDouble(0, 1) <= buildingProb) {
						grid.put(jsonBuilding(j, i, Utils.randInt(lowType, highType)));
					} else {
						grid.put(jsonBuilding(j, i, -1));
					}
				}

			}
		}

		return grid;

	}

}