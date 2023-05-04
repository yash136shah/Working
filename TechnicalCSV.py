import streamlit as st 
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests 
import json


def EOD(date):
    request = requests.get(f"https://api.polygon.io/v2/aggs/grouped/locale/us/market/stocks/{date}?adjusted=true&apiKey=WM0pxRvcI654ZqGYD3GF3LzGbp6CIsiu")
    all_fields = json.loads(request.content)
    results = all_fields["results"]
    df=pd.DataFrame(results)
    st.write(df)

date=st.date_input("Date")
EOD(date)

def NewsPoly():
    request = requests.get("https://api.polygon.io/v3/reference/tickers/AAPL?apiKey=WM0pxRvcI654ZqGYD3GF3LzGbp6CIsiu")
    all_fields = json.loads(request.content)
    results = all_fields["results"]
    st.write(results)
NewsPoly()

file=st.file_uploader("Upload CSV/Excel file")

df=pd.read_csv(file)
df.columns = df.columns.str.upper().str.strip()


df["DATE"] = df["DATE"].astype("datetime64[ns]")
df = df.set_index("DATE")

#Trend 
cols=st.multiselect("Select:",df.columns,default=df.columns.tolist())

df = df[cols]


tabs = st.tabs(["Trend","Performace","Volatility","Beta","Correlation","Volume","Indicators"])

with tabs[0]:
    fig=px.line(df)
    st.plotly_chart(fig,use_container_width=True)



def PeriodSetting(ticker_data,key=" "):
        import datetime
        with st.expander("Period Settings",expanded=True):
                containerR = st.container()
                containerV = st.container()
                scol1,scol2 = st.columns(2)
                with scol1:
                    containerDateS = st.container()
                with scol2:
                    containerDateE = st.container()
                

        dtFreq = containerR.selectbox("Date Frequency:",("Quarterly","Monthly","Weekly","Daily"),index=3,key=f"{key}DF")#,horizontal=True)

        date_list = ticker_data.index.date
        
        per_type = containerV.selectbox("Period:",("1d","1w","1m","3m","6m","12m","5y"),index=6,key=f"{key}indexPerType")
        
        if per_type == "Choose your own Period":
                    ds=containerDateS.date_input("Start Date",value=datetime.date(2015,1,1),min_value=datetime.date(1980,1,1),max_value=datetime.date.today(),key=f"{key}Ds")
                    de=containerDateE.date_input("End Date",value=datetime.date.today(),min_value=datetime.date(1980,1,1),max_value=datetime.date.today(),key=f"{key}De")

        else:
            try:
                de = date_list[-1]

                if per_type == "1d":
                    ds = date_list[-2]

                elif per_type == "1w":
                    ds = date_list[-5]

                elif per_type == "1m":
                    ds = date_list[-20]


                elif per_type == "3m":
                    ds = date_list[-60]

                elif per_type == "6m":
                    ds = date_list[-120]

                elif per_type == "12m":
                    ds = date_list[-240]
                
                elif per_type == "5y":
                    ds = date_list[-1200]

                elif per_type == "All":
                    ds = date_list[0]
            except:
                de = date_list[-1]
                ds = date_list[0]
            #containerDateS.warning(f"Data from:{ds}!")
        return ds,de,dtFreq,per_type



def Correlation(data,key=" "):
        cols = st.columns([2,10])
        with cols[0]:
            ds,de,dtFreq,per_type = PeriodSetting(data,key=f"correlation{key}")
            pfData = data.copy().loc[ds:de]  ##############TO HAVE A CONTINUOUS DATA PERIOD 
            if dtFreq == "Quarterly":
                pfData=pfData.resample("QS").mean()

            elif dtFreq == "Monthly":
                pfData=pfData.resample("MS").mean()
        
            elif dtFreq == "Weekly":
                pfData=pfData.resample("W").mean()
        
            else:
                pass

        with cols[1]:
                
                corrdf=pfData.corr()
                fig=px.imshow(corrdf,text_auto=".2f",aspect="auto",title=f"Correlation of {dtFreq} close prices - {per_type}")
                fig.update_layout(height=450)
                st.plotly_chart(fig,use_container_width=True)



def Volatility(data,key=" "):
        
        cols = st.columns([2,10])
        with cols[0]:
            ds,de,dtFreq,per_type = PeriodSetting(data,key=f"Volatility{key}")
            pfData = data.copy().loc[ds:de]  ##############TO HAVE A CONTINUOUS DATA PERIOD 
            if dtFreq == "Quarterly":
                pfData=pfData.resample("QS").mean()

            elif dtFreq == "Monthly":
                pfData=pfData.resample("MS").mean()
        
            elif dtFreq == "Weekly":
                pfData=pfData.resample("W").mean()
        
            else:
                pass

        with cols[1]:   
            stdDf=pfData.pct_change().std().to_frame()
            
            fig=px.bar(stdDf,x=stdDf.columns,y=stdDf.index,text_auto=".2%")
            fig.update_layout(
                title=f"Volatility - {dtFreq} return - {per_type}",
                xaxis_title="Volatility",
                yaxis_title="Company",
                showlegend=False)
            fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig,use_container_width=True)


def Beta(data,key=" "):
        cols = st.columns([2,10])
        with cols[0]:
            benchmark = st.selectbox("Select Benchamark:",df.columns)
            ds,de,dtFreq,per_type = PeriodSetting(data,key=f"beta{key}")

            pfData = data.copy().loc[ds:de]

            if dtFreq == "Quarterly":
                pfData=pfData.resample("QS").mean()
    
            elif dtFreq == "Monthly":
                pfData=pfData.resample("MS").mean()

            elif dtFreq == "Weekly":
                pfData=pfData.resample("W").mean()

            else:
                pass


       
        
        with cols[1]:
            covDf=data.pct_change().cov()
            varDf=data.pct_change().var()
            betadf=covDf.loc[benchmark]/varDf.loc[benchmark]

            betadf = betadf.transpose().to_frame()
            fig=px.bar(betadf,x=betadf.columns,y=betadf.index,text_auto=".2f")
            fig.update_layout(
                title=f"Beta with {benchmark} - {dtFreq} - {per_type}",
                xaxis_title="Beta",
                yaxis_title="Company",
                showlegend=False)
            fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig,use_container_width=True)


#Volatility 
with tabs[2]:
     Volatility(df)
     

with tabs[3]: 
     Beta(df)

with tabs[4]:
     Correlation(df)




#Correlation 

#Volume 

#Indicators 

