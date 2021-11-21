
# Setting up OctoPi url and apikey settings file

Please copy settings.json.template to settings.json and fill in
the information such as url and apikey.  The settings.json should not
be added to git due to sensitive nature of the apikey and it is being
ignored by use of .gitignore file.


# Example of collect topography data

Below command will run an experiment where the data is saved to the output (-o)
file and the url and apikey are gotten from the settings.json file:

$ ./run-experiment.py -j settings.json -t -o /home/pi/3d-rf-scanner/data/topographydata.csv


# Example of collecting RF data

Below command will run experiment to collect RF data using in input (-i) file that specifies
the topography and generating an output (-o) file where the RF data is saved:

$ ./run-experiment.py -j settings.json -r -i /home/pi/3d-rf-scanner/data/topographydata.csv -o /home/pi/3d-rf-scanner/data/rfdata.csv

# Example of plotting data

Below command will generate a plot from input (-i) data and save it to the plot (-p) output file,
the options --topography and --rf are used to specify what data is being provided, and thus
what plot to generate:

$ ./plot-data.py --topography -i /home/pi/3d-rf-scanner/data/topographydata.csv -p /home/pi/3d-rf-scanner/plots/topography.pdf
$ ./plot-data.py --rf -i /home/pi/3d-rf-scanner/data/rfdata.csv -p /home/pi/3d-rf-scanner/plots/rf.pdf

