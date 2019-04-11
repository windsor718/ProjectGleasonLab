import numpy as np
import pandas as pd
import datetime

"""
Sarah, let's do this in a objective way in this time. Objective programming is the manner of programming that makes your code clear and reusable.
In python we define function as "def" keyword. You can call your function whereever you want in your code.
Objective programming is decomposed to two part: 1.) making parts (defining functions) and 2.) assemble parts. 
Here, the parts are:

readFile()
calcStats()
nRMSE
RMSE
R
NSE

and I assemble them in the main() function which will iterate whole reaches.

Why definig functions?
-By defining functions, you will summerize your code lines into one function. 
 This makes your cord a lot more organized. For instance, in this code we define each metric as each function.
 This would be better than writing like:
 #here is rmse
 se = (obs-sim)**2
 mse = se.mean()
 rmse = mse**0.5
 nrmse = rmse/obs.mean()
 return nrmse
 #here is R square
 r = np.corrcoef(obs,sim)[0,1]
 etc.
"""

# general settings
sDate = datetime.datetime(2003,1,1)
tDate = datetime.datetime(2011,1,1)

openFile = "./open_loop.csv"
assimFile = "./assimilated.csv"
gaugeFile = "./gaugeData.csv"

def main():
    # read files
    df_open = readFile(openFile)
    df_assim = readFile(assimFile)
    df_gauge = readFile(gaugeFile)
    # extract reaches that is in the gauge file
    # here, set() is the built in function in Python to extract unique values
    reaches = set(df_gauge.Reach)
    # prepare container (list) to store results for reaches
    out = []
    # let's iterate through
    for reach in reaches:
        stats = calcStats(df_open,df_assim,df_gauge,reach,sDate,tDate)
        out.append(stats)
    # create dataframe from results
    df = pd.DataFrame(np.array(out))
    df.columns = ["reach","rmse_o","rmse_a","nrmse_o","nrmse_a","r_o","r_a","nse_o","nse_a"]
    print(df)
    # save dataframe as a standard csv format.
    df.to_csv("./stats.csv",index=False)

def readFile(filename):
    #Read csv files and create data frame
    #To treat data frame in Python, we use pandas.
    data = pd.read_csv(filename,parse_dates=[0]).set_index("Date")
    return data

def calcStats(df_open,df_assim,df_gauge,reachNum,sDate,tDate):

    #extract data only from the reach specified above
    series_assim = df_assim.loc[:,str(reachNum)]
    #same above
    series_openl = df_open.loc[:,str(reachNum)]
    #extract data only from the reach specified above
    series_gauge = df_gauge[df_gauge.Reach==reachNum].loc[:,"Gauge_flow"]
    #Here, I made a dataframe that summerize simulation results (assimilated and open loop)
    df_all = pd.concat([series_assim,series_openl,series_gauge],axis=1)
    #Let's set column name
    df_all.columns = ["assim","open","gauge"]

    #extracting data only in the range of dates specifed above
    df_target = df_all[sDate:tDate]
    #remove rows that contain NaNs
    df_target = df_target.dropna(how="any")
    #exracting each of them as numpy.ndarray
    assimArray = df_target["assim"].values.astype(np.float64)
    openlArray = df_target["open"].values.astype(np.float64)
    gaugeArray = df_target["gauge"].values.astype(np.float64)
    #calculate metrics for opel loop
    nrmse_o = nRMSE(gaugeArray,openlArray)
    rmse_o = RMSE(gaugeArray,openlArray)
    r_o = corrcoef(gaugeArray,openlArray)
    nse_o = NSE(gaugeArray,openlArray)
    #calculate ones for assim loop
    nrmse_a = nRMSE(gaugeArray,assimArray)
    rmse_a = RMSE(gaugeArray,assimArray)
    r_a = corrcoef(gaugeArray,assimArray)
    nse_a = NSE(gaugeArray,assimArray)
    #store them into the list
    stats = [reachNum,rmse_o,rmse_a,nrmse_o,nrmse_a,r_o,r_a,nse_o,nse_a]

    return stats

def nRMSE(obs,sim):
    se = (obs-sim)**2
    mse = se.mean()
    rmse = mse**0.5
    nrmse = rmse/obs.mean()
    return nrmse

def RMSE(obs,sim):
    se = (obs-sim)**2
    mse = se.mean()
    rmse = mse**0.5
    return rmse

def corrcoef(obs,sim):
    r = np.corrcoef(obs,sim)[0,1]
    return r

def NSE(obs,sim):
    se = (sim-obs)**2
    numerator = se.sum()
    se_m = (obs-obs.mean())**2
    denominator = se_m.sum()
    nse = 1 - (numerator/denominator)
    return nse

if __name__ == "__main__":
    main()
