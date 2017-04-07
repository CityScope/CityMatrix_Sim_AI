/**
* Name: CityGamatrix_Visual
* Author: Kevin Lyons
* Description: Model to visualize a city matrix after a PEV simulation has been completed. This will show the city configuration and heat map of traffic/wait time values.
* Tags: pev, cityMatrix, gama, visual, heat map
*/

model CityGamatrix_Visual

// Import generic matrix loader.
import "CityGamatrix.gaml"

global {
	
	string dir <- '../includes/small_output/'; // Directory with output JSON files. Must have trailing /.
	list<string> files <- folder(dir) select (string(each) contains "json");
	int index <- 0;
	string raw_file;
	int fleet;
	int total;
	int complete;
	int missed;
	int total_wait;
	int population;
	int mode <- 0; // 0 = large, 1 = traffic, 2 = wait
	map<point, list<float>> heatMap;
	string viewString <- "City";
	float max_traffic <- 0.0;
	float max_wait <- 0.0;
	
	init {
		
		step <- 1 # second;
		
		matrix_size <- 16;
		surround <- false;
		
		raw_file <- files[index];
		filename <- dir + files[index];
		
		do initGrid;
		do setEdges;
		do setProps;
		do loadMap;
		
		index <- 1;
		mode <- 1;
		
	}
	
	action loadMap {
		loop cell over: (list<unknown>(matrixData["grid"]) where (each["type"] = 6)) {
			list<float> l <- [float(cell["data"]["traffic"]), float(cell["data"]["wait"])];
			point p <- {int(cell["x"]), int(cell["y"]), 0};
			heatMap[p] <- l;
			if l[0] > max_traffic {
				max_traffic <- l[0];
			}
			if l[1] > max_wait {
				max_wait <- l[1];
			}
		}
	}
	
	reflex addColor when:every(4000 # cycles) {
		if (mode = 0) {
			viewString <- "City";
			mode <- 1;
			// Nothing.
			do drawColors(0.0, true);
		} else if (mode = 1) {
			viewString <- "Traffic";
			// Add traffic heatmap.
			do drawColors(max_traffic, false);
			mode <- 2;
		} else if (mode = 2) {
			viewString <- "Wait";
			// Add wait heatmap.
			do drawColors(max_wait, false);
			mode <- 0;
		}
 	}
	
	action drawColors(float m, bool clear) {
		ask cityMatrix where (each.type = 6) {
			if (clear) {
				color <- rgb(40,40,40);
			} else {
				point p <- {grid_x, grid_y, 0};
				int val <- int(heatMap[p][mode - 1]);
				float ratio;
				if (val = 0) {
					ratio <- 0.0;
				} else {
					ratio <- 2.5 * float(val) / m;
				}
				write ratio color: # black;
		    	int b <- int(max([0, 255*(1 - ratio)]));
		    	int r <- int(max([0, 255*(ratio - 1)]));
		    	int g <- 255 - b - r;
		    	color <- rgb(r, g, b, 0.7); // Added alpha value for some transparency.
			}
		}
	}
	
	reflex changeCity when:every(12000 # cycles) {
		if (index = length(files)) {
			do pause;
			do die;
			// Done with this round.
		}
		raw_file <- files[index];
		filename <- dir + files[index];
		do initGrid;
		do setEdges;
		do setProps;
		do loadMap;
		index <- index + 1;
	}
	
	action setProps {
		fleet <- int(matrixData["objects"]["data"]["fleet"]);
		total <- int(matrixData["objects"]["data"]["total"]);
		complete <- int(matrixData["objects"]["data"]["completed"]);
		missed <- int(matrixData["objects"]["data"]["missed"]);
		population <- int(matrixData["objects"]["data"]["population"]);
		
		loop cell over: (list<unknown>(matrixData["grid"]) where (each["type"] = 6)) {
			total_wait <- total_wait + int(cell['data']['wait']);
		}
	}

}

experiment PNGDisplay type: gui {
	// float minimum_cycle_duration <- 1.0 #ms;
	output {
		
		display cityMatrixView2 autosave: true refresh:every(4000 #cycles) type:opengl background: # black autosave: true camera_pos: {500,234234,12423000} camera_look_pos: {250.0,500.0,0.0} camera_up_vector: {0,0.7071067811865476,0.7071067811865475} {	
			species cityMatrix aspect:base;
			graphics "text" {
               draw "PEV Fleet: " + string(fleet) color: # white font: font("Helvetica", 24, #bold) at: { -600, 100};// perspective: true;
               draw "Total Trips: " + string(total) color: # white font: font("Helvetica", 24, #bold) at: { -600, 200};// perspective: false;
               draw "Complete: " + string(complete) color: # white font: font("Helvetica", 24, #bold) at: { -600, 300};// perspective: false;
               draw "Missed: " + string(missed) color: # white font: font("Helvetica", 24, #bold) at: { -600, 400};// perspective: false;
               draw "Total Wait: " + string(total_wait) color: # white font: font("Helvetica", 24, #bold) at: { -600, 500};// perspective: false;
               draw "Population: " + string(population) color: # white font: font("Helvetica", 24, #bold) at: { -600, 600};// perspective: false;
               draw "View: " + viewString color: # white font: font("Helvetica", 24, #bold) at: { -600, 700};// perspective: false;
               draw "File: " + raw_file color: # white font: font("Helvetica", 20, #bold) at: { -600, 1050};// perspective: false;
            }
		}
	}
}