// Barcelona PEV Simulation v0010
// for MIT Media Lab, Changing Place Group, CityScope Project

// by Kevin Lyons <kalyons@mit.edu>
// Oct.21st.2016

class Building {
  Road nearestRoad; // Represents nearest Road to building, from which we're going to 
  PVector nearestPt;
  float density;
  float probability;
  PVector position;
  
  Building(float d, float x, float y){
    density = d;
    position = new PVector(x,y,0);
    nearestRoad = null;
    nearestPt = null;
    probability = 0;
  }

  
  
}