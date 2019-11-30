# Traffic-Assignment
Traffic-Assignment is a repository for static traffic assignment python code. Currently, the program can solve the static traffic assignment problem using user equilibrium (UE) and stochastic user equilibrium (SUE) for the city network. The solution can be achieved both using MSA and Frank-Wolfe algorithm.



# How to run traffic assignment
1. #### Clone the repository on a local directory  

2. #### Data Preparation : 
Navigate to the network folder (e.g., Sioux Falls network) and check the demand and network file format. For more network data, please refer to [TNTP](https://github.com/bstabler/TransportationNetworks). Note that the data format used by the current script is different from the data available on this website. Use script "dataPreparation.py" to create a network suitable to this script.

3. #### Running the script :
Open the script "ta.py". Set the "inputLocation"  to the directory where the network is stored. Use the following methods to perform operations:

```
assignment(loading, algorithm, accuracy = default, maxIter=default)
```
 - *Loading* can be "deterministic" or "stochastic". The deterministic loading uses all or nothing assignment whereas stochastic loading uses Dial's algorithm to produce auxiliary flows.
 
 - *algorithm* can be "MSA" or "FW". MSA refers to method of successive averages and FW refers to Frank-Wolfe method to compute the step size.
 
 - *accuracy* is the tolerance parameter used to stop the algorithm when the solution is close to UE or SUE. The default value is set of 0.01 (i.e., 1%)
 
 - *maxIter* is the maximum number of iterations to stop the program if the program is not able to reach the equilibrium solution for a given accuracy. The default value of 10000.
 
 
```
writeUEresults()
```
 - Use this method to write the UE results after the assignment is finished. You can open the output file in notepad or MS excel. 
 
 
# How to cite
If you are using this program for your research, you can cite this code as below:
```
Pramesh Kumar. (2019, October 10). prameshk/Traffic-Assignment: Static Traffic Assignment using User Equilibrium and Stochastic User Equilibrium- Python Code (Version 2.0). Zenodo. http://doi.org/10.5281/zenodo.3479554
```

```
@software{pramesh_kumar_2019_3479554,
  author       = {Pramesh Kumar},
  title        = {{prameshk/Traffic-Assignment: Static Traffic 
                   Assignment using User Equilibrium and Stochastic
                   User Equilibrium- Python Code}},
  month        = oct,
  year         = 2019,
  publisher    = {Zenodo},
  version      = {2.0},
  doi          = {10.5281/zenodo.3479554},
  url          = {https://doi.org/10.5281/zenodo.3479554}
}
```


## Questions
Feel free to send an email to [kumar372@umn.edu](kumar372@umn.edu) if you have questions or concerns.


## Future releases
Future releases will have an implementation of other traffic assignment algorithms such as Gradient Projection, Origin-based assignment, and Algorithm B. 



