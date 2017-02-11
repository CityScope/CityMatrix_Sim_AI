// Barcelona PEV Simulation v0010
// for MIT Media Lab, Changing Place Group, CityScope Project

// by Udgam Goyal <udgam@mit.edu>
// Feb.8th.2015

class Node {
  ArrayList <Road> Roads;
  String roadPtFile;
  PVector point;
  int id;
  Road roadOfNode;
  int activity;
  boolean blue = false;

  Node(PVector point1, int id1, Road road1) {
    point = point1;
    roadOfNode = road1;
    id = id1;
    activity = 0;
  }
  
  Node(PVector point1){
    point = point1;
    activity = 0;
  }
  
  void drawNode(){
    pushMatrix();
    translate(point.x*constantFactor+starting, point.y*constantFactor+starting);
    ellipse(0, 0, 10, 10);
    // draw PEV img
    scale(0.3);
    popMatrix();
  }

  void drawNode(int act) {
    pushMatrix();
    translate(point.x*constantFactor+starting, point.y*constantFactor+starting);
    if (act <= 10){
      fill(0,255,act * 25);
    }
    else if (act > 10 && act < 20){
      fill(0, 255 - ((act-10)*25), 255);
    }
    ellipse(0, 0, 10, 10);
    popMatrix();
  }
}