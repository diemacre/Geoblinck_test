# Nearest shop to client
This program calculates the number of users whose near_shop field relates to a store which is one
that is not located in his/her country. And then it assigns to each client the closest shop to his/her home location (there could be several shops with the same location, but only one is assigned)

# Installation
For python 2:
pip install -r requirements.txt
For python 3:
pip3 install -r requirements.txt

# Test
Run: py.test

# Future development -> Change structure 
The process of calculating the nearest_shop for each of the clients takes around 13 seconds to compute. This is not reliable and scalable. I tried to optimized using 3 different approaches but I did only optimized a little (2 seconds). What I will do for this kind of problem will be having a raster map that contains cells (the resolution will need to be studied) each one with its shops. Then for each client, we can calculate her/his corresponding cell in the raster map and first check the distance to the shops in that cell and if there are no shops, start checking the neighbor cells in rings until a shop is found.

# Future Scalation and automation of the program
For the first time, we need to calculate for all the clients which are their nearest shop from all the shops and save them. However, if this needs to be scaled and a new client is added we only need to check for that client if its location is in the database and if it is not then the nearest is calculated.
On the other hand, if a new store is added and has a different location the whole database will need to be updated.
Also, the testing file should be modified or making anther for these new clients/stores and automate the process so if it passes the tests then it will make the calculation and if not, therefore it won't.

# Support
Diego Martín Crespo
dmartinc2009@gmail.com