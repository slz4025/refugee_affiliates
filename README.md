# AI Methods to Aid in Finding New Refugee Resettlement Locations

Christopher Smith, Tina Wu, Sydney Zheng 

{cvsmith,  huachenw,  slzheng}@andrew.cmu.edu

17-537/737 AI Methods for Social Good | Prof. Fei Fang | Carnegie Mellon University

This project is a proof-of-concept system based on combination of real, publically available data, web scraped data, and simulated data for sensitive refugee information that is not publicly available.  The system predicts refugee employment rates for cities based on the synthetic refugee data with a linear regression.  Then, it uses those rates and the publicly available and webscrapped city features to cluster cities with similar resettlement profiles and rank the best cities for refugee resettlement.  The pipeline is constructed such that actual refugee data can be easily substituted for the synthetic data.  It also allows users to assign custom weights by city feature category, so that experts can emphasize the features they think are important.  
