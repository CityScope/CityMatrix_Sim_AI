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
	
	string dir <- '../includes/output_2/'; // Directory with output JSON files. 
	list<string> files <- folder(dir) select (string(each) contains "json");
	int index <- 0;
	
	
	init {
		
		surround <- true;
		
	}
	
	reflex changeCity when: every(10 # cycles) and index < length(files) {
		filename <- dir + files[index];
		do initGrid;
		do setEdges;
		index <- index + 1;
		write length(files) color: # black;
		if (index = length(files)) {
			do pause;
			do die;
			// Done with this round.
		}
	}

}

experiment Display type: gui {
	output {
		
		display cityMatrixView type:opengl background: # black autosave: true {	
			species cityMatrix aspect:base;
		}
	}
}