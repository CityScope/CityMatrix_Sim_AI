/**
* Name: JSON File Loading
* Author:  Arnaud Grignard
* Description: Initialize a grid from a JSON FIle. 
* Tags:  load_file, grid, json
*/

model json_loading   

global {
	file JsonFile <- json_file("../includes/cityIO.json");
    map<string, unknown> c <- JsonFile.contents;
    map<int,rgb> peopleColors <-[0::#blue, 1::#yellow, 2::#red,3::#blue, 4::#yellow, 5::#red];
    map<int,rgb> buildingColors <-[0::rgb(189,183,107), 1::rgb(189,183,107), 2::rgb(189,183,107),3::rgb(230,230,230), 4::rgb(230,230,230), 5::rgb(230,230,230)];
    map<int,geometry> peopleShape <-[0::square(0.5), 1::circle(0.25), 2::triangle(0.5)];
    file andorra_texture <- file('../images/andorrABM.png');	
    int nb_pedestrians <- 0 max: 10 min: 0 parameter: "Pedestrians:" category: "Environment";
    int nb_pev <- 0 max: 10 min: 0 parameter: "PEVs:" category: "Environment";
    int nb_car <- 1 max: 10 min: 0 parameter: "Cars:" category: "Environment";
   

	init { 
		list<map<string, int>> cells <- c["grid"];
        loop mm over: cells {                 
            cityMatrix cell <- cityMatrix grid_at {mm["x"],mm["y"]};
            cell.type <-int(mm["type"]);
            if(int(cell.type) = 6){
            	  cell.color <-rgb(40,40,40);
            	  do initAgent(cell);       	  
            }else{
              if(int(cell.type) = -1){
            	   cell.color <- (flip(0.5) ? #green : #gray);
            	  }if(int(cell.type) = 0 or int(cell.type) = 1 or int(cell.type) = 2){
            	  cell.color <-buildingColors[int(cell.type)];    	  
            	 } 
            }
        }

        ask people{
         do findNewTarget;
        }
	} 
	
	action initAgent (cityMatrix cell){
		 create people number:nb_pedestrians{
            	  	id <-int(cell.type);
            	  	shape <- geometry(peopleShape[0]);
            	  	location <- cell.location + {rnd(-2.0,2.0),rnd(-2.0,2.0)};
            	  	color <- peopleColors[rnd(2)];
            	  	speed <-0.1;	
            	  }
            	  create people number:nb_pev{
            	  	id <-int(cell.type);
            	  	shape <- geometry(peopleShape[1]);
            	  	location <- cell.location + {rnd(-2.0,2.0),rnd(-2.0,2.0)};
            	  	color <- peopleColors[rnd(2)];	
            	  	speed <-0.2;
            	  }
            	  create people number:nb_car{
            	  	id <-int(cell.type);
            	  	shape <- geometry(peopleShape[2]);
            	  	location <- cell.location + {rnd(-2.0,2.0),rnd(-2.0,2.0)};
            	  	color <- peopleColors[rnd(2)];	
            	  	speed <-0.3;
            	  } 
	} 
	
	
} 

grid cityMatrix width:16  height:16 {
	int type;
	rgb color;
	
   	aspect base{	
   		 draw shape color:color  border:#black;	
    }
    aspect depth{
	  draw shape color:color depth:6-type;		
	}
	
	aspect andorra{
	  draw shape color:rgb(0,0,0,125) depth:10-type;		
	}
}

species people skills:[moving]{
	int id;
	point target;
	rgb color;
	aspect base{
	  draw shape at:location color:color;		
	}
		
	action findNewTarget{
		if(id =6){
        		target <- one_of(cityMatrix where (each.type = 6)).location ;//+ {rnd(-2.0,2.0),rnd(-2.0,2.0)}; 		
        	}

	}
	reflex move{
		do goto target:target on:cityMatrix where (each.type = 6) speed: speed;
		if (target = location){
			write "target = lcoation" + self;
			do findNewTarget;
		}
	}
}

experiment Display  type: gui {
	output {

		display cityMatrixView   type:opengl background:#black {	
			species cityMatrix aspect:base;
			species people aspect:base;
			/*species cityMatrix aspect:base position:{400,30,0.1} size:{0.4,0.4,0.4};
			species people aspect:base position:{400,30,0.1} size:{0.4,0.4,0.4};	
			
			graphics table{
				//CITYMATRIX
				int feetSize <-75;
				draw box(100/16,100/16,feetSize) at:{0,0,-feetSize} color:#white;
				draw box(100/16,100/16,feetSize) at:{0,100,-feetSize} color:#white;
				draw box(100/16,100/16,feetSize) at:{100,0,-feetSize} color:#white;
				draw box(100/16,100/16,feetSize) at:{100,100,-feetSize} color:#white;
				draw square(100) at:{50,50,-feetSize*0.75} color:#gray;
				//ANDORRA
				draw box(100/16,100/16,feetSize) at:{300,0,-feetSize} color:#white;
				draw box(100/16,100/16,feetSize) at:{600,100,-feetSize} color:#white;
				draw box(100/16,100/16,feetSize) at:{600,0,-feetSize} color:#white;
				draw box(100/16,100/16,feetSize) at:{300,100,-feetSize} color:#white;
				draw rectangle(300,100) texture:andorra_texture.path at:{450,50,0} color:#gray;
				draw rectangle(300,100)  at:{450,50,-feetSize*0.75} color:#gray;
			}*/	
		}
	}
}
