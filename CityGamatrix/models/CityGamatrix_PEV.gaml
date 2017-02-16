/*
* Name: PEV Model
* Authosr: Arnaud Grignard, Kevin Lyons
* Description: Load CityMatrix view and run PEV agent simulation over time.
* Tags: pev, cityMatrix, gama
*/

model pev_model

import "CityGamatrix.gaml"

global {
	
	// Configurations.
	
	// 1. Vehicle information.
    int nb_pev <- 10 parameter: "Number of PEVs:" category: "Environment";
    float pev_speed <- 15 # km / # h;
    
    // 2. Trip generation..
    list< map<string, unknown> > trip_queue <- [];
    int trip_interval <- 1;
	float maximumTripCount <- 4.0 parameter: "Max Trip Count:" category: "Environment";
	// So, we generate at most 4 jobs every 10 seconds.
	int max_wait_time <- 20 parameter: "Max Wait Time (minutes):" category: "Environment";
	int missed_trips <- 0;
	int completed_trips <- 0;
	int total_trips <- 0;
    file prob <- text_file("../includes/demand.txt");
	list<float> prob_array <- [];
	int total_population;
	list<int> peoplePerFloor <- [5, 8, 16, 16, 23, 59];
	
	// 3. Timing and traffic visualization.
	float step <- 10 # seconds; // visualize ? 1 # seconds : 10 # seconds;
	int current_second update: (time / # second) mod 86400;
	int graph_interval <- 1000;
	int traffic_interval <- 100 # cycles;
	bool visualize;
	matrix traffic;
	matrix waiting;
	string time_string;
	int current_day;
	float box_size;
	date s;
   
	init {
		
		time_string <- "12:00 AM";
		starting_date <- date([2017,1,1,0,0,0]);
		s <- # now;
		
		filename <- '../includes/generator_configurations/city_hope.json';
		
		matrix_size <- 18;
		
		box_size <- 1 # km / matrix_size;
		
		traffic <- 0 as_matrix({ matrix_size, matrix_size });
		
		waiting <- 0 as_matrix({ matrix_size, matrix_size });
 		
		do initGrid;
		
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
        
        // Initialize trip probability array.
        loop r from: 0 to: length(prob) - 1
		{
			add (float(prob[r]) * maximumTripCount) to: prob_array;
		}
        	
        // Create PEV agents and init.
    	create pev number: nb_pev {
    	  	location <- one_of(cityMatrix where (each.type = 6)).location;
    	  	color <- # white;
    	  	speed <- pev_speed;
    	  	status <- "wander";
    	}
        
        ask pev {
        	do findNewTarget;
        }
        
        ask cityMatrix where (each.density > 0) {
        	total_population <- total_population + peoplePerFloor[type] * int(density);
        }
        
        int expected_trips <- int(0.3 * total_population);
        
        write expected_trips * 2 color: # black;
        
        write length(cityMatrix where (each.density > 0)) color: # black;
	}
	
	// Init a road cell.
	action initRoad(cityMatrix cell) {
		cell.type <- surround ? 6 : -1;
		cell.color <- surround ? buildingColors[6] : # black;
		cell.density <- 0.0;
	}
	
	// Accumulate traffic/waiting time on each road cell.
	reflex data_count {
		ask cityMatrix where (each.type = 6) {
			traffic[grid_x , grid_y] <- int(traffic[grid_x , grid_y]) + length(agents_inside(self));
		}
		loop trip over: trip_queue {
			waiting[int(trip['x']), int(trip['y'])] <- int(waiting[int(trip['x']), int(trip['y'])]) + 1;
		}
	}
	
	// Draw traffic heatmap.
	reflex traffic_draw when: every(traffic_interval # cycles) and visualize {
		ask cityMatrix where (each.type = 6) {
			int recent_traffic <- int(traffic[grid_x , grid_y]);
			float ratio <- 2 * float(recent_traffic) / float(max(traffic));
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
		list<cityMatrix> neighbors <- building neighbors_at box_size where (each.type = 6);
		float i <- 2 * box_size;
		loop while: (length(neighbors) = 0 and i < matrix_size / 2) {
			neighbors <- building neighbors_at i where (each.type = 6);
			i <- i + box_size;
		}
		cityMatrix final_cell <- one_of(neighbors);
		if (final_cell = nil) {
			final_cell <- one_of(cityMatrix where (each.type = 6));
		}
		result['x'] <- float(final_cell.location.x);
		result['y'] <- float(final_cell.location.y);
		result['grid_x'] <- int(final_cell.grid_x);
		result['grid_y'] <- int(final_cell.grid_y);
		return;
	}
	
	action completeDay {
		float rate <- float(completed_trips) / float(total_trips);
		write rate color: # black;
		int elapsed_seconds <- int(# now - s);
		write total_trips color: # black;
		write elapsed_seconds color: # black;
		write "Simulation day complete!" color: # black;
		// Output JSON format.
	}
	
	// Manage our trip queue.
	reflex trip_manage when: every(trip_interval # cycles)
	{
		// Stop after 1 day for testing purposes.
		if (time > # day and ! looping) {
			do completeDay;
			do pause;
		}
		
		// Manage any missed trips.
		
		if (length(trip_queue) > 0) {
			loop trip over: trip_queue where (current_second - int(each['start']) > max_wait_time * 60) {
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
	
	action findNewTarget {
		if (status = 'wander') {
			if (length(trip_queue) > 0) {
				do claim;
			} else {
				status <- 'wander';
				target <- one_of(cityMatrix where (each.type = 6 and each.location distance_to self >= matrix_size / 2)).location;
				color <- # white;
			}
		} else if (status = 'pickup') {
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
		map<string, unknown> trip <- trip_queue[0];
		remove trip from: trip_queue;
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
				do pause;
			}
		} else if (status = 'wander' and length(trip_queue) > 0) {
			do claim;
		}
	}
}

experiment Display  type: gui {
	parameter "Heat Map:" var: visualize <- true category: "Grid";
	output {
		
		display cityMatrixView   type:opengl background:#black {	
			species cityMatrix aspect:base;
			species pev aspect:base;	
		}
		
		monitor 'Time' value:time_string refresh:every(1 # minute);
		monitor 'Simulation Day' value: current_day refresh: every(1 # day);
		monitor 'Completion Rate' value: string((completed_trips / (total_trips = 0 ? 1 : total_trips) * 100) with_precision 1) + "%" refresh: every(1 # minute);
		monitor 'Total Trips' value:total_trips refresh: every(1 # minute);
	}
}

experiment Run type: gui {
	parameter "Heat Map:" var: visualize <- false category: "Grid";
}