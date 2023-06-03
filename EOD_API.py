from eodhd import APIClient
import os
import urllib, json
import pandas as pd 
import numpy as np 
import datetime
import yfinance as yf


#EOD API TO AWS 
#API - DATA - PROCESS - RATIOS & SCREENER DATAFRAME


#EOD API 
YOUR_API_KEY="647950fbb96692.96123493"
api = APIClient(YOUR_API_KEY)



#URL LIST

#"ExchangeList":f"https://eodhistoricaldata.com/api/exchanges-list/?api_token={YOUR_API_KEY}",
#"TickerInExchange":f"https://eodhistoricaldata.com/api/exchange-symbol-list/{EXCHANGE_CODE}?api_token={YOUR_API_KEY}",
#"CompanyOverview":f"https://eodhistoricaldata.com/api/fundamentals/{ticker}?api_token={YOUR_API_KEY}"}


def read_url(url=" "):
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())
    df=pd.DataFrame.from_dict(data)
    return df

dfExchange=read_url(url=f"https://eodhistoricaldata.com/api/exchanges-list/?api_token={YOUR_API_KEY}")
                    
exchangeList = dfExchange["Code"].tolist()
dfGlobalTicker=[]
for exchangeCode in exchangeList[:2]:
    dfTicker = read_url(url=f"https://eodhistoricaldata.com/api/exchange-symbol-list/{exchangeCode}?api_token={YOUR_API_KEY}&fmt=json")
    dfGlobalTicker.append(dfTicker)

dfGlobalTicker=pd.concat(dfGlobalTicker,axis=0, ignore_index=True)
tickerTypes=dfGlobalTicker["Type"].unique().tolist()
dfStockTickers = dfGlobalTicker[dfGlobalTicker["Type"]=="Common Stock"]



def EOD_Data(exchange=[],tickerList=[]):
  
    allDataKeys=['General', 'Highlights', 'Valuation', 'SharesStats', 'Technicals',
           'SplitsDividends', 'AnalystRatings', 'Holders', 'InsiderTransactions',
           'ESGScores', 'outstandingShares', 'Earnings', 'Financials']

    #Key Sub Classification
    #ESGScource - Outdated 
    companyInfoDataKeys = ['General', 'Highlights', 'Valuation', 'SharesStats', 'Technicals', 'AnalystRatings']
    splitsDividendKey = ["SplitsDividend"]
    shareholdersKey = ["Holders"]
    iTransactionKey = ["InsiderTransactions"]
    osSharesKey = ['outstandingShares']
    earningsKey = ["Earnings"]
    financialsKey = ["Financials"]

    companyInfo = [] 
    officersInfo = []
    listingsInfo = []
    shareholderInfo = []
    shareOutstandInfo = []
    insiderTransacInfo = []
    earningHist = []
    earningTrend  = []
    earningAnnual = [] 
    statements = ['Balance_Sheet','Cash_Flow','Income_Statement']
    periods = ["quarterly","yearly"]
    annualFS=[]
    quarterFS=[]
    noData = {}
    noDataDf = []
    count = 1

    for ticker in tickerList:
        url=f"https://eodhistoricaldata.com/api/fundamentals/{ticker}.{exchange}?api_token={YOUR_API_KEY}"
        response = urllib.request.urlopen(url)
        data = json.loads(response.read())


        #Company Info
        dfCI = []
        for key in companyInfoDataKeys:
            dfCI.append(pd.DataFrame.from_dict([data[key]]))

        dfCompanyInfo=pd.concat(dfCI,axis=1)
        companyInfo.append(dfCompanyInfo)


        #Company Financials 
        dfF= []
        for period in periods:
            for statement in statements:
                dfF.append(pd.DataFrame.from_dict(data['Financials'][statement][period]))

            dfFS=pd.concat(dfF,axis=1,ignore_index=True).transpose()
            dfFS["Ticker"]=ticker
            if period == "quarterly":
                  quarterFS.append(dfFS)
                  dfF = []
            else:
                  annualFS.append(dfFS)
                  dfF = []
    return companyInfo,annualFS,quarterFS


def convert_to_space_upper(text):
    import re
    if re.match(r'^[A-Za-z0-9_]+$', text):
        if re.match(r'^[a-z]+(_[a-z]+)*$', text):
            return text.replace('_', ' ').upper()
        else:
            return re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', text).upper()
    else:
        return text.upper()
    
def concatList(clist=[]):
    df=pd.concat(clist,ignore_index=True)
    df.columns = df.columns.map(convert_to_space_upper)
    return df



companyInfo,annualFS,quarterFS = EOD_Data(exchange="US",tickerList=["AAPL","MSFT"])
dfF=concatList(annualFS)
dfQ=concatList(quarterFS)
dfC=concatList(companyInfo)


#dfOff = Management - RAW DATA - API 
#dfSh = Shareholder- RAW DATA - API 

#dfM = MetricRef DataFrame - MANUAL CSV CREATED 
#dfScols = Screnner Columns for AgGrid



#VARIABLES

sector = 'SECTOR'
industry = "INDUSTRY"
coName = "NAME"
year = "YEAR"
marketCap='MARKET CAPITALIZATION'
updatedTicker="YF TICKER"
country = "COUNTRY"
Date ="DATE"
roic = 'ROIC'
revenue = 'TOTAL REVENUE'
rev_type = "TOTAL REVENUE"
fcf = 'FREE CASH FLOW'
gm = 'GROSS PROFIT MARGIN'
ebitda_m = 'EBITDA MARGIN'
npm = 'NET PROFIT MARGIN'
nprofit = "NET INCOME"
gp = "GROSS PROFIT"
ebitda = "EBITDA"
assets = "TOTAL ASSETS"
liab="TOTAL LIAB"
equity="TOTAL STOCKHOLDER EQUITY"
cfo = "TOTAL CASH FROM OPERATING ACTIVITIES"
cfi = "TOTAL CASHFLOWS FROM INVESTING ACTIVITIES"
cff = "TOTAL CASH FROM FINANCING ACTIVITIES"
d_e = 'DEBT TO EQUITY'
c_r = 'CURRENT RATIO'
pe = 'PRICE TO EARNINGS RATIO (TTM)'
pcf = 'PRICE TO FREE CASH FLOW (TTM)'
prev = "PRICE TO REVENUE RATIO (TTM)"
st1 = "IS"
st2 = "CF"
st3 = "Ratio"
st4 = "Ratio"
IS = "IS"
BS = "BS"
CF = "CF"
OT = "Ratio "
mScale="MARKET CAP SCALE"
indexUS=["S&P500","NASDAQ100","DOW30"]
indexIND = ["SECTORIAL INDEX","MARKET CAP INDEX"]















#Changing Quarterly Financials to USD
def QFUSD(dFF=[],dfM=[]):
    dFF.columns = dFF.columns.str.lstrip()
    dFF["DATE"]=pd.to_datetime(dFF["DATE"],errors="coerce")
   
    dFF["YEAR"]=dFF["DATE"].dt.year
    dFF["QUARTER"]= dFF["DATE"].dt.quarter
    dFF["MONTH"] = dFF["DATE"].dt.month
 
    sd="1980-1-1"
    ed = datetime.date.today()


    currencyList=dFF["CURRENCY SYMBOL"].unique().tolist()
    currencyList.remove("USD")
    currencyList.remove(np.nan)
    currencies=currencyList
    currencyTick = []
    for currency in currencies:
        currencyTick.append(currency+"USD=X")

    currencyData = yf.download(currencyTick,start=sd,end=ed)
    exRates=currencyData["Close"]
    exQ = exRates.resample("Q").mean().reset_index()
    exQ["YEAR"] = exQ["Date"].dt.year
    exQ["QUARTER"] = exQ["Date"].dt.quarter
    exM =  exRates.resample("M").mean().reset_index()
    exM["YEAR"] = exM["Date"].dt.year
    
    exM["MONTH"] = exM["Date"].dt.month

    dFFex=dFF[dFF["CURRENCY SYMBOL"].isin(currencies)][["TICKER","DATE","YEAR","MONTH","QUARTER","CURRENCY SYMBOL"]]

    zlist = []
    for currency in currencies:
        cCode=currency+"USD=X"

        x=dFFex[dFFex["CURRENCY SYMBOL"]==currency]

        yFp = exQ[[cCode,"YEAR","QUARTER"]]
        yFp.columns = ["ExRate_forperiod","YEARfp","QUARTERfp"]


        yAd = exM[[cCode,"YEAR","MONTH"]]
        yAd.columns=["ExRate_asonDate","YEARas","MONTHas"]

        z=pd.merge(x,yFp,left_on=["YEAR","QUARTER"],right_on=["YEARfp","QUARTERfp"])
        zqq=pd.merge(z,yAd,left_on=["YEAR","MONTH"],right_on=["YEARas","MONTHas"])

        zlist.append(zqq)

    erT=pd.concat(zlist)


    erT.drop(["YEAR","MONTH","QUARTER","CURRENCY SYMBOL","YEARfp","QUARTERfp","YEARas","MONTHas"],axis=1,inplace=True)

    dFFex=pd.merge(dFF,erT,left_on=["TICKER","DATE"],right_on=["TICKER","DATE"])

    for met in dfM[dfM["Statement"]=="BS"]["title"]:
                dFFex[met]=dFFex[met]*dFFex["ExRate_asonDate"]

    for met in dfM[dfM["Statement"].isin(["CF","IS"])]["title"]:
                dFFex[met]=dFFex[met]*dFFex["ExRate_forperiod"]

    usdDF=dFF[~dFF["CURRENCY SYMBOL"].isin(currencies)]

    usdF=pd.concat([dFFex,usdDF])

    usdF.loc[usdF["CURRENCY SYMBOL"]=="USD","ExRate_asonDate"]=1
    usdF.loc[usdF["CURRENCY SYMBOL"]=="USD","ExRate_forperiod"]=1
    
    usdF.loc[usdF["CURRENCY SYMBOL"].isin([np.nan]),"ExRate_asonDate"]=1
    usdF.loc[usdF["CURRENCY SYMBOL"].isin([np.nan]),"ExRate_forperiod"]=1
    
    usdF.dropna(subset=["ExRate_forperiod"],inplace=True)
    
    return usdF


#Changing Annual Financials to USD
def AFUSD(dFF=[],dfM=[]):
    
    dFF.columns = dFF.columns.str.lstrip()
    
    dFF["DATE"]=pd.to_datetime(dFF["DATE"],errors="coerce")
    dFF["YEAR"] = dFF["DATE"].dt.year
    dFF["MONTH"] =  dFF["DATE"].dt.month
    dFF.loc[dFF["MONTH"]<6,"YEAR"] = dFF.loc[dFF["MONTH"]<6,"YEAR"] - 1
    dFF["YEAR BS"] = dFF["DATE"].dt.year
    dFF["LAST YEAR"]=dFF["YEAR BS"]-1
   
    
    
    currencyList=dFF["CURRENCY SYMBOL"].unique().tolist()
    currencyList.remove("USD")
    currencyList.remove(np.nan)
    currencies=currencyList
    currencyTick = []
    for currency in currencies:
        currencyTick.append(currency+"USD=X")


    sd="1980-1-1"
    ed = datetime.date.today()

    currencyData = yf.download(currencyTick,start=sd,end=ed)
    exRates=currencyData["Close"]
    exY=exRates.resample("Y").mean().reset_index()
    exY["Year"] = exY["Date"].dt.year

    exM=exRates.resample("M").mean().reset_index()
    exM["Year"] = exM["Date"].dt.year
    exM["Month"]=exM["Date"].dt.month

    dFFex=dFF[dFF["CURRENCY SYMBOL"].isin(currencies)][["TICKER","DATE","YEAR","YEAR BS","LAST YEAR","MONTH","CURRENCY SYMBOL"]]


    zlist = []
    for currency in currencies:
        cCode=currency+"USD=X"

        x=dFFex[dFFex["CURRENCY SYMBOL"]==currency]

        y=exY[[cCode,"Year"]]
        yL=exY[[cCode,"Year"]]
        m = exM[[cCode,"Year","Month"]]
        m.columns = ["ExRate_asonDate","YEARexasd","MONTHexasd"]

        y.columns = ["ExRate_currentYear","YEARexCY"]
        yL.columns = ["ExRate_lastYear","YEARexLY"]

        z=pd.merge(x,m,left_on=["YEAR BS","MONTH"],right_on=["YEARexasd","MONTHexasd"])
        zq=pd.merge(z,y,left_on=["YEAR BS"],right_on=["YEARexCY"])


        zqq=pd.merge(zq,yL,left_on=["LAST YEAR"],right_on=["YEARexLY"])
        zlist.append(zqq)

    erT=pd.concat(zlist)

    erT["YearFactor"] = erT["MONTH"]/12

    erT["ExRate_forperiod"]=(erT["YearFactor"]*erT["ExRate_currentYear"])+((1-erT["YearFactor"])*erT["ExRate_lastYear"])

    erT.drop(["CURRENCY SYMBOL","YEAR","YEAR BS","LAST YEAR","MONTH","YEARexasd","MONTHexasd","YEARexCY","YEARexLY"],axis=1,inplace=True)

    dFFex=pd.merge(dFF,erT,left_on=["TICKER","DATE"],right_on=["TICKER","DATE"])

    for met in dfM[dfM["Statement"]=="BS"]["title"]:
                dFFex[met]=dFFex[met]*dFFex["ExRate_asonDate"]

    for met in dfM[dfM["Statement"].isin(["CF","IS"])]["title"]:
                dFFex[met]=dFFex[met]*dFFex["ExRate_forperiod"]

    usdDF=dFF[~dFF["CURRENCY SYMBOL"].isin(currencies)]

    usdF=pd.concat([dFFex,usdDF])

    usdF.loc[usdF["CURRENCY SYMBOL"]=="USD","ExRate_asonDate"]=1
    usdF.loc[usdF["CURRENCY SYMBOL"]=="USD","ExRate_forperiod"]=1
    
    usdF.loc[usdF["CURRENCY SYMBOL"].isin([np.nan]),"ExRate_asonDate"]=1
    usdF.loc[usdF["CURRENCY SYMBOL"].isin([np.nan]),"ExRate_forperiod"]=1
    
    usdF.dropna(subset=["ExRate_forperiod"],inplace=True)
    return usdF



def Ratios(dfF=[]):
    #dfF = annual or quarterly financials 

    numerics = ['int', 'float']
    colnumeric = dfF.select_dtypes(include=numerics).columns
    dfF[colnumeric]=dfF[colnumeric].fillna(0)

    debt=dfF['LONG TERM DEBT'] + dfF['SHORT LONG TERM DEBT']+dfF['CAPITAL LEASE OBLIGATIONS']

    #PER SHARE RATIOS 
    dfF["EPS"] = dfF["NET INCOME"]/dfF["SHARES OUTSTANDING"]
    dfF["TOTAL REVENUE PER SHARE"] = dfF["TOTAL REVENUE"]/dfF["SHARES OUTSTANDING"]
    dfF["FREE CASH FLOW PER SHARE"] = dfF['FREE CASH FLOW']/dfF["SHARES OUTSTANDING"]
    dfF["EBITDA PER SHARE"] = dfF['EBITDA']/dfF["SHARES OUTSTANDING"]

    #VALUATION RELATED 
    dfF['NON-OPERATIONS VALUE'] = dfF['CASH'] + dfF['SHORT TERM INVESTMENTS'] + dfF['LONG TERM INVESTMENTS'] - (dfF['MINORITY INTEREST']*-1) - debt
    dfF['FAIR VALUE (30)'] = ((dfF['FREE CASH FLOW']*30)+(dfF['NON-OPERATIONS VALUE']))/dfF['SHARES OUTSTANDING']
    dfF['FAIR VALUE (15)'] =((dfF['FREE CASH FLOW']*15)+(dfF['NON-OPERATIONS VALUE']))/dfF['SHARES OUTSTANDING']
    dfF['FAIR VALUE (45)'] =((dfF['FREE CASH FLOW']*45)+(dfF['NON-OPERATIONS VALUE']))/dfF['SHARES OUTSTANDING']
    dfF["Effective Interest Rate"] = dfF["INTEREST EXPENSE"]/(debt)
    dfF["Effective Tax Rate"] =dfF["INCOME TAX EXPENSE"]/dfF["INCOME BEFORE TAX"] 
    dfF["DEBT %"] = debt/(debt+dfF["TOTAL STOCKHOLDER EQUITY"])
    dfF["Equity %"] = 1 - dfF["DEBT %"]


    #PROFIT MARGINS 
    dfF['Net Profit Margin'] = dfF['NET INCOME']/dfF['TOTAL REVENUE']                     
    dfF['Operating Profit Margin'] = dfF['OPERATING INCOME']/dfF['TOTAL REVENUE']
    dfF['EBITDA Margin'] = dfF['EBITDA']/dfF['TOTAL REVENUE']
    dfF['Gross Profit Margin'] = dfF['GROSS PROFIT']/dfF['TOTAL REVENUE']
    dfF['DATE']=pd.to_datetime(dfF['DATE']).dt.date


    #ACTIVITY/TURNOVER RATIOS:
    dfF["INVENTORY TURNOVER"]=dfF["COST OF REVENUE"]/dfF["INVENTORY"]
    dfF["Days of inventory on hand (DOH)"]=365/dfF["INVENTORY TURNOVER"]
    dfF["RECEIVABLES TURNOVER"] = dfF["TOTAL REVENUE"]/dfF["NET RECEIVABLES"]
    dfF["Days of sales outstanding (DSO)"]=365/dfF["RECEIVABLES TURNOVER"]
    dfF["PAYABLES TURNOVER"] = dfF["COST OF REVENUE"]/dfF["ACCOUNTS PAYABLE"]
    dfF["Number of days of payables"] = 365/dfF["PAYABLES TURNOVER"]
    dfF["WORKING CAPITAL TURNOVER"] = dfF["TOTAL REVENUE"]/dfF["NET WORKING CAPITAL"]
    dfF["FIXED ASSET TURNOVER"] = dfF["TOTAL REVENUE"]/dfF["NET TANGIBLE ASSETS"]
    dfF["TOTAL ASSET TURNOVER"] = dfF["TOTAL REVENUE"]/dfF["TOTAL ASSETS"]


    #LIQUIDITY RATIOS 
    dfF['CURRENT RATIO'] = dfF['TOTAL CURRENT ASSETS']/dfF['TOTAL CURRENT LIABILITIES']
    dfF['QUICK RATIO'] = (dfF['CASH'] + dfF['SHORT TERM INVESTMENTS'] + dfF["NET RECEIVABLES"])/dfF['TOTAL CURRENT LIABILITIES']
    dfF["CASH RATIO"]=  (dfF['CASH'] + dfF['SHORT TERM INVESTMENTS'])/dfF['TOTAL CURRENT LIABILITIES']                                                                                              
    dfF["Cash conversion cycle"] = dfF["Days of inventory on hand (DOH)"]+dfF["Days of sales outstanding (DSO)"]-dfF["Number of days of payables"]

    #SOLVENCY & COVERAGE RATIOS
    dfF['Debt to Equity'] = (debt)/dfF['TOTAL STOCKHOLDER EQUITY']
    dfF["DEBT TO ASSETS"] = dfF["TOTAL ASSETS"]/debt
    dfF["FINANCIAL LEVERAGE"]=dfF["TOTAL ASSETS"]/dfF['TOTAL STOCKHOLDER EQUITY']
    
    dfF["INTEREST COVERAGE"] = dfF["EBIT"]/dfF["INTEREST EXPENSE"]


    #RETURN ON CAPITAL RATIOS 
    dfF['ROIC'] = dfF['EBIT']/(debt + dfF['TOTAL STOCKHOLDER EQUITY'])
    dfF["ROA"] = dfF["NET INCOME"]/dfF["TOTAL ASSETS"]
    dfF["Operating ROA"] = dfF["EBIT"]/dfF["TOTAL ASSETS"]
    dfF["ROE"] = dfF["NET INCOME"]/dfF['TOTAL STOCKHOLDER EQUITY']


    numerics = ['int', 'float']
    colnumeric = dfF.select_dtypes(include=numerics).columns
    dfF[colnumeric]=dfF[colnumeric].fillna(0)
    dfF.replace([np.inf,-np.inf],0,inplace=True)
    dfF[colnumeric] = round(dfF[colnumeric],4)
    dfF.columns = dfF.columns.str.upper()
    dfF.columns = dfF.columns.str.lstrip()
    
    return dfF




#SCREENER DATAFRAME - GROWTH AND RATINGS 
#dfF = "Annual Financials"
def multidfC(dfF=[],dfC=[],dfM=[]):
    
    #GROWTH AND AVERAGE 
    metdf1=dfF[dfF[year]==dfF[year].max()]
    metdf2=dfF[dfF[year]==(dfF[year].max()-1)]

    tickcy=metdf1["TICKER"].unique().tolist()
    tickly=metdf2["TICKER"].unique().tolist()

    ticknt = []
    for tick in tickly:
        if tick not in tickcy:
            ticknt.append(tick)
    metdf2=metdf2[metdf2["TICKER"].isin(ticknt)]
    metdf = pd.concat([metdf1,metdf2],axis=0)
    diff_cols = metdf.columns.difference(dfC.columns)

    #Filter out the columns that are different. You could pass in the df2[diff_cols] directly into the merge as well.
    selcols = diff_cols.tolist()+ ["TICKER"]
    selcolmetdf = metdf[selcols]
    metdfC = pd.merge(dfC,selcolmetdf,left_on="TICKER",right_on="TICKER",how="left")   

    growth_cols = dfM[dfM['MultidfC']=="growth"]["title"].unique().tolist() 

    avg_cols = dfM[dfM['MultidfC']=="average"]["title"].unique().tolist()  
    colListg = growth_cols+[coName,year]
    colLista = avg_cols+[coName,year]

    year_list=dfF[year].unique().tolist()
    year_list.sort(reverse=True)

    dfFg = dfF[colListg]
    dfF10g=dfFg[dfFg[year].isin(year_list[:11])]
    dfF5g=dfFg[dfFg[year].isin(year_list[:6])]
    dfF3g=dfFg[dfFg[year].isin(year_list[:4])]
    dfF1g=dfFg[dfFg[year].isin(year_list[:2])]
    dfF1ge=dfFg[dfFg[year].isin(year_list[1:3])]
    grL = [dfF10g,dfF5g,dfF3g,dfF1g,dfF1ge]
    dfFa = dfF[colLista]
    dfF10a=dfFa[dfFa[year].isin(year_list[:10])]
    dfF5a=dfFa[dfFa[year].isin(year_list[:5])]
    dfF3a=dfFa[dfFa[year].isin(year_list[:4])]
    dfF1a=dfFa[dfFa[year].isin(year_list[:2])]
    dfF1ae=dfFa[dfFa[year].isin(year_list[1:3])]
    avL = [dfF10a,dfF5a,dfF3a,dfF1a,dfF1ae]


    colnameg = [" 10y-growth"," 5y-growth"," 3y-growth"," 1cy-growth"," 1ly-growth"]
    colnameav = [" 10y-average"," 5y-average"," 3y-average"," 1cy-average"," 1ly-average"]
    growthlist = []
    count = 0
    for yg in grL:
        yg=yg.pivot_table(index=coName,columns=year,values=growth_cols).groupby(level=0,axis=1).pct_change(axis=1)
        ayg=yg.groupby(level=0,axis=1).mean()
        col_list = ayg.columns.tolist()
        col_list =  [x + colnameg[count] for x in col_list]
        ayg.columns = col_list 
        growthlist.append(ayg)
        count += 1

    averagelist = []
    countav=0
    for ya in avL:
        ya=ya.pivot_table(index=coName,columns=year,values=avg_cols)
        ayg=ya.groupby(level=0,axis=1).mean()
        col_list = ayg.columns.tolist()
        col_list =  [x + colnameav[countav] for x in col_list]
        ayg.columns = col_list 
        averagelist.append(ayg)
        countav += 1

    multilist = growthlist + averagelist
    multiyeardfC = pd.concat(multilist,axis=1,join="inner").reset_index()
    multidfC = metdfC.merge(multiyeardfC,left_on=coName,right_on=coName,how="left")

    colcg=[col for col in multidfC.columns if '1cy-growth' in col]
    colclg=[col for col in multidfC.columns if '1ly-growth' in col]
    for acol in growth_cols:
        try:
            multidfC.loc[~multidfC[f'{acol} 1cy-growth'].isin([np.nan,0]),f'{acol} 1y-growth'] = multidfC.loc[~multidfC[f'{acol} 1cy-growth'].isin([np.nan,0]),f'{acol} 1cy-growth']
            multidfC.loc[multidfC[f'{acol} 1cy-growth'].isin([np.nan,0]),f'{acol} 1y-growth'] = multidfC.loc[multidfC[f'{acol} 1cy-growth'].isin([np.nan,0]),f'{acol} 1ly-growth']
            multidfC.drop([f'{acol} 1cy-growth',f'{acol} 1ly-growth'],axis=1,inplace=True)
        except:
            pass

    colca=[col for col in multidfC.columns if '1cy-average' in col]
    colcla=[col for col in multidfC.columns if '1ly-average' in col]
    for acol in avg_cols:
        multidfC.loc[~multidfC[f'{acol} 1cy-average'].isin([np.nan]),f'{acol} 1y-average']=multidfC.loc[~multidfC[f'{acol} 1cy-average'].isin([np.nan]),f'{acol} 1cy-average']
        multidfC.loc[multidfC[f'{acol} 1cy-average'].isin([np.nan]),f'{acol} 1y-average']=multidfC.loc[multidfC[f'{acol} 1cy-average'].isin([np.nan]),f'{acol} 1ly-average']
        multidfC.drop([f'{acol} 1cy-average',f'{acol} 1ly-average'],axis=1,inplace=True)




    #RATING 
    met_list = [rev_type,fcf,roic,nprofit,gm,ebitda_m,npm,d_e,c_r]

    colnameg = [" 10y-growth"," 5y-growth"," 3y-growth"," 1y-growth"]
    colnameav = [" 10y-average"," 5y-average"," 3y-average"," 1y-average"]
    ratingdF = multidfC.copy()

    for metrics in met_list:
        for co in colnameg+colnameav:
            try:
                if metrics in [rev_type,fcf,roic,npm,nprofit]:
                        bins = [-100000,-0.1,0,0.07,0.15,0.3,100000]
                        label = [-2,-1,1,3,6,9]


                elif metrics == c_r:
                        bins = [0,0.05,0.2,0.75,1.5,2.5,100000]
                        label = [-2,-1,0,1,2,3]


                elif metrics ==d_e:
                        bins = [0,0.05,1,1.5,3,5,100000]
                        label = [-2,-1,0,1,2,3]

                else:
                    bins = [-100000,-0.1,0,0.1,0.25,0.5,100000]
                    label = [-2,-1,0,1,2,3]

                ratingdF[f'{metrics}{co}-scale'] = pd.cut(ratingdF[f'{metrics}{co}'],bins=bins,labels=label).astype("float")

            except:
                pass
    yL = ["10y","5y","3y","1y"]

    for y in yL :
        colsa=[col for col in ratingdF.columns if f'{y}-average-scale' in col]
        colsg = [col for col in ratingdF.columns if f'{y}-growth-scale' in col]
        cols = colsa + colsg
        ratingdF[cols]=ratingdF[cols].fillna(0)
        ratingdF[f'{y}-Overall Rating']=(ratingdF[cols].sum(axis=1)/57)*10
        ratingdF[f'{y}-Avg Rating']=(ratingdF[colsa].sum(axis=1)/30)*10
        ratingdF[f'{y}-Growth Rating']=(ratingdF[colsg].sum(axis=1)/27)*10
    ratingdF['Fundamental Growth Rating']=round((ratingdF['10y-Growth Rating'] + ratingdF['5y-Growth Rating']*2 + ratingdF['3y-Growth Rating']*3 + ratingdF['1y-Growth Rating']*4)/10,2)
    ratingdF['Fundamental Avg Rating']=round((ratingdF['10y-Avg Rating'] + ratingdF['5y-Avg Rating']*2 + ratingdF['3y-Avg Rating']*3 + ratingdF['1y-Avg Rating']*4)/10,2)

    ratingdF["Revenue Size"] = pd.cut(ratingdF[rev_type],bins=[-100000000000000,500000000,1000000000,20000000000,100000000000,100000000000000],labels=[0,0.25,0.5,0.75,1]).astype("float")
    ratingdF["Net Profit Size"] = pd.cut(ratingdF[rev_type],bins=[-100000000000000,50000000,100000000,2000000000,10000000000,100000000000000],labels=[0,0.25,0.5,0.75,1]).astype("float")
    ratingdF["EBITDA Size"] = pd.cut(ratingdF[rev_type],bins=[-100000000000000,200000000,400000000,4000000000,20000000000,100000000000000],labels=[0,0.25,0.5,0.75,1]).astype("float")
    ratingdF["ASSET Size"] =  pd.cut(ratingdF[rev_type],bins=[-100000000000000,1500000000,3000000000,60000000000,300000000000,100000000000000],labels=[0,0.25,0.5,0.75,1]).astype("float")
    ratingdF["Fundamental Size Rating"] = round(((ratingdF["Revenue Size"]+ratingdF["Net Profit Size"]+ratingdF["EBITDA Size"]+ratingdF["ASSET Size"])/4)*10,2)
    ratingdF["Fundamental Size Rating"].fillna(0,inplace=True)
    ratingdF['Fundamental Overall Rating']=round((ratingdF['10y-Overall Rating'] + ratingdF['5y-Overall Rating']*2 + ratingdF['3y-Overall Rating']*3 + ratingdF['1y-Overall Rating']*4)/10,2)
    ratingdF['Fundamental Overall Rating']=round((9*ratingdF['Fundamental Overall Rating'] + ratingdF["Fundamental Size Rating"])/10,2)

    rdf=ratingdF[['TICKER','Fundamental Growth Rating','Fundamental Avg Rating',"Fundamental Size Rating",'Fundamental Overall Rating']]
    
    multidfC=pd.merge(multidfC,rdf,left_on="TICKER",right_on="TICKER",how="left")
    multidfC.columns = multidfC.columns.str.upper()
    multidfC.columns = multidfC.columns.str.lstrip()

    return multidfC 

