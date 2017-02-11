// Barcelona PEV Simulation v0010
// for MIT Media Lab, Changing Place Group, CityScope Project

// by Kevin Lyons <kalyons@mit.edu>
// Oct.21st.2016 //<>// //<>//

class CityOutput {
  
  Roads roads;
  ArrayList<Building> buildings;
  Boolean isValid;
  int[][] matrix;
  
  CityOutput(Roads roadsIn, ArrayList<Building> buildingsIn, Boolean validIn, int[][] matrixIn) {
    roads = roadsIn;
    buildings = buildingsIn;
    isValid = validIn;
    matrix = matrixIn;
  }
  
}