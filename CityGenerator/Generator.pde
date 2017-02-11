class CityFrame {
  
  public int[][] matrix;
  
  CityFrame(int[][] theMatrix) {
    matrix = theMatrix;
  }
  
}

class Generator {
  
  int maxBuildingDensity = 25;
  int citySize = 16;
  float roadDensity = 0.4;
  ArrayList<Road> queue = new ArrayList<Road>();
  int[][] matrix = new int[citySize][citySize];
  Roads roads = new Roads();
  ArrayList<Building> buildings = new ArrayList<Building>();
  
  PVector right = new PVector(0, 1);
  PVector left = new PVector(0, -1);
  PVector up = new PVector(-1, 0);
  PVector down = new PVector(1, 0);
  
  float extProbability = 0.7;
  
  ArrayList<Road> generateFirstRoads() {
    ArrayList<Road> result = new ArrayList<Road>();
    Road roadOne = new Road();
    roadOne.direction = down;
    roadOne.roadPts = new PVector[citySize];
    for (int row = 0; row < citySize; row++) {
      matrix[row][0] = -1;
      roadOne.roadPts[row] = new PVector(0, row);
    }
    result.add(roadOne);
    Road roadTwo = new Road();
    roadTwo.direction = down;
    roadTwo.roadPts = new PVector[citySize];
    for (int row = 0; row < citySize; row++) {
      matrix[row][citySize - 1] = -1;
      roadOne.roadPts[row] = new PVector(citySize - 1, row);
    }
    result.add(roadTwo);
    Road roadThree = new Road();
    roadThree.direction = right;
    roadThree.roadPts = new PVector[citySize];
    for (int col = 0; col < citySize; col++) {
      matrix[0][col] = -1;
      roadThree.roadPts[col] = new PVector(col, 0);
    }
    result.add(roadThree);
    Road roadFour = new Road();
    roadFour.direction = right;
    roadFour.roadPts = new PVector[citySize];
    for (int col = 0; col < citySize; col++) {
      matrix[citySize - 1][col] = -1;
      roadFour.roadPts[col] = new PVector(col, citySize - 1);
    }
    result.add(roadFour);
    return result;
  }
  
  Road extendInDirection(PVector direction, PVector startPoint) {
    Road resultRoad = new Road();
    resultRoad.direction = direction;
    int rowStart = int(startPoint.y);
    int colStart = int(startPoint.x);
    ArrayList<PVector> newPoints = new ArrayList<PVector>();
    if (direction == right) {
      for (int col = colStart + 1; col < citySize; col++) {
        if (isValidRoadPoint(rowStart, col, right)) {
          matrix[rowStart][col] = -1;
          newPoints.add(new PVector(col, rowStart));
          if (col != citySize - 1 && matrix[rowStart][col + 1] == -1) {
            float rand = random(1);
            if (rand <= extProbability)
              col++;
            else
              break;
          }
        } else {
          break;
        }
      }
    } else if (direction == down) {
      for (int row = rowStart + 1; row < citySize; row++) {
        if (isValidRoadPoint(row, colStart, down)) {
          matrix[row][colStart] = -1;
          newPoints.add(new PVector(colStart, row));
          if (row != citySize - 1 && matrix[row + 1][colStart] == -1) {
            float rand = random(1);
            if (rand <= extProbability)
              row++;
            else
              break;
          }
        } else {
          break;
        }
      }
    } else if (direction == left) {
      // Backwards case...
      for (int col = colStart - 1; col >= 0; col--) {
        if (isValidRoadPoint(rowStart, col, left)) {
          matrix[rowStart][col] = -1;
          newPoints.add(new PVector(col, rowStart));
          if (col != 0 && matrix[rowStart][col - 1] == -1) {
            float rand = random(1);
            if (rand <= extProbability)
              col++;
            else
              break;
          }
        } else break;
      }
      return null;
    } else if (direction == up) {
      // Backwards case...
      for (int row = rowStart - 1; row >= 0; row--) {
        if (isValidRoadPoint(row, colStart, up)) {
          matrix[row][colStart] = -1;
          newPoints.add(new PVector(colStart, row));
          if (row != 0 && matrix[row - 1][colStart] == -1) {
            float rand = random(1);
            if (rand <= extProbability)
              row++;
            else
              break;
          }
        } else break;
      }
      return null;
    }
    if (newPoints.size() == 0)
      return null;
    else {
      resultRoad.roadPts = new PVector[newPoints.size()];
      for (int i = 0; i < newPoints.size(); i++) {
        resultRoad.roadPts[i] = newPoints.get(i);
      }
      return resultRoad;
    }
  }
  
  Boolean isValidRoadPoint(int row, int col, PVector direction) {
    if (direction == right || direction == left) {
      // Check the matrix around [row][col] for any illegal...
      try {
        Boolean oneAbove = matrix[row - 1][col] == -1;
        Boolean oneBelow = matrix[row + 1][col] == -1;
        return ! (oneAbove || oneBelow);
      } catch (Exception e) {
        //println(e);
        return true;
      }
    } else if (direction == down || direction == up) {
      // Check the matrix around [row][col] for any illegal...
      try {
        Boolean oneRight = matrix[row][col + 1] == -1;
        Boolean oneLeft = matrix[row][col - 1] == -1;
        return ! (oneRight || oneLeft);
      } catch (Exception e) {
        return true;
      }
    } else return null;
  }
  
  PVector getOppositeDirection(PVector dir) {
  
    if (dir == right) {
      return left;
    } else if (dir == down) {
      return up;
    }
    
    else return null;
  
  }
  
  void extendAllRoads(Roads roads) {
    
    // Goal - extend all roads randomly with extProbability...
    
    for (Road r: roads.roads) {
    
      float rand = random(1);
      
      if (rand <= extProbability) {
      
        // Do extend in opposite direction...
        
        PVector newDir = getOppositeDirection(r.direction);
        
        if (r.roadPts.length > 0 && r.roadPts[0] != null) {
          Road n = extendInDirection(newDir, r.roadPts[0]);
        }
        
      }
    
    }
    
  }
  
  ArrayList<HashMap<PVector, PVector>> getRoadStartPoints(Road currentRoad) {
    ArrayList<HashMap<PVector, PVector>> result = new ArrayList<HashMap<PVector, PVector>>();
    
    PVector extensionDirection;
      
      if (currentRoad.direction == down || currentRoad.direction == up) {
        PVector[] a = { right, left };
        int rand = (int)random(a.length);
        extensionDirection = a[rand];
      } else {
        PVector[] a = { up, down };
        int rand = (int)random(a.length);
        extensionDirection = a[rand];
      }
    
    int roadLength = currentRoad.roadPts.length;
    
    int randomCount = int(random(1, roadLength/2));
    
    ArrayList<Integer> distArray = new ArrayList<Integer>();
    
    for (int i = 0; i < randomCount; i++) {
      int randomStart = int(random(2, roadLength));
      while (distArray.indexOf(randomStart) > -1) {
        randomStart = int(random(2, roadLength));
      }
      distArray.add(randomStart);
    }
    
    try {
    
      for (int j = 0; j < randomCount; j++) {
        HashMap<PVector, PVector> map = new HashMap<PVector, PVector>();
        if (extensionDirection == right) {
          PVector v = new PVector(currentRoad.roadPts[0].x, min(currentRoad.roadPts[0].y  + distArray.get(j), citySize - 1));
          map.put(extensionDirection, v);
        } else if (extensionDirection == left) {
          PVector v = new PVector(currentRoad.roadPts[0].x, max(currentRoad.roadPts[0].y  - distArray.get(j), 0));
          map.put(extensionDirection, v);
        } else if (extensionDirection == down) {
          PVector v = new PVector(min(currentRoad.roadPts[0].x  + distArray.get(j), citySize - 1), currentRoad.roadPts[0].y);
          map.put(extensionDirection, v);
        } else if (extensionDirection == up) {
          PVector v = new PVector(max(currentRoad.roadPts[0].x  - distArray.get(j), 0), currentRoad.roadPts[0].y);
          map.put(extensionDirection, v);
        }
        result.add(map);
      }
    
    } catch (Exception e) {
      //
    }
    
    return result;
  }
  
  CityOutput run() {
    
    ArrayList<Road> queue = new ArrayList<Road>();
    int[][] matrix = new int[citySize][citySize];
    Roads roads = new Roads();
    ArrayList<Building> buildings = new ArrayList<Building>();
    
    ArrayList<Road> firstFour = generateFirstRoads();
    
    for (Road r : firstFour) {
      Road back = getReverse(r);
      roads.roads.add(r);
      roads.roads.add(back);
    }
    
    queue.add(firstFour.get(0));
    
    queue.add(firstFour.get(2));
    
    int roadCount = (int)(roadDensity * pow(citySize, 2));
    
    while (queue.size() > 0 && roads.roads.size() < roadCount) {
      
      // Get the earliest road...
      
      Road current = queue.get(0);
      
      queue.remove(0);
        
      ArrayList<HashMap<PVector, PVector>> startPoints = getRoadStartPoints(current);
      
      for (HashMap<PVector, PVector> start: startPoints) {
        PVector dir = (PVector)start.keySet().toArray()[0];
        PVector startPoint = start.get(dir);
        Road newRoad = extendInDirection(dir, startPoint);
        if (newRoad != null) {
          Road back = getReverse(newRoad);
          roads.roads.add(newRoad);
          roads.roads.add(back);
          queue.add(newRoad);
        }
      }
    }
    
    extendAllRoads(roads);
    
    println(roads.roads.size());
    
    if (roads.roads.size() <= roadCount/4)
      return run();
      
    printMatrix();
    
    return parseInputMatrix(null, false);
    
  }
  
  Road getReverse(Road road) {
    
    // Return backwards Road
    
    Road result = new Road();
    
    result.roadPts = new PVector[road.roadPts.length];
    
    for (int i = road.roadPts.length - 1; i >= 0; i--) {
      result.roadPts[road.roadPts.length - 1 - i] = road.roadPts[i];
    }
    
    result.direction = road.direction;
    
    return result;
    
  }
  
  void printMatrix() {
    // Assuming square size x size matrix
    print(" \t");
    for (int i = 0; i < citySize; i++) {
      print(i + "\t");
    }
    println();
    for (int i = 0; i < citySize; i++) {
      print(i + "\t");
      for (int j = 0; j < citySize; j++) {
        if (matrix[i][j] == 0)
          print("\t");
        else
          print(matrix[i][j] + "\t");
      }
      println();
    }
  }
  
  String[] directionArray = new String[4];
  int maxDensity = 25;
  
  // Need a method to take in matrix and output Roads and Buildings
  
  void loadDirectionArray() {
    directionArray[0] = "-1,0";
    directionArray[1] = "0,1";
    directionArray[2] = "1,0";
    directionArray[3] = "0,-1";
  }
  
  CityOutput parseInputMatrix(int[][] theMatrix, boolean input) {
    loadDirectionArray();
    //int[][] og = matrix;
    if (input)
      matrix = theMatrix;
    int matrixHeight = matrix.length;
    int [] sample = matrix[0];
    int matrixWidth = sample.length;
    ArrayList<Building> buildings = new ArrayList<Building>(); // Change to "Buildings" class...
    int[][][] roadMatrix = new int[matrixHeight][matrixWidth][4];
    ArrayList<ArrayList<Node>> roadLists = new ArrayList<ArrayList<Node>>();
    for (int row = 0; row < matrixHeight; row++) {
      for (int column = 0; column < matrixWidth; column++) {
        int cell = matrix[row][column];
        if (cell != -1) {
          int density = 0;
          if (cell != 0)
            density = cell;
          else {
            density = (int)random(maxDensity);
            matrix[row][column] = density;
          }
          Building b = constructBuilding(density, column, row);
          buildings.add(b);
        } else if (roadMatrix[row][column][0] == 0 && roadMatrix[row][column][1] == 0 && roadMatrix[row][column][2] == 0 && roadMatrix[row][column][3] == 0) {
          // We have a Road cell. We must determine where this should go and construct Roads accordingly.
          ArrayList<Integer> directions = getAdjacentRoadCells(matrix, row, column);
          for (int i = 0; i < directions.size(); i++) {
            int dir = directions.get(i);
            // Expand along this direction and its negative, if it exists...create Nodes along the way?
            ArrayList<Node> nodes = getRoadNodesAlongDirection(dir, row, column, matrix, roadMatrix);
            int newDir = -1;
            if (dir == 0)
              newDir = 2;
            else if (dir == 1)
              newDir = 3;
            if (newDir != -1) {
              directions.remove(Integer.valueOf(newDir));
              ArrayList<Node> otherNodes = getRoadNodesAlongDirection(newDir, row, column, matrix, roadMatrix);
              nodes = removeDuplicates(combineLists(nodes, otherNodes));
            }
            roadLists.add(nodes);
          }
        }
      }
    }
    writeRoadsToLocalFile(roadLists);
    Roads roads = new Roads();
    roads.addRoadsByRoadPtFile("roads.txt");
    roads = removeIsolatedRoads(roads, matrix, matrixWidth, matrixHeight);
    //printMatrix();
    return new CityOutput(roads, buildings, true, matrix);
  }
  
  Roads removeDeadEnds(Roads roads, int[][] matrix, int w, int h) {
    // Assume that we have already run removeIsolatedRoads...
    // Seeking road where one endpoint shares no others
    Roads res = new Roads();
    for (Road road: roads.roads) {
      PVector startPoint = road.roadPts[0];
      int x1 = (int)startPoint.x, y1 = (int)startPoint.y;
      ArrayList<Integer> adjacentStart = getAdjacentRoadCells(matrix, y1, x1);
      PVector endPoint = road.roadPts[road.roadPts.length - 1];
      int x2 = (int)endPoint.x, y2 = (int)endPoint.y;
      ArrayList<Integer> adjacentEnd = getAdjacentRoadCells(matrix, y2, x2);
      Boolean goodRoad = false;
      for (int i = 1; i < road.roadPts.length - 1; i++) {
        PVector point = road.roadPts[i];
        int x = (int)point.x, y = (int)point.y;
        ArrayList<Integer> adjacent = getAdjacentRoadCells(matrix, y, x);
        if (adjacent.size() > 2 && x != x1 && x != x2 && y != y1 && y != y2) {
          goodRoad = true;
          res.roads.add(road);
          break;
        }
      }
      if (goodRoad == false) {
        if ((adjacentStart.size() == 2 && adjacentEnd.size() == 1) || (adjacentStart.size() == 1 && adjacentEnd.size() == 2))
          goodRoad = false;
        else
          goodRoad = true;
      }
      if (! goodRoad) {
        // Connect locally, by row or column
        for (PVector p : road.roadPts) {
          Road newRoad = roads.findRoadWithLocation(startPoint);
          //println(newRoad.roadPts);
        }
      } else {
        res.roads.add(road);
      }
    }
    return res;
  }
  
  Roads removeIsolatedRoads(Roads roads, int[][] matrix, int w, int h) {
    Roads res = new Roads();
    for (Road road: roads.roads) {
      if (road.roadPts.length > 1) {
        PVector startPoint = road.roadPts[0];
        int x1 = (int)startPoint.x, y1 = (int)startPoint.y;
        ArrayList<Integer> adjacentStart = getAdjacentRoadCells(matrix, y1, x1);
        PVector endPoint = road.roadPts[road.roadPts.length - 1];
        int x2 = (int)endPoint.x, y2 = (int)endPoint.y;
        ArrayList<Integer> adjacentEnd = getAdjacentRoadCells(matrix, y2, x2);
        Boolean fullRoad = (x1 == 0 && x2 == w - 1) || (x2 == 0 && x1 == w - 1) || (y1 == 0 && y2 == h - 1) || (y2 == 0 && y1 == h - 1);
        if (fullRoad || (adjacentStart.size() > 1 || adjacentEnd.size() > 1))
          res.roads.add(road);
        else {
          // Need to check that each other node only has 2 adjacent nodes...
          Boolean goodRoad = false;
          for (int i = 1; i < road.roadPts.length - 1; i++) {
            PVector point = road.roadPts[i];
            int x = (int)point.x, y = (int)point.y;
            ArrayList<Integer> adjacent = getAdjacentRoadCells(matrix, y, x);
            if (adjacent.size() > 2) {
              goodRoad = true;
              res.roads.add(road);
              break;
            }
          }
          if (! goodRoad) {
            /*println("Invalid road detected.");
            println("x1 = " + x1 + ", y1 = " + y1 + ", x2 = " + x2 + ", y2 = " + y2);
            println("startList = " + adjacentStart);
            println("endList = " + adjacentEnd);*/
          }
        }
      }
    }
    return res;
  }
  
  // Temporary solution as we must currently input roads with this specific text file format.
  
  // Refactor - create method to directly convert between node lists and corresponding roads... [KEVIN]
  
  void writeRoadsToLocalFile(ArrayList<ArrayList<Node>> allRoads) {
    PrintWriter output = createWriter("roads.txt");
    for (ArrayList<Node> road: allRoads) {
      output.println("start");
      output.println("one way");
      for (Node n : road)
        output.println(n.point.x + ", " + n.point.y + ", " + n.point.z);
      output.println("end");
      output.println("start");
      output.println("one way");
      road = reverseList(road);
      for (Node n : road)
        output.println(n.point.x + ", " + n.point.y + ", " + n.point.z);
      output.println("end");
    }
    output.flush();
    output.close();
  }
  
  ArrayList removeDuplicates(ArrayList<Node> list) {
    for (int i = 0; i < list.size() - 1; i++) {
      for (int j = i + 1; j < list.size(); j++) {
        if (list.get(i).point.x == list.get(j).point.x && list.get(i).point.y == list.get(j).point.y)
          list.remove(j);
      }
    }
    return list;
  }
  
  ArrayList combineLists(ArrayList one, ArrayList two) {
    ArrayList res = new ArrayList();
    for (Object o : one)
      res.add(o);
    for (Object n : two)
      res.add(n);
    return res;
  }
  
  ArrayList reverseList(ArrayList input) {
    ArrayList newList = new ArrayList();
    for (int i = input.size() - 1; i >= 0; i--)
      newList.add(input.get(i));
    return newList;
  }
  
  Building constructBuilding(float density, float x, float y) {
    return new Building(density, x, y);
  }
  
  ArrayList<Integer> getAdjacentRoadCells(int[][] matrix, int row, int column) {
    ArrayList<Integer> returnArray = new ArrayList<Integer>();
    try {
      if (matrix[row - 1][column] == -1)
        returnArray.add(0);
    } catch (Exception e) {
    }
    try {
      if (matrix[row][column + 1] == -1)
        returnArray.add(1);
    } catch (Exception e) {
    }
    try {
      if (matrix[row + 1][column] == -1)
        returnArray.add(2);
    } catch (Exception e) {
    }
    try {
      if (matrix[row][column - 1] == -1)
        returnArray.add(3);
    } catch (Exception e) {
    }
    return returnArray;
  }
  
  ArrayList<Node> getRoadNodesAlongDirection(int dir, int row, int column, int[][] inputMatrix, int[][][] roadMatrix) {
    String moveString = directionArray[dir];
    String[] split = moveString.split(",");
    int rowIncrement = Integer.parseInt(split[0]);
    int colIncrement = Integer.parseInt(split[1]);
    int r = row, c = column;
    int matrixHeight = inputMatrix.length; //<>// //<>// //<>// //<>// //<>//
    int [] sample = inputMatrix[0]; //<>// //<>// //<>// //<>// //<>//
    int matrixWidth = sample.length;
    ArrayList<Node> list = new ArrayList<Node>();
    Node first = constructNode(column, row);
    list.add(first);
    r += rowIncrement;
    c += colIncrement;
    while (r >= 0 && r < matrixHeight && c >= 0 && c < matrixWidth) {
      if (inputMatrix[r][c] == -1 && roadMatrix[r][c][dir] != 1) { //<>// //<>// //<>// //<>// //<>//
        roadMatrix[r][c][dir] = 1;
        Node thisNode = constructNode(c, r);
        list.add(thisNode);
        r += rowIncrement;
        c += colIncrement;
      } else
        break;
    }
    if (dir == 1 || dir == 7)
      return reverseList(list);
    else
      return list;
  }
  
  Node constructNode(int x, int y) {
    return new Node(new PVector(x, y, 0));
  }
  
  int[][] fillMatrix(String fileName) {
    String[] rows = loadStrings(fileName);
    // Check length of integers. Assume good validation.
    int matrixHeight = rows.length;
    String[] firstRow = rows[0].split(",");
    int matrixWidth = firstRow.length;
    int[][] returnMatrix = new int[matrixHeight][matrixWidth];
    for (int row = 0; row < matrixHeight; row++) {
      String[] thisRow = rows[row].split(",");
      for (int col = 0; col < matrixWidth; col++) {
        //println(row + " " + col);
        returnMatrix[row][col] = Integer.parseInt(thisRow[col].trim());
      }
    }
    return returnMatrix;
  }
  
}