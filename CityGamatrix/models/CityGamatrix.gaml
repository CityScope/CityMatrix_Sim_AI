/**
* Name: GamaMatrix
* Author: Arnaud Grignard, Kevin Lyons
* Description: This is a template for the CityMatrix importation in GAMA. The user has the choice to instantiate the grid either from a local file ( onlineGrid = false) or from the cityscope server ( onlineGrid = true)
* The grid is by default loaded only once but it can be loaded every "refresh" cycle by setting (dynamicGrid= true).
* Tags: grid, load_file, json
* Residential (0:L, 1:M, 2: S) 
* Office: (L:3, M:4, S: 5) - Road: 6 - Parking/Green Area : -1
*/

model GamaMatrix

global {
	
	geometry shape <- square(1 #km);
	
    map<string, unknown> matrixData;
    map<int,rgb> buildingColors <-[0::rgb(189,183,107), 1::rgb(189,183,107), 2::rgb(189,183,107),3::rgb(230,230,230), 4::rgb(230,230,230), 5::rgb(230,230,230),6::rgb(40,40,40)];
    map<int,rgb> buildingGAMAColors <-[0::rgb(244,165,40), 1::rgb(244,165,40), 2::rgb(217,72,33),3::rgb(217,72,33), 4::rgb(22,94,147), 5::rgb(22,94,147),6::rgb(0,0,0)];
    map<int,rgb> buildingMinimalColors <-[0::#white, 1::#white, 2::#white,3::#white, 4::#white, 5::#white,6::#black];
    list<map<string, unknown>> cells;
    map<string, unknown> objects;
	list<float> density_array;
	float max_density;
	
	bool onlineGrid <- false parameter: "Online Grid:" category: "Grid";
	bool dynamicGrid <- false parameter: "Update Grid:" category: "Grid";
	int refresh <- 100 min: 1 max:1000 parameter: "Refresh rate (cycle):" category: "Grid";
	bool surround <- false parameter: "Surrounding Road:" category: "Grid";
	bool looping <- false parameter: "Continuous Demo:" category: "Environment";
	int matrix_size <- 16;
	string filename <- './../includes/general_input/city_ryan.json' parameter: "filename" category: "Environment"; // Default option in case no other file is selected.
	bool first <- true;
	bool gama_view<-false;
	
	init {
        do initGrid;
	}
	
	action initGrid{
		if(onlineGrid = true){
		  matrixData <- json_file("http://45.55.73.103/table/citymatrix_ml").contents;
	    }
	    else{
	      matrixData <- json_file(filename).contents;
	    }	
		cells <- matrixData["grid"];
		objects <- matrixData["objects"];
		density_array <- matrixData["objects"]["density"];
		//density_array <- [30.0, 20.0, 10.0, 25.0, 15.0, 5.0];
		max_density <- max(density_array);
		int a <- (matrix_size = 18) ? 1 : 0;
		loop c over: cells {
			int x <- int(c["x"]) + a;
			int y <- int(c["y"]) + a;
            cityMatrix cell <- cityMatrix grid_at { x, y };
            if (! first and c["type"] = cell.type) {
            	// Same type on update - don't change color.
            } else {
            	if (int(c["type"]) = 7) {
            		// Camera  boy edge case. Assume road.
            		cell.type <- 6;
            	} else {
            		cell.type <- int(c["type"]);
            	}
            	if (gama_view = true) {
            	  cell.color <- (cell.type = -1) ? # gray : buildingMinimalColors[cell.type];	
            	} else {
            	  	cell.color <- (cell.type = -1) ? # gray : buildingColors[cell.type];	
            	}
            }
            cell.density <- (cell.type = -1 or cell.type= 6) ? 0.0 : density_array[cell.type];
        }
	}
	
	reflex updateGrid when: ((cycle mod refresh) = 0) and (dynamicGrid = true) {
		first <- false;	
		do initGrid;
	}
	
	action setEdges {
		// Add surrounding road if surround = true, else add nothing.
		
		// Top edge.
		loop i from: 0 to: matrix_size - 1 {
			cityMatrix cell <- cityMatrix grid_at { i , 0 };
			do initRoad(cell);
		}
		
		// Bottom edge.
		loop i from: 0 to: matrix_size - 1 {
			cityMatrix cell <- cityMatrix grid_at { i , matrix_size - 1 };
			do initRoad(cell);
		}
		 
		// Left edge.
		loop i from: 0 to: matrix_size - 1 {
			cityMatrix cell <- cityMatrix grid_at { 0 , i };
			do initRoad(cell);
		}
		
		// Right edge.
		loop i from: 0 to: matrix_size - 1 {
			cityMatrix cell <- cityMatrix grid_at { matrix_size - 1 , i };
			do initRoad(cell);
		}
	}
	
	// Init a road cell.
	action initRoad(cityMatrix cell) {
		cell.type <- surround ? 6 : -1;
		cell.color <- surround ? buildingColors[6] : # black;
		cell.density <- 0.0;
	}
}

grid cityMatrix width:matrix_size height:matrix_size {
	int type;
	rgb color;
	float density;
	
	aspect flat{
	  draw shape color:color border:#black;		
	}
		
    aspect base{
	  draw shape color:color depth:density / max(density_array) * 4 * (1 # km / matrix_size) border:#black;		
	}
	
	cityMatrix closestCell(list<cityMatrix> n) {
		float minDistance <- float(matrix_size);
		cityMatrix result <- nil;
		loop c over: n {
			float d <- sqrt((grid_x - c.grid_x)^2 + (grid_y - c.grid_y)^2);
			if (d < minDistance) {
				minDistance <- d;
				result <- c;
			}
		}
		return result;
	}
}


experiment Display  type: gui {
	output {
		display cityMatrixView  type:opengl background:#black {
			species cityMatrix aspect:base;
		}
	}
}

experiment DisplayKeystone  type: gui {
	output {
		display cityMatrixView  rotate:-90 type:opengl fullscreen:0 
		keystone: [{-0.0345,0.1425,0.0},{0.0235,1.02654,0.0},{0.9859,1.02793,0.0},{1.041536,0.148045,0.0}]
		background:#black {
			species cityMatrix aspect:flat;
		}
	}
}