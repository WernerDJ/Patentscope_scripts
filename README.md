# Patentscope_scripts
Ppython scripts to obtain meaningful data from the exported csv search results list
<hr />
The PatentscopeApp_Inv.py is the Applicants Inventors network code. It traces the movements of Inventors between different applicants, showing in a circular network diagram the technology transfer that happens between companies and/or universities when their inventors move from one workplace to the next. Applicants_Inventors_Network.png is the output from the result list used in this example. 
<hr />
<br>
ParallelCoords_Patentscope.py creates a parallel coordinates graphic of the 6 most frequent IPC groups (A61B, C12K, etc) by year, in this case  the years are restricted between 2007 and 2023 in the line: year_range = range(2007, 2023)
The graphic Parallel_Coords.png show the expected result
