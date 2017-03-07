# CityGamatrix
Agent-Based Model of the CityMatrix using latest Gama platform.

## Instructions

#### A. City Generation

Generate a given amount of cities. In order to do this, you can run the `CityGenerator.java` script and set the numberCities variable as you wish. Two sub-notes:
  - This script requires the local JAR libarary for JSON processing, which can be found [here](http://stackoverflow.com/questions/8997598/importing-json-into-an-eclipse-project).
  - **You must create the a directory named `out` before running this script that is one directory above your working `CityGenerator.java` file.**

This will produce JSON city configuration files in the `../out/` directory.

#### B. Single City Run

If you want to run a single JSON city file and extract results, use the following steps with the `CityGamatrix_PEV.gaml` file.

1. Set the `output_dir` variable in the `global` section to be the directory (relative or absolute path) where you want to save your output JSON.
2. Set the `filename` variable in the `global init` section to be the relative (or absolute) path to the JSON file you want.
3. Click the "Display" experiment on the top toolbar for a visual of the city simulation. Click the "Run" experiment if you simply want to output JSON.
4. If you would like, you can change the PEV fleet size/maximum wait time with the parameters on the left side of the scren. The current default values are 50 PEV's and 20 minutes of wait time.
5. When you are ready, press the play button at the top to run the day-long simulation.

This will produce an output file with the form `city_{ID}_output.json` in the `output_dir` you chose earlier.

#### C. Batch Simulation Run

If you want to run many JSON city configurations in the GAMA simulation, you should use the batch simulation option. Use the following steps with the `CityGamatrix_PEV.gaml` file.

1. Make sure all of the input JSON files are in the same directory with no other conflicting JSON files. Set this directory to the `input_dir` variable.
2. Set the `output_dir` variable in the `global` section to be the directory (relative or absolute path) where you want to save your output JSON files.
3. Click the "Batch" option on the top toolbar. When you are ready, press the play button to iterate through all the files.

On average, each city takes about 90 seconds. This will produce 1 output file for every input file given, with a similar structure of `city_{ID}_{Date Timestamp}.json` for clarity purposes.

#### D. Visualizing Outputs

Once you have a set of output JSON files, it is helpful to generate PNG screenshots of the cities to view traffic and wait time heatmaps, as well as the general road layout. You can use the `CityGamatrix_Visual.gaml` file to do this.

1. Set the `dir` variable to be the directory containing all of the output JSON files you want to visualize.
2. Click the `PNGDisplay` experiment on the top toolbar and press play.

This will produce 3 .png images for each city and output them in the `models/snapshots/` directory of your current working Gama project. The 3 images correspond to the following 3 views.

- **City**: a simple image of the city layout road network and relative building heights.
- **Traffic**: a heatmap of relative traffic at each road cell, reporesenting the number of PEV's that passed over that road segment during their travels.
- **Wait**: a heatmap of relative wait time at each road cell, representing the number of minutes that trips generated at the segment had to wait from the time they requested a job to the time they were picked up.

# CityGenerator
Processing script that generates different configuration of the CityMatrix.
