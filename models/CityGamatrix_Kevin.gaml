/**
* Name: PEV Model
* Authosr: Arnaud Grignard, Kevin Lyons
* Description: Load CityMatrix view and run PEV agent simulation over time.
* Tags:  pev, cityMatrix, gama
*/

model pev_model

import "CityGamatrix.gaml"

global {
	
	// Configurations.
	
	// 1. Vehicle information.
    int nb_pev <- 10 parameter: "Number of PEVs:" category: "Environment";
    float pev_speed <- 15 # km / # h;
    
    // 2. Job generation..
    list< map<string, unknown> > job_queue <- [];
    int job_interval <- 10;
	int maximumJobCount <- 10 parameter: "Max Job Count:" category: "Environment";
	int max_wait_time <- 20 parameter: "Max Wait Time (minutes):" category: "Environment";
	int missed_jobs <- 0;
	int completed_jobs <- 0;
	int total_jobs <- 0;
    file prob <- text_file("../includes/demand.txt");
	list<float> prob_array <- [];
	float max_prob;
	
	// 3. Timing and traffic visualization.
	float step <- 1 # second;
	int current_second update: (time / # second) mod 86400;
	int graph_interval <- 1000;
	int traffic_interval <- 60 * 60 # cycles;
	bool do_traffic_visualization;
	matrix traffic;
	string time_string;
	int current_day;
   
	init {
		
		time_string <- "12:00 AM";
		starting_date <- date([2017,1,1,0,0,0]);
		
		filename <- '../includes/mobility_configurations/diagonal.json';
		
		matrix_size <- 18;
		
		traffic <- 0 as_matrix({ matrix_size, matrix_size });
 		
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
        
        // Initialize job probability array.
        loop r from: 0 to: length(prob) - 1
		{
			add (float(prob[r]) * maximumJobCount / 60) to: prob_array;
		}
		
		max_prob <- max(prob_array);
        	
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
	}
	
	// Init a surrounding road cell.
	action initRoad(cityMatrix cell) {
		cell.type <- surround ? 6 : -1;
		cell.color <- surround ? buildingColors[6] : # black;
		cell.density <- 0.0;
	}
	
	// Accumulate traffic on each road cell.
	reflex traffic_count when: do_traffic_visualization {
		ask cityMatrix where (each.type = 6) {
			traffic[grid_x , grid_y] <- int(traffic[grid_x , grid_y]) + length(agents_inside(self));
		}
	}
	
	// Draw traffic heatmap.
	reflex traffic_draw when: every(traffic_interval # cycles) and do_traffic_visualization {
		ask cityMatrix where (each.type = 6) {
			float minimum <- 0.0;
			float maximum <- float(max(traffic));
			int recent_traffic <- int(traffic[grid_x , grid_y]);
			float ratio <- 2 * (float(recent_traffic) - minimum) / (maximum - minimum);
	    	int b <- int(max([0, 255*(1 - ratio)]));
	    	int r <- int(max([0, 255*(ratio - 1)]));
	    	int g <- 255 - b - r;
	    	color <- rgb(r, g, b, 0.7); // Added alpha value for some transparency.
		}
	}
	
	// Update time string for visualization.
	reflex update_time when: every(1 # minute) {
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
	
	// Update days for visualization.
	reflex update_days when: every(1 # day) {
		current_day <- current_day + 1;
	}
	
	// Find a random location on map, skewed toward areas with higher building denisty.
	action findLocation(map<string, float> result) {
		float m <- max(density_array);
		float random_density <- rnd(1, m - 1);
		list<cityMatrix> the_cells <- cityMatrix where (each.density > random_density);
		loop while: length(cells) = 0 {
			random_density <- rnd(1, m - 1);
		}
		bool found <- false;
		cityMatrix cell <- one_of(the_cells);
		list<cityMatrix> neighbors;
		int i <- 0;
		loop while: (found = false) {
			neighbors <- cell neighbors_at i where (each.type = 6);
			found <- length(neighbors) != 0;
			i <- i + 1;
			if (i > matrix_size / 3) {
				break;
			}
		}
		if (found) {
			point road_cell <- one_of(neighbors).location;
			result['x'] <- float(road_cell.x);
			result['y'] <- float(road_cell.y);
			return;
		} else {
			point road_cell <- one_of(cityMatrix where (each.type = 6)).location;
			result['x'] <- float(road_cell.x);
			result['y'] <- float(road_cell.y);
			return;
		}
	}
	
	// Manage our job queue.
	reflex job_manage when: every(job_interval # cycles)
	{
		// Stop after 1 day for testing purposes.
		if (time > # day and ! looping) {
			do pause;
		}
		
		// Manage any missed jobs.
		loop job over: job_queue where (current_second - int(each['start']) > max_wait_time) {
			missed_jobs <- missed_jobs + 1;
			total_jobs <- total_jobs + 1;
			remove job from: job_queue;
		}
		
		// Add new jobs.
		float p <- prob_array[current_second];
		float r <- rnd(0, max_prob);
		if (r <= p)
		{
			int job_count;
			if (floor(r * job_interval) = 0)
			{
				job_count <- flip(r * job_interval) ? 1 : 0;
			} else
			{
				job_count <- int(floor(r * job_interval));
			}
			if (job_count > 0)
			{
				loop i from: 0 to: job_count - 1 {
					map<string, unknown> m;
					m['start'] <- current_second;
					map<string, float> pickup;
					do findLocation(pickup);
					m['pickup.x'] <- float(pickup['x']);
					m['pickup.y'] <- float(pickup['y']);
					map<string, float> dropoff;
					do findLocation(dropoff);
					m['dropoff.x'] <- float(dropoff['x']);
					m['dropoff.y'] <- float(dropoff['y']);
					add m to: job_queue;
				}
			} 
		}

	}
}

species pev skills: [moving] {
	point target;
	rgb color;
	string status;
	map<string, unknown> pev_job;
	
	aspect base {
		draw circle(10) at: location color: color;
	}
	
	action findNewTarget {
		if (status = 'wander') {
			if (length(job_queue) > 0) {
				do find;
			} else {
				status <- 'wander';
				target <- one_of(cityMatrix where (each.type = 6 and each.location distance_to self >= matrix_size / 2)).location;
				color <- # white;
			}
		} else if (status = 'pickup') {
			status <- 'dropoff';
			float d_x <- float(pev_job['dropoff.x']);
			float d_y <- float(pev_job['dropoff.y']);
			target <- { d_x, d_y, 0.0};
			color <- # pink;
		} else if (status = 'dropoff') {
			completed_jobs <- completed_jobs + 1;
			total_jobs <- total_jobs + 1;
			status <- 'wander';
			target <- one_of(cityMatrix where (each.type = 6 and each.location distance_to self >= matrix_size / 2)).location;
			color <- # white;
		}
	}
	
	// Pops job from front of queue and assigns to this PEV.
	action find {
		map<string, unknown> job <- job_queue[0];
		remove job from: job_queue;
		pev_job <- job;
		status <- 'pickup';
		float p_x <- float(job['pickup.x']);
		float p_y <- float(job['pickup.y']);
		target <- { p_x, p_y, 0.0};
		color <- # orange;
	}
	
	// Allows PEV to move through our matrix.
	reflex move {
		do goto target: target on: cityMatrix where (each.type = 6) speed: speed;
		if (target = location) {
			do findNewTarget;
		} else if (status = 'wander') {
			if (length(job_queue) > 0) {
				do find;
			}
		}
	}
}

experiment Display  type: gui {
	parameter "Heat Map:" var: do_traffic_visualization <- true category: "Grid";
	output {
		display cityMatrixView   type:opengl background:#black {	
			species cityMatrix aspect:base;
			species pev aspect:base;	
		}
		
		monitor 'Time' value:time_string refresh:every(1 # minute);
		monitor 'Simulation Day' value: current_day refresh: every(1 # day);
		monitor 'Completion Rate' value: string((completed_jobs / (total_jobs = 0 ? 1 : total_jobs) * 100) with_precision 1) + "%" refresh: every(1 # minute);
		monitor 'Total Jobs' value:total_jobs refresh: every(1 # minute);
	}
}

experiment Display_Light type: gui {
	parameter "Heat Map:" var: do_traffic_visualization <- false category: "Grid";
	output {
		monitor 'Time' value:time_string refresh:every(1 # minute);
		monitor 'Simulation Day' value: current_day refresh: every(1 # day);
		monitor 'Completion Rate' value: string((completed_jobs / (total_jobs = 0 ? 1 : total_jobs) * 100) with_precision 1) + "%" refresh: every(1 # minute);
		monitor 'Total Jobs' value:total_jobs refresh: every(1 # minute);
	}
}
