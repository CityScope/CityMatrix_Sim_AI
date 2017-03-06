/**
* Name: DynamicPop
* Author: Arnaud Grignard & Tri Nguyen Huu
* Description: 
* Tags: Tag1, Tag2, TagN
*/

model DynamicPop

/* Insert your model definition here */

global{
	
	geometry shape <- square(1 #km);
	
	int matrix_size <- 18;
	float mpaRadius <- 0.1 #km;
	float growthRate <- 0.0004;
	float carryingCapacity <- 200 #tons;
	float splitThreshold <- 100 #tons;
	float visionRadius <- 0.1#km;
	int initBoatNumber <- 2;
	float boatSpeed <- 2.0;
	float captureCapacity <- 0.08 #tons;
	float captureRadius <- 0.005 #km;
	
	map<string,rgb> colorType <- ["water"::rgb(84,156,245), "land"::rgb(155,118,98), "mpa"::rgb(125,219,142),"fad"::rgb(229,130,64),"fish1"::rgb(53,128,221),"fish2"::rgb(22,69,127)];
	geometry accessZone;
	
	
		
	init {
        do initGrid;
        
        create fishSchool number: 5{
			size <- rnd(100) #tons;
		}
		create boat number: initBoatNumber;
		create testAccessZone number: 1;
	}
	
	action initGrid{
		loop i from:0 to: matrix_size - 1{
			loop j from:0 to: matrix_size - 1{
				waterGrid cell <- waterGrid grid_at { i, j };
				cell.type <- "water";
			}
		}
		
		// decorate
		loop i from:0 to: matrix_size - 1{
			waterGrid cell <- waterGrid grid_at { i , matrix_size - 1 };
			cell.type <- "land";
		}
		loop i from:0 to: matrix_size - 1{
			waterGrid cell <- waterGrid grid_at { i , 8 };
			cell.type <- "land";
			cell <- waterGrid grid_at { i , 7 };
			cell.type <- "land";
			cell <- waterGrid grid_at { i , 9 };
			cell.type <- "land";
		}
		waterGrid cell <- waterGrid grid_at { 5 , 9};
		cell.type <- "mpa";
		cell <- waterGrid grid_at { 2 , 3};
		cell.type <- "mpa";
	//	add to: visibility;
		cell <- waterGrid grid_at { 14 , 8};
		cell.type <- "mpa";		
		cell <- waterGrid grid_at { 4 , 7};
		cell.type <- "fad";
		cell <- waterGrid grid_at { 9 , 5};
		cell.type <- "fad";	
		accessZone <- union(waterGrid where (each.type = "water") collect(each.shape));		
		//write accessZone;
	}
	


	
}



grid waterGrid width:matrix_size height:matrix_size {
	string type;
	float density;
	
	
	aspect base{
	  	draw shape color:colorType["water"] border:#black;	
	  	switch(type){
//	  		match "mpa" {draw circle(2*mpaRadius) color: #white depth: 50 at: location + {0,0,1};}// ne marche pas avec circle ??
	  		match "mpa" {draw 0.004#km around circle(mpaRadius) color: #white depth: 1;}
	  		match "fad" {draw cylinder(0.01 #km,0.01 #km) color: colorType["fad"] at: location + {0,0,1};}	
	  	}
	}
		
   
}

species fishSchool skills:[moving]{
	float size;

	reflex move{
		do wander amplitude: 30;
	}
	
	reflex growth{
		size <- size + growthRate * size * max([0,1 - size / carryingCapacity]);
	}
	
	reflex split when: flip((size - splitThreshold)/(carryingCapacity - splitThreshold)){// the fish school splits when it is too large
		float splitSize <- rnd(0.3)* size;
		size <- size - splitSize;
		create fishSchool {
			size <- splitSize;
			self.location <- myself.location;
		}
	}
	
	aspect base{
		float ratio <- size/carryingCapacity;
		if min(boat accumulate (self distance_to each.location)) < visionRadius {
			draw circle(ratio*0.03 #km) color: colorType["fish2"] ;
		}
		else
		{
			draw  circle(ratio*0.03 #km)  color: colorType["fish1"] ;
		}

	}
	
	aspect school{
		
	}
	
}



species boat skills:[moving]{

	geometry visionBox <- circle(visionRadius);
	
	reflex move{
		list<fishSchool> visibleFishSchools <- fishSchool where (each distance_to self < visionRadius);
	if empty(visibleFishSchools){
			//do wander amplitude: 30 speed: boatSpeed bounds: accessZone;
						do wander speed: 50.0 ;//bounds: accessZone;
		}else{
			do goto target: visibleFishSchools with_max_of (each.size) speed: boatSpeed;
		}
//			
		visionBox <- visionBox at_location location;
	}
	
	
//	reflex capture{
//		fishSchool target <- fishSchool closest_to self;
//		if self distance_to target < captureRadius{
//			target.size <- target.size - captureCapacity;
//			if target.size < 0 {
//				ask target {do die;}
//			}
//		}
//	}
	
	
	aspect base{
		draw circle(0.01#km) color: #orange;// depth: 5 ;
		draw 0.01#km around visionBox color: #orange; 
	}
	
}

species testAccessZone{
	
	aspect base{
		draw accessZone color: #red;
	}
}


experiment Display  type: gui {
	output {
		display oceanView  type:opengl  
		background:#black {
			species waterGrid aspect:base;
			species fishSchool aspect: base;
			species boat aspect: base;
			//species testAccessZone aspect: base;
		}
	}
}


