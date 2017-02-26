/*
* Name: CityGamatrix_PEV
* Authosr: Arnaud Grignard, Kevin Lyons
* Description: Load CityMatrix view and run PEV agent simulation over time. Also has batch run functionality.
* Tags: pev, cityMatrix, gama
*/

model CityGamatrix_PEV

// Import generic matrix loader.
import "CityGamatrix.gaml"

global {
	
	// Configurations.
	
	// 0. Directory strings!!! Need to include trailing slash.
	string input_dir <- '../includes/input_2/';
	string output_dir <- '../includes/output_2/';
	
	// 1. Vehicle information.
    int nb_pev <- 50 parameter: "Number of PEVs:" category: "Environment";
    float pev_speed <- 15 # km / # h;
    
    // 2. Trip generation..
    list< map<string, unknown> > trip_queue <- [];
    int trip_interval <- 1;
	float maximumTripCount; // <- 6.0 parameter: "Max Trip Count:" category: "Environment";
	// Number of jobs generated every trip_interval cycles;
	int max_wait_time <- 20 parameter: "Max Wait Time (minutes):" category: "Environment";
	int missed_trips <- 0;
	int completed_trips <- 0;
	int total_trips <- 0;
    file prob <- text_file("../includes/demand.txt");
	list<float> prob_array <- [];
	int total_population;
	list<int> peoplePerFloor <- [5, 8, 16, 16, 23, 59];
	map<point, list<map<string, float>> > buildingMap;
	float scaleFactor <- 1370.0; // Helps us map expected jobs to actual 10 seconds intervals. Subject to change if necessary.
	
	// 3. Timing and traffic visualization.
	float step <- 10 # seconds; // visualize ? 1 # seconds : 10 # seconds;
	int current_second update: (time / # second) mod 86400;
	int graph_interval <- 1000;
	int traffic_interval <- 100 # cycles;
	bool visualize;
	matrix traffic;
	matrix waiting;
	float max_traffic <- 10000.0;
	float max_wait <- 25000.0;
	string time_string;
	int current_day;
	float box_size;
	date s;
	
	// 4. Batch properties.
	bool did_finish <- true;
	bool day_done <- false;
	list<string> file_list <- folder(input_dir) select (string(each) contains "json");
	bool isBatch <- false;
	string raw_filename;
   
	init {
		
		if (isBatch) {
			raw_filename <- replace(filename, '.json', ''); 
			filename <- input_dir + filename;
		} else {
			filename <- './../includes/cityIO.json';
		}
		
		write "Current file: " + filename color: # black;
		
		time_string <- "12:00 AM";
		starting_date <- date([2017,1,1,0,0,0]);
		s <- # now;
		
		matrix_size <- 18;
		
		box_size <- 1 # km / matrix_size;
		
		traffic <- 0 as_matrix({ matrix_size, matrix_size });
		waiting <- 0.0 as_matrix({ matrix_size, matrix_size });
 		
		do initGrid;
		
		do setEdges;
		
		// Get total population and trip statistics.
        ask cityMatrix where (each.density > 0) {
        	total_population <- total_population + peoplePerFloor[type] * int(density);
        }
        int expected_trips <- int(0.3 * total_population * 2);
        maximumTripCount <- float(expected_trips) / scaleFactor;
        
        // Initialize trip probability array.
        loop r from: 0 to: length(prob) - 1 {
			add (float(prob[r]) * maximumTripCount) to: prob_array;
		}
        	
        // Create PEV agents and init.
    	create pev number: nb_pev {
    	  	location <- one_of(cityMatrix where (each.type = 6)).location;
    	  	color <- # white;
    	  	speed <- pev_speed;
    	  	status <- "wander";
    	}
    	
    	// Map buildings to their respective nearest roads.
    	do mapBuildings; 
        
        // Set all PEV's with some initial wandering target.
        ask pev {
        	do findNewTarget;
        }
	}
	
	// Map buildings to their respective nearest roads.
	action mapBuildings {
		loop building over: cityMatrix where (each.density > 0) {
			cityMatrix nearest_neighbor <- (cityMatrix where (each.type = 6)) closest_to building;
			float d <- building.location distance_to nearest_neighbor.location;
			list<cityMatrix> n <- (cityMatrix where (each.type = 6 and each.location distance_to building.location = d));
			buildingMap[{building.grid_x, building.grid_y, 0}] <- [];
			loop r over: n {
				map<string, float> result;
				result['x'] <- float(r.location.x);
				result['y'] <- float(r.location.y);
				result['grid_x'] <- int(r.grid_x);
				result['grid_y'] <- int(r.grid_y);
				add result to: buildingMap[{building.grid_x, building.grid_y, 0}];
			}
		}
	}
	
	// Accumulate traffic/waiting time on each road cell.
	reflex data_count {
		ask cityMatrix where (each.type = 6) {
			traffic[grid_x , grid_y] <- int(traffic[grid_x , grid_y]) + length(agents_inside(self));
		}
		loop trip over: (trip_queue where (each['status'] = 'waiting' or each['status'] = 'waiting_active')) {
			// Every 10 seconds, add 1/6 of a minute to the queue...
			waiting[int(trip['x']), int(trip['y'])] <- float(waiting[int(trip['x']), int(trip['y'])]) + float(1/6);
		}
	}
	
	// Draw traffic heatmap.
	reflex traffic_draw when: every(traffic_interval # cycles) and visualize {
		ask cityMatrix where (each.type = 6) {
			int recent_traffic <- int(traffic[grid_x , grid_y]);
			float ratio <- 2 * float(recent_traffic) / max_traffic;
	    	int b <- int(max([0, 255*(1 - ratio)]));
	    	int r <- int(max([0, 255*(ratio - 1)]));
	    	int g <- 255 - b - r;
	    	color <- rgb(r, g, b, 0.7); // Added alpha value for some transparency.
		}
	}
	
	// Update time string for visualization.
	reflex update_time when: every(1 # minute) and visualize {
		string hour;
		if (current_date.hour = 0) {
			hour <- "12";
		} else if (current_date.hour < 12) {
			hour <- string(current_date.hour);
		} else if (current_date.hour = 12) {
			hour <- "12";
		} else {
			hour <- string(current_date.hour - 12);
		}
		string minute <- (current_date.minute < 10 ? "0" + string(current_date.minute) : string(current_date.minute));
		string type <- current_date.hour > 11 ? "PM" : "AM";
		time_string <- 	hour + ":" + minute + " " + type;
	}
	
	// Update day for visualization.
	reflex update_days when: every(1 # day) and visualize {
		current_day <- current_day + 1;
	}
	
	// Find a random location on map, skewed toward areas with higher building denisty.
	action findLocation(map<string, float> result) {
		float random_density <- rnd(1, max_density);
		cityMatrix building <- one_of(cityMatrix where (each.density >= random_density));
		map<string, float> r <- one_of(buildingMap[{building.grid_x, building.grid_y, 0}]);
		result['x'] <- float(r['x']);
		result['y'] <- float(r['y']);
		result['grid_x'] <- int(r['grid_x']);
		result['grid_y'] <- int(r['grid_y']);
		return;
	}
	
	//Output simulation data to JSON.
	action completeDay {
		
		// Add data dict with traffic and wait to each ROAD cell.
		int a <- (matrix_size = 18) ? 1 : 0;
		loop c over: cells where (each["type"] = 6) {
			int x <- 15 - int(c["x"]) + a;
			int y <- int(c["y"]) + a;
			map<string, int> data;
			data["traffic"] <- int(traffic[x, y]);
			data["wait"] <- int(waiting[x, y]);
			c["data"] <- data;
		}
		
		// Now, add all properties to data dict in objects
		map<string, unknown> final_data;
		final_data["completed"] <- completed_trips;
		final_data["missed"] <- missed_trips;
		final_data["total"] <- total_trips;
		final_data["finished"] <- did_finish ? 1 : 1;
		final_data["fleet"] <- nb_pev;
		final_data["max_wait"] <- max_wait_time;
		final_data["trip_prob"] <- maximumTripCount;
		final_data["runtime"] <- int(# now - s);
		final_data["total_wait"] <- int(sum(waiting));
		final_data["population"] <- total_population; // Latest add...
		final_data["max_traffic"] <- max_traffic;
		final_data["max_wait"] <- max_wait;
		objects["data"] <- final_data;
		
		// Write final result to JSON.
		map<string, unknown> result;
		result["grid"] <- cells;
		result["objects"] <- objects;
		json_file copy <- json_file(output_dir + raw_filename + '_output.json', result);
		save copy;
		
		day_done <- true;
		write "Day complete." color: # black;
		write # now color: # black;
		
		if (! isBatch) {
			do pause;
		}
	}
	
	// Manage our trip queue.
	reflex trip_manage when: every(trip_interval # cycles)
	{
		// Stop after 1 day.
		if (time > # day and ! looping) {
			do completeDay;
		}
		
		// Remove any missed trips.
		if (length(trip_queue) > 0) {
			loop trip over: trip_queue where (current_second - int(each['start']) > max_wait_time * 60 and each['status'] = 'waiting') {
				missed_trips <- missed_trips + 1;
				total_trips <- total_trips + 1;
				remove trip from: trip_queue;
			}
		}
		
		// Add new trips.
		float r <- rnd(0, maximumTripCount);
		if (r <= prob_array[current_second]) {
			int trip_count <- round(r);
			if (trip_count > 0)
			{
				loop times: trip_count {
					map<string, unknown> m;
					m['status'] <- 'waiting';
					m['start'] <- current_second;
					map<string, float> pickup;
					do findLocation(pickup);
					m['pickup.x'] <- float(pickup['x']);
					m['pickup.y'] <- float(pickup['y']);
					m['x'] <- int(pickup['grid_x']);
					m['y'] <- int(pickup['grid_y']);
					map<string, float> dropoff;
					do findLocation(dropoff);
					m['dropoff.x'] <- float(dropoff['x']);
					m['dropoff.y'] <- float(dropoff['y']);
					add m to: trip_queue;
				}
			} 
		}

	}
}

species pev skills: [moving] {
	point target;
	string status;
	map<string, unknown> pev_trip;
	
	aspect base {
		draw circle(10) at: location color: color;
	}
	
	// Find a new destination after previous one completed.
	action findNewTarget {
		if (status = 'wander') {
			if (length((trip_queue where (each['status'] = 'waiting'))) > 0) {
				do claim;
			} else {
				status <- 'wander';
				target <- one_of(cityMatrix where (each.type = 6 and each.location distance_to self >= matrix_size / 2)).location;
				color <- # white;
			}
		} else if (status = 'pickup') {
			remove pev_trip from: trip_queue;
			status <- 'dropoff';
			target <- { float(pev_trip['dropoff.x']), float(pev_trip['dropoff.y']), 0.0};
			color <- # pink;
		} else if (status = 'dropoff') {
			completed_trips <- completed_trips + 1;
			total_trips <- total_trips + 1;
			status <- 'wander';
			target <- one_of(cityMatrix where (each.type = 6 and each.location distance_to self >= matrix_size / 2)).location;
			color <- # white;
		}
	}
	
	// Pops trip from front of queue and assigns to this PEV.
	action claim {
		map<string, unknown> trip <- (trip_queue where (each['status'] = 'waiting'))[0];
		trip['status'] <- 'waiting_active';
		pev_trip <- trip;
		status <- 'pickup';
		target <- { float(trip['pickup.x']), float(trip['pickup.y']), 0.0};
		color <- # orange;
	}
	
	// Allows PEV to move through our matrix.
	reflex move {
		path p <- goto(target: target, on: cityMatrix where (each.type = 6), speed: speed, return_path: true);
		if (target = location) {
			do findNewTarget;
		} else if (length(p.segments) = 0) {
			// Bad road.
			ask world {
				write "Bad road detected. Heading to " + string(myself.target) + "." color: # black;
				did_finish <- false;
				do completeDay;
				do die;
			}
		} else if (status = 'wander' and length((trip_queue where (each['status'] = waiting))) > 0) {
			do claim;
		}
	}
}

// Batch experiment container.
experiment Batch type: batch until: day_done {
	parameter var: isBatch <- true;
	parameter "Filename" var: filename among: file_list;
}

// Experiment for visualization purposes.
experiment Display  type: gui {
	parameter "Heat Map:" var: visualize <- true category: "Grid";
	output {
		
		display cityMatrixView type:opengl background:#black {	
			species cityMatrix aspect:base;
			species pev aspect:base;
			// Add autosave: true to the display.
		}
		
		// Several monitors for reference.
		monitor 'Time' value:time_string refresh:every(1 # minute);
		monitor 'Simulation Day' value: current_day refresh: every(1 # day);
		monitor 'Completion Rate' value: string((completed_trips / (total_trips = 0 ? 1 : total_trips) * 100) with_precision 1) + "%" refresh: every(1 # minute);
		monitor 'Total Trips' value:total_trips refresh: every(1 # minute);
	}
}

// Experiment for personal day long testing.
experiment Run type: gui {
	parameter "Heat Map:" var: visualize <- false category: "Grid";
}