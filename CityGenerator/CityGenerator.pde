// Andorra PEV Simulation v0010
// for MIT Media Lab, Changing Place Group, CityScope Project

// by Yan Zhang (Ryan) <ryanz@mit.edu>
// Dec.8th.2015

// Generation parameters
int numCities = 1000;
String outputFile = "./out/city_"; // Will have '[Number].json' appended

  // City generation parameters
int totalRoadNum;
float scaleMeterPerPixel = 2.15952; //meter per pixel in processing; meter per mm in rhino
float constantFactor = 100.0;
float starting = 100;

// Property generation parameters
int numDensity = 6;
int maxDensity = 15;
int numTypes = 5;
int roadId = 6;

void setup() {
  int numPadding = ceil(log(numCities) / log(10));
  Generator gen = new Generator();

  int i = 0;
  while (i < numCities) {
    CityOutput city = gen.run();

    JSONObject jsonCity = new JSONObject();

    jsonCity.setJSONArray("grid", getGrid(city.buildings, city.matrix));
    jsonCity.setJSONObject("objects", generateProperties());
    jsonCity.setInt("new_delta", -1);
    
    String filename = outputFile + nf(i, numPadding) + ".json";
    println("Saving file " + filename);
    saveJSONObject(jsonCity, filename);
    i ++;
  }
}

// Generates the metadata included as "objects" in the CityMatrix json spec.
// Most values are -1, to indicate that they don't carry legitimate info
JSONObject generateProperties() {
  JSONObject json = new JSONObject();
  json.setInt("pop_young", -1);
  json.setInt("pop_mid", -1);
  json.setInt("pop_old", -1);

  json.setInt("toggle1", -1);
  json.setInt("toggle2", -1);
  json.setInt("toggle3", -1);

  json.setInt("slider1", -1);
  json.setInt("dockRotation", -1);
  json.setInt("gridIndex", -1);
  json.setInt("dockID", -1);
  json.setInt("IDMax", -1);

  JSONArray density = new JSONArray();
  for (int i = 0; i < numDensity; i ++) {
    density.setInt(i, round(random(0, maxDensity)));
  }
  json.setJSONArray("density", density);

  return json;
}

// Generates a building at the given position with random type and rotation
JSONObject jsonBuilding(int x, int y) {
  JSONObject json = new JSONObject();
  json.setInt("x", x);
  json.setInt("y", y);
  json.setInt("type", round(random(-1, numTypes)));
  json.setInt("rot", round(random(0, 3)) * 90);
  json.setInt("magnitude", -1);

  return json;
}

JSONObject jsonRoad(int x, int y) {
  JSONObject prototype = jsonBuilding(x, y);
  prototype.setInt("type", roadId);
  return prototype;
}

JSONArray getGrid(ArrayList<Building> buildings, int[][] roadMatrix) {
  JSONArray arr = new JSONArray();
  int counter = 0;

  for (Building b : buildings) {
    arr.setJSONObject(counter, jsonBuilding(round(b.position.x), round(b.position.y)));
    counter += 1;
  }

  for (int i = 0; i < roadMatrix.length; i ++) {
    int[] col = roadMatrix[i];
    for (int j = 0; j < col.length; j ++) {
      if (col[j] == -1) {
        arr.setJSONObject(counter, jsonRoad(i, j));
        counter += 1;
      }
    }
  }

  return arr;
}