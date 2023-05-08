#file upload and calculations 
import streamlit as st 
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np 
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
from streamlit_pandas_profiling import st_profile_report
from ydata_profiling import ProfileReport

if "next" not in st.session_state:
    st.session_state["next"]=0
if "files" not in st.session_state:
    st.session_state["files"] = " "

if "dateTypes" not in st.session_state:
    st.session_state["dateTypes"]=" "

if "descriptionTypes" not in st.session_state:
    st.session_state["descriptionTypes"]=" "
    st.session_state["numericTypes"]=" "

if "df" not in st.session_state:
     st.session_state["df"]=" "

with st.expander("File Upload:"):
    #@st.cache_resource
    def FilesUploadChange():
        st.session_state["next"]=0
    st.session_state["files"]=st.file_uploader("Upload CSV/Excel file",accept_multiple_files=True,on_change=FilesUploadChange)
        
#if st.session_state["next"]==0:
    
#if len(st.session_state["files"])!=0:




objective=st.radio("What would you like to do?:",("Merge Files","Contact Files","Individual File Analysis"),index=0,horizontal=True)

def NextButton():
    st.session_state["next"]=1

nexT= st.button("Next",on_click=NextButton)
        

#FILE NAME AND UPLOAD 
if objective == "Merge Files":
    
    dfList=[]
    for file in st.session_state["files"]:
        try:
            dfX=pd.read_csv(file)   
        except:
            dfX= pd.read_excel(file)
        dfList.append(dfX)
    
   

    
    files=[]
    for c,i in enumerate(st.session_state["files"],start=1):
        files.append(i.name)
    
    cols = st.columns(2)

    with cols[0]:
        fileLeft=st.selectbox("Select Main File:",files,index=0)
        ldf=dfList[files.index(fileLeft)]

        colsLeft=ldf.columns
        left_on=st.selectbox("Select Main Column to merge on:",colsLeft)
        with st.expander("File1"):
            st.write(ldf)
        

    with cols[1]:
        fileRight = st.selectbox("Select Merge File:",files,index=1)
        rdf=dfList[files.index(fileRight)]
        colsRight=rdf.columns
        right_on = st.selectbox("Select Column to merge on:",colsRight)
        rdf.rename(columns={right_on:left_on},inplace=True)
        with st.expander("File2"):
            st.write(rdf)

    cols = st.columns(8)

    with cols[0]:
        mergeType=st.radio("Merge Type:",("inner","outer"),horizontal=True)
    
    with cols[1]:
        removeDuplicateColumns=st.radio("Remove Duplicate Columns",("Yes","No"),horizontal=True)

    with cols[2]:
        mergeDetails = st.radio("Merge Row Details:",(True,False),horizontal=True)

    #with cols[3]:
    #    mergeValidate = st.selectbox("Merge Validate:",[" ",'one_to_one','one_to_many','many_to_one','many_to_many'])

    mergeData= st.radio("Merge",("Yes","No"),horizontal=True,index=1)
    if mergeData == "Yes":
        
        
        try:
            df_merged= pd.merge(ldf,rdf,left_on=left_on,right_on=left_on,how=mergeType,suffixes=('', '_duplicate'),indicator=mergeDetails)#,validate=mergeValidate)

            
            if removeDuplicateColumns=="Yes":
                df_merged.drop([i for i in df_merged.columns if 'duplicate' in i],
                axis=1, inplace=True)
    

            st.write(df_merged.head(50))
            
            mergeFileName=st.text_input("Enter Merged File Name:","Merged_File")

            @st.cache_data
            def convert_df(df):
                # IMPORTANT: Cache the conversion to prevent computation on every rerun
                return df.to_csv().encode('utf-8')

            csv = convert_df(df_merged)

            st.download_button(
                label="Download data as CSV",
                data=csv,
                file_name=f'{mergeFileName}.csv',
                mime='text/csv',
            )

           
        except:
            
            st.error("Issues in Merging!")



                
    

if objective=="Individual File Analysis":
    if len(st.session_state["files"])>1:
            files=[]
            for c,i in enumerate(st.session_state["files"],start=1):
                files.append(i.name)
            fileName=st.selectbox("Select File:",files)
            fileIndex = files.index(fileName)
            file=st.session_state["files"][fileIndex]
            
    else: 
        file = st.session_state["files"][0]
    #@st.cache_data
    def fileLoad():
        
        try:
            df=pd.read_csv(file)   

        except:
            df = pd.read_excel(file)

        return df 
    
    df = fileLoad()



    
    if st.session_state["next"]==1:
                cols = st.columns(15)

                with cols[0]:
                    def BackButton():
                            st.session_state["next"]=0
                    backT=st.button("Back",on_click=BackButton)
                
                with cols[1]:
                    def NextButton():
                        st.session_state["next"]=2

                    nexT= st.button("Next",on_click=NextButton,help="Data Analysis")
                
                st.subheader("Data Cleaning")

                Dtabs=st.tabs(["Data Types","Duplicates","Blank/Error"])

                with Dtabs[0]:
                    
                        #MIXED DATA TYPE 

                    st.session_state["descriptionTypes"]=df.select_dtypes("object").columns.tolist()
                    st.session_state["numericTypes"]=df.select_dtypes(["float","int"]).columns.tolist()

                    for dateCols in st.session_state["descriptionTypes"]:
                            try:
                                df[dateCols]=pd.to_datetime(df[dateCols])
                                
                            except:
                                pass

                        
                    st.session_state["dateTypes"] = df.select_dtypes("datetime64[ns]").columns.tolist()

                
                    
                    if len(st.session_state["descriptionTypes"])==0:
                        st.warning("Atleast one column has to be descriptive!")
                            
                    dfDtypes=pd.DataFrame()
                    for column in df.columns:
                        if pd.api.types.infer_dtype(df[column]) in ["mixed"]:
                                dfDtypes[column]=[pd.api.types.infer_dtype(df[column])]
                    if len(dfDtypes)==0:
                        st.success("It looks like you have no Data Type Issues!")

                    elif len(st.session_state["descriptionTypes"])==0:
                        descriptive=st.selectbox("Atleast one column has to be descriptive! This column will be the KEY of the data!",st.session_state["numericTypes"])
                        df[descriptive] = df[descriptive].astype("str")
                        
                    else:
                        st.warning("You have Mixed Data Types!")
                        st.dataframe(dfDtypes)

                    cols = st.columns(2)
                    with cols[0]:
                        with st.form("ColumnChangedf"):
                            df.columns = df.columns.str.upper().str.strip()
                            
                            st.markdown("**Change Column Names**")
                            dfDtype=df.select_dtypes(["datetime64[ns]","int","float"]).dtypes.to_frame()
                            dfDtype.columns = ["Data Types"]
                            dfDtype.index.name = "Column Names"
                            dfCol=df.columns.to_frame().reset_index(drop=True)
                            dfCol = st.experimental_data_editor(dfCol)
                        #st.dataframe(dfDtype)
                            if st.form_submit_button("Update Column Names"):
                                st.success("Column Names Updated")

                    with cols[1]:
                        with st.form("Data Type df"):
                            st.markdown("**Change Data Types**")
                            dfDtype["Update Data Types"]=dfDtype["Data Types"]

                            dfDtype["Update Data Types"]=dfDtype["Update Data Types"].astype("string").astype("category").cat.add_categories(["object"])
                            edited_df = st.experimental_data_editor(dfDtype)
                            
                        

                            if st.form_submit_button("Update Data Types"):
                                convert_dict =  edited_df["Update Data Types"].to_dict()
                            
                                #df = df.astype(convert_dict)
                                st.write(convert_dict)
                                #st.write(df.dtypes.to_frame())
                    
                
                    #DATA PROCESSING
                    
                    #df=df.T.drop_duplicates().T
                    st.session_state["descriptionTypes"]=df.select_dtypes("object").columns.tolist()
                    st.session_state["numericTypes"]=df.select_dtypes(["float","int"]).columns.tolist()


                
                with Dtabs[1]:
                    D2tabs = st.tabs(["Duplicate Rows","Duplicate Columns","Duplicate Headers"])
                    #DUPLICATE ROWS    

                    with D2tabs[0]:
                       
                        
                            
                        if True in df.duplicated().tolist():
                            nRowsDuplicate=df.duplicated().sum()
                            st.write(f"Data has {nRowsDuplicate} duplicate Rows!")

                            st.write(df[df.duplicated(keep=False)].sort_values(by=df.columns[0]))
                            rDupl=st.radio("Remove Duplicated",("Yes","No"),horizontal=True,index=1)

                            if rDupl == "Yes":
                                df=df.drop_duplicates()

                        else:
                            st.success("No Duplicate Rows")

                        

                    #DUPLICATE COLUMNS 

                    with D2tabs[1]:
                        duplicatCol = []
                        for col in df.columns:
                            if True in df.duplicated(subset=col).tolist():
                                duplicatCol.append(col)
                    
                        cols = st.columns([2,10])
                        
                        with cols[0]:
                            dfDupCol=pd.DataFrame()
                            dfDupCol["Columns with Duplicate Data"]=duplicatCol
                            st.dataframe(dfDupCol)
                        with cols[1]:
                            dropDupli=st.multiselect("Select Columns to Drop Duplicate Data from",duplicatCol)
                            
                            dropD= st.radio("Drop Duplicates",("Yes","No"),index=1,horizontal=True)
                            
                            

                            if dropD == "Yes":
                                if len(dropDupli)>0:
                                    for c,k in enumerate(dropDupli):
                                        df.insert(c, dropDupli[c], df.pop(dropDupli[c]))       
                                        df=df.drop_duplicates(subset=k)
                                    st.success(f"Duplicates Dropped in {','.join(dropDupli)}")
                                    df

                            else:
                                if len(dropDupli)>0:
                                    #for col in dropD:
                                    for c,k in enumerate(dropDupli):
                                        df.insert(c, dropDupli[c], df.pop(dropDupli[c]))
                                
                                    st.write(df.loc[df.duplicated(dropDupli,keep=False)].sort_values(by=df.columns[0])) 

                



                with Dtabs[2]:

                    if len(dfDtypes)>0:
                        dfDtypes=dfDtypes.transpose()
                        dfDtypes.columns = ["Current Data Type"]
                        dfDtypes["Classify Data as:"]=[" "]*len(dfDtypes)
                        st.warning("Your Data has a mixed data type, determine if it is a word, number, date or boolean!")
                        st.experimental_data_editor(dfDtypes)
                        

                    emptyNData=st.selectbox("What to do with empty or error in Numerica Data?:",("Drop Errors","Keep them Blank","Replace Numeric Columns with 0 and keep Descriptive Columns Blank"))
                    df[st.session_state["numericTypes"]]=df[st.session_state["numericTypes"]].replace([" ",np.nan],0)
                    
                    df[st.session_state["descriptionTypes"]]=df[st.session_state["descriptionTypes"]].astype("str")

                    st.session_state["df"] = df
                    
                    
                    #st.write(df)


    if st.session_state["next"]==2:
                df = st.session_state["df"] 

                def BackButton():
                        st.session_state["next"]=1
                backT=st.button("Back",on_click=BackButton)
                
                dateTypes = df.select_dtypes(["datetime"]).columns.tolist()
                            
                #DATE TYPE - DATA BIFFURCATION
                if len(st.session_state["dateTypes"])>0:
                    dataPeriod=st.radio("Is this Data:",("Multi-Period","Single Period"),horizontal=True)
                
                else:
                    dataPeriod = "Single Period"

                
                if dataPeriod == "Multi-Period":
                    
                        cols = st.columns(3)
                        with cols[0]:
                            with st.expander("Multi-Period Setting:"):
                                if len(dateTypes)>0:
                                        
                                        dateType=st.selectbox("Select Date Category:",dateTypes)
                                else:
                                    dateType = dateTypes[0]
                                
                            
                                dateFreq=st.radio("Date Frequency:",("Continuous","Discrete"),index=1,horizontal=True)
                                if dateFreq == "Discrete":
                                
                                    discDate=st.selectbox("Period:",("Yearly","Quarterly","Monthly","Weekly"))

                                
                                    if discDate =="Yearly":
                                        
                                        df["Period"] = df[dateType].dt.year.astype("object",errors='ignore')

                                else:
                                    df["Period"] = df[dateType]



                descriptionTypes =df.select_dtypes("object").columns.tolist()
                numericTypes =df.select_dtypes(["float","int"]).columns.tolist()
                dateTypes = df.select_dtypes(["datetime"]).columns.tolist()

    

                tabs = st.tabs(["Table","Pivot Table","Summary","Charts"])

                with tabs[0]:

                    
                    #cols = st.columns([4,8])

                
                
                    #FILTER 
                    def Filter(descType=" ",numericType=" "):

                            with st.expander("Filter Data:"):
                                with st.form("FilterData"):
                                
                                    ftabs=st.tabs(["Descriptive","Numeric"])

                                    with ftabs[0]:
                                    
                                        descTypes=st.multiselect("Select Descriptive Filters:",descType,descType[0])

                                        dFilter = {}
                                        counter=0
                                        cols = st.columns(3)
                                        for d in descTypes:
                                            with cols[counter]:
                                                listOptions=df[d].unique().tolist()+["All"]
                                                dSel=st.multiselect(f"Select {d}",listOptions,default="All",key=d)
                                                dFilter[d]=dSel
                                            if counter ==2:
                                                counter=0
                                            else:
                                                counter += 1
                            
                                    
                                        dfSel = pd.DataFrame()
                                        counter=0
                                        for k,v in dFilter.items():
                                            if "All" in v:
                                                v=df[k].unique().tolist()
                                            
                                            if counter==0:
                                                dfSel=df[df[k].isin(v)]
                                            else:
                                                dfSel=dfSel[dfSel[k].isin(v)]
                                            counter+=1

                                    with ftabs[1]:
                                        descTypes=st.multiselect("Select Numeric Filters:",numericType,numericType[0])

                                        dFilter = {}
                                        cols = st.columns(3)
                                        counter=0
                                        for d in descTypes:
                                            minValue=df[d].min()
                                            maxValue = df[d].max()
                                            

                                        
                                            
                                            
                                            
                                            with cols[counter]:
                                                st.markdown(f"**{d}**")
                                                dSelmin=st.number_input(f"Greater than for {d}",minValue,maxValue,minValue,key=f"{d}min")
                                                dSelmax=st.number_input(f"Lesser than for {d}",minValue,maxValue,maxValue,key=f"{d}max")
                                                st.markdown("***")
                                            if counter==2:
                                                counter=0
                                            else:
                                                counter +=1

                                            
                                            dFilter[d]=[dSelmin,dSelmax]
                                        
                                        for k,v in dFilter.items():         
                                                dfSel=dfSel[(dfSel[k]>=v[0])&(dfSel[k]<=v[1])]
                                    
                                    

                                    if st.form_submit_button("Apply"):
                                        st.write(" ")
                                
                        
                            return dfSel
                
                    
                    #with cols[0]:
                    sstabs = st.tabs(["Select Data","Filter Data"])

                        
                    with sstabs[0]: 
                            with st.expander("Select Data:"):
                                with st.form("SelectData"):
                                    s3tabs = st.tabs(["Descriptive Data","Numeric Data"])            
                                    with s3tabs[0]:
                                        descriptiveData=st.multiselect("Select the Descriptive Data:",descriptionTypes,default=descriptionTypes)

                                    with s3tabs[1]:
                                        
                                        numericData = st.multiselect("Select Numeric Data:",numericTypes,default=numericTypes)
                                    

                                    descriptionTypes =df.select_dtypes("object").columns.tolist()
                                    numericTypes =df.select_dtypes(["float","int"]).columns.tolist()
                                    dateTypes = df.select_dtypes(["datetime"]).columns.tolist()

                                    selectedData = descriptiveData + numericData + dateTypes

                                    
                                    df = df[selectedData]

                                    descriptionTypes =df.select_dtypes("object").columns.tolist()
                                    numericTypes =df.select_dtypes(["float","int"]).columns.tolist()
                                    dateTypes = df.select_dtypes(["datetime"]).columns.tolist()

                                    #st.write(selectedData)
                                    #df = df.replace([" ",np.nan],0)
                                    positive_cols = [col for col in numericTypes if (df[col] >= 0).all()]

                                    if st.form_submit_button("Apply"):
                                        st.success("Selection Applied")
                            
                    with sstabs[1]:
                            df = Filter(descType=descriptionTypes,numericType=numericTypes)


                    #with cols[1]:
                    if len(df)>0:
                        updateMode=GridUpdateMode.MANUAL
                        
                        st.dataframe(df.head(100),use_container_width=True)

                with tabs[1]:
                    ptableOperation=st.radio("Operations",("Pivot Table","Grouping"),horizontal=True)

                    with st.form("PivotOperations"):
                        if ptableOperation=="Pivot Table":
                            cols = st.columns(3)

                            with cols[0]:
                                columns=st.multiselect("Choose Columns",(descriptionTypes+dateTypes))
                            with cols[1]:
                                index=st.multiselect("Choose Index",descriptionTypes)
                            with cols[2]:
                                value=st.multiselect("Choose Values:",numericTypes)
                            
                            aggfunc=st.radio("Choose Aggregate Function:",("sum","mean","count"),horizontal=True)
                                            
                           
                            if st.form_submit_button("Apply"):
                                ptable=df.pivot_table(columns=columns,index=index,values=value,aggfunc=aggfunc)
                                st.dataframe(ptable)

                        else:

                            aggfunc=st.radio("Choose Aggregate Function:",("sum","mean","count"),horizontal=True)
                                
                            groupDataby=st.multiselect("Group Your Data",df.columns,df.columns[0])
                            gKey=st.multiselect("Filter:",df[groupDataby[0]].unique().tolist())
                            if len(gKey)>0:
                                df=df[df[groupDataby[0]].isin(gKey)]


                            
                            if st.form_submit_button("Apply"):
                                if aggfunc =="sum":
                                    dfG=df.groupby(by=groupDataby).sum()#.unstack(fill_value=0)
                                elif aggfunc =="mean":
                                    dfG=df.groupby(by=groupDataby).mean()
                                else:
                                    try:
                                        dfG=df.groupby(by=groupDataby).size().unstack(fill_value=0)
                                    except:
                                        dfG=df.groupby(by=groupDataby).size()
                            
                                st.write(dfG)

                                dfChange=st.radio("Use this Table for Analysis:",("Yes","No"),index=1)
                                if dfChange=="Yes":
                                    df = dfG
                                    df = df.reset_index()

                                    descriptionTypes =df.select_dtypes("object").columns.tolist()
                                    numericTypes =df.select_dtypes(["float","int"]).columns.tolist()
                                    dateTypes = df.select_dtypes(["datetime"]).columns.tolist()

                with tabs[2]:
                        #dfDesc = df.describe()
                        cols = st.columns(2)
                        with cols[0]:
                            fig = px.box(df,y=numericTypes[0],x="INDUSTRY",points="all")
                            st.plotly_chart(fig,use_container_width=True)

                        with cols[1]:
                            st.dataframe((df.describe()[numericTypes[0]]),use_container_width=True)
                        

                                                

                        def Summary():
                            if len(df)>0:
                                st.write(df.describe())

                            
                            cols = st.columns(8)

                            with cols[0]:
                                catSel=st.selectbox("Select Category:",descriptionTypes,key="SummaryHistCatSel")
                            
                            with cols[1]:
                                xMetric=st.selectbox("Select Metric:",df.columns,key="SummaryHistSelMet")

                            sstabs = st.tabs(["Overall","Each Category"])
                            with sstabs[0]:
                                fig = px.histogram(df, x=xMetric)
                                st.plotly_chart(fig)

                            with sstabs[1]:
                            
                                if len(df[catSel].unique()) < len(df):
                                    catSelList=st.multiselect("Select Category Type:",df[catSel].unique(),df[catSel].unique()[0],key="SelectCatSummary")
                                    cols = st.columns(2)
                                    count = 0
                                    for catSeluni in catSelList:
                                        with cols[count]:
                                            dfx = df[df[catSel].isin([catSeluni])]
                                            fig = px.histogram(dfx, x=xMetric)
                                            st.plotly_chart(fig)
                                            
                                            if count == 0:
                                                count += 1
                                            else:
                                                count = 0

                                            
                            def ValueCounts():
                                counts = df[descriptionTypes].apply(pd.Series.value_counts)
                                st.write(counts)
                                for d in df[descriptionTypes].columns:
                                    st.write(df[d].value_counts().head(5))
                    


                with tabs[3]:
                    #name_select=st.multiselect("Name Select:",df["TICKER"].unique().tolist())

                    chartType=st.radio("Select Chart Type:",("Line","Bar","Histogram","Pie","Radar","Heatmap","Treemap","Scatter Plot"),horizontal=True)
                    
                    if chartType not in ["Line","Bar"]:
                        if dataPeriod =="Multi-Period":
                                    try:
                                        
                                        ps=st.number_input("Period:",int(df["Period"].min()),int(df["Period"].max()),int(df["Period"].max()))
                                        df=df[df["Period"]==ps]
                                    except:
                                        pass

                    if chartType == "Bar":

                        with st.form("BarChart"):
                            cols = st.columns(5)
                            with cols[0]:
                                x_axis_met2=st.selectbox("Select X-Axis:",descriptionTypes)

                            with cols[1]:
                                y_axis_met=st.selectbox("Select Y-Axis:",numericTypes)

                            with cols[2]: 
                                sortVal = st.selectbox("Sort Values by:",df.columns.unique())
                            with cols[3]:
                                sValAsc = st.radio("Sort Direction - Ascending:",(True,False),horizontal=True)
                            
                            with cols[4]:
                                xMetLen=int(len(df[x_axis_met2].unique().tolist()))
                                
                                startNumber=st.number_input("Start Number of X-Axis Metric:",0,xMetLen,0)

                                if xMetLen>20:
                                    eMax=20
                                else:
                                    eMax = xMetLen
                                endNumber=st.number_input("End Number of X-Axis Metric:",0,xMetLen,eMax)

                            
                            if dataPeriod =="Multi-Period":

                                    maxPeriod=df["Period"].max()
                                    if len(df[df["Period"]==(df["Period"].max())]) != len(df):
                                        maxPeriod = df["Period"].max() - 1

                                    
                                    dfPS=df[df["Period"]==maxPeriod].sort_values(by=sortVal,ascending=sValAsc).iloc[startNumber:endNumber]
                                    #st.write(dfPS)
                                    xList=dfPS[x_axis_met2].tolist()
                                    
                                    df = df[df[x_axis_met2].isin(xList)].sort_values(by=["Period"])
                                    if sortVal == x_axis_met2:
                                        ispdf = df.pivot_table(columns="Period",index=[x_axis_met2],values=y_axis_met,sort=False,aggfunc='sum')#.sort_index()
                                    
                                    else:
                                        ispdf = df.pivot_table(columns="Period",index=[x_axis_met2,sortVal],values=y_axis_met,sort=False,aggfunc='sum')#.sort_index()
                                    
                                    
                                    period_range = st.slider("Number of Periods:",0,len(df["Period"].unique()),(0,5),key=f"periodSlide")
                                    ys = period_range[0]
                                    ye = period_range[1]      
                                    
                            
                            if st.form_submit_button("Apply"):
                                
                                if dataPeriod =="Multi-Period":

                                    if ys == 0:
                                        ispdfS = ispdf.iloc[:,-ye:]
                                        

                                    else:
                                        ispdfS = ispdf.iloc[:,-ye:-ys]
                                     
                                    if sortVal == x_axis_met2:
                                        ispdfS = ispdfS.reset_index().sort_values(by=x_axis_met2,ascending=sValAsc).set_index(x_axis_met2)
                                   
                                    else:
                                        ispdfS = ispdfS.reset_index().sort_values(by=sortVal,ascending=sValAsc).drop([sortVal],axis=1).set_index(x_axis_met2)
                                   
                                    gtf = ispdfS.pct_change(axis=1)

                                    fig1 = go.Figure()
                                    for col in ispdfS.columns.to_list():
                                        fig1.add_trace(go.Bar(x=ispdfS.index, y=ispdfS[col], name = str(col),text=ispdfS[col].values))
                            
                                    st.plotly_chart(fig1,use_container_width=True)

                                    st.write(ispdfS)
                                    

                                    def BarAnimation():
                                        dfAni=df.iloc[:2000]
                                        st.write(dfAni)
                                        fig = px.bar(dfAni,x=x_axis_met2,y=y_axis_met,animation_frame="Period")
                                        st.plotly_chart(fig,use_container_width=True)


                                    gtf.columns = gtf.columns.astype("str")
                                    fig2 = px.imshow(gtf.values, text_auto=".2%", x=gtf.columns,y=gtf.index,aspect="auto")#,title=f"{metrics}-Growth")                    
                                    fig2.update_coloraxes(colorbar_tickformat=".0%",cmin=0,cmax=1)#,colorscale=heatmap_colorscale_growth)
                                    fig2.update_layout(height=450)
                                    #fig2.update_xaxes(dtick=1)
                                    st.plotly_chart(fig2,use_container_width=True)



                                else:
                                    df=df[[x_axis_met2,y_axis_met]].set_index(x_axis_met2)

                                    
                                    df = df.sort_values(by=sortVal,ascending=sValAsc).iloc[:1000]
                                    
                                    
                                    for c in range(0,len(df)//100):
                                        #if c <=5:
                                            
                                            dfx = df.iloc[c*100:(c+1)*100]
                                            minV=round(dfx[y_axis_met].min(),2)
                                            maxV=round(dfx[y_axis_met].max(),2)
                                            fig=px.bar(dfx,title=f"{y_axis_met}: {minV}-{maxV}")
                                            st.plotly_chart(fig,use_container_width=True)


                    if chartType == "Line":
                        if dataPeriod == "Multi-Period":
                            if dateFreq == "Discrete":
                                with st.form("Line Multiperiod"):
                                    cols = st.columns(8)

                                    with cols[0]:
                                        column=st.selectbox("Select Category:",descriptionTypes)

                                    with cols[1]:
                                        values = st.selectbox("Select Values:",numericTypes)

                                    df=df.pivot_table(columns="Period",index=column,values=values,sort=True)#.sort_index()
                                    
                                    period_range = st.slider("Number of Periods:",0,len(df.columns),(0,5),key=f"periodSlide")
                                    ys = period_range[0]
                                    ye = period_range[1]      

                                    if ys == 0:
                                        df = df.iloc[:,-ye:]
                                    
                                    else:
                                        df = df.iloc[:,-ye:-ys]
                    
                                
                                    df = df.iloc[:20]
                                    if st.form_submit_button("Apply"):
                                        fig=px.line(df.transpose())
                                        st.plotly_chart(fig,use_container_width=True)
                            else:
                                with st.form("Line Continuous Multiperiod"):
                                    cols = st.columns(8)
                                    import datetime
                                    import yfinance as yf

                                    sd = datetime.date(2000, 1, 1)    
                                    ed = datetime.date.today()


                                    infoData = ["AAPL","TSLA","MSFT","META","GOOG"]
                                    ticker_data = yf.download(infoData,start=sd,end=ed)   


                                    close = ticker_data["Close"]
                                    close.index.name="Period"
                                    close = close.reset_index()
                                    close = close.set_index(["Period"])
                                    #with cols[0]:
                                        #column=st.selectbox("Select Category:",descriptionTypes)

                                    #with cols[1]:
                                    values = st.multiselect("Select Values:",numericTypes,numericTypes[0])
                                    cols = ["Period"]+values
                                    df=df[cols]

                                    
                                    df = close.iloc[:400]
                                    if st.form_submit_button("Apply"):
                                        fig=px.line(df)
                                        st.plotly_chart(fig,use_container_width=True)


                        else:
                            with st.form("Line"):
                                cols = st.columns(5)
                            
                                with cols[0]:
                                    lineCh=descriptionTypes+dateTypes
                                    x_axis_met=st.selectbox("Select X-Axis:",lineCh)
                                
                                    #df[x_axis_met]=df[x_axis_met].astype("datetime64[ns]")
                                    
                                
                                with cols[1]:
                                    y_axis_met=st.selectbox("Select Y-Axis:",numericTypes)
                                
                                df=df[[x_axis_met,y_axis_met]].set_index(x_axis_met)
                                df = df.iloc[:20]

                                if st.form_submit_button("Apply"):
                                    fig=px.line(df)
                                    st.plotly_chart(fig,use_container_width=True)




                    if chartType =="Histogram":
                        cols = st.columns(8)

                        with cols[0]:
                            catSel=st.selectbox("Select Category:",descriptionTypes)
                        
                        with cols[1]:
                            xMetric=st.selectbox("Select Metric:",df.columns)

                        sstabs = st.tabs(["Overall","Each Category"])
                        with sstabs[0]:
                            fig = px.histogram(df, x=xMetric)
                            st.plotly_chart(fig)

                        with sstabs[1]:
                        
                            if len(df[catSel].unique()) < len(df):
                                catSelList=st.multiselect("Select Category Type:",df[catSel].unique(),df[catSel].unique()[0])
                                cols = st.columns(2)
                                count = 0
                                for catSeluni in catSelList:
                                    with cols[count]:
                                        dfx = df[df[catSel].isin([catSeluni])]
                                        fig = px.histogram(dfx, x=xMetric)
                                        st.plotly_chart(fig)
                                        
                                        if count == 0:
                                            count += 1
                                        else:
                                            count = 0

                       
                                
                    if chartType == "Scatter Plot":
                        with st.form("Scatter Plot"):                                

                            cols = st.columns(5)

                            with cols[0]:
                                labelName=st.selectbox("Select Scatter Labels:",descriptionTypes)
                            with cols[1]:
                                x_axis_met=st.selectbox("Select X-Axis:",numericTypes)

                            with cols[2]:
                                y_axis_met=st.selectbox("Select Y-Axis:",numericTypes,index=1)

                            with cols[3]:
                                marker_size=st.selectbox("Select Marker Size:",positive_cols,index=0)

                            with cols[4]:
                                marker_color=st.selectbox("Select Marker Color:",descriptionTypes,index=1)


                            df = df.sort_values(by=marker_size,ascending=False)
                            if st.form_submit_button("Apply"):
                                #df = df.sort_values("Period",ascending=False)
                                fig = px.scatter(df,x=x_axis_met,y=y_axis_met,color=marker_color,size=marker_size,size_max=40,text=labelName,height=600)#,animation_frame="Period")
                                results = px.get_trendline_results(fig)
                                
                                st.plotly_chart(fig,use_container_width=True)
                                

                    if chartType=="Radar":
                        selMet=st.multiselect("Select Metrics:",numericTypes)
                        
                        fig = px.line_polar(df, r='r', theta=selMet, line_close=True)
                        st.plotly_chart(fig)


                    
                    

                    if chartType == "Pie":
                        cols = st.columns(5)
                        with cols[0]:
                            x_axis_met=st.selectbox("Select Names:",descriptionTypes)
                        
                        with cols[1]:
                            y_axis_met=st.selectbox("Select Values:",positive_cols)
                        
                        #df=df[[x_axis_met,y_axis_met]].set_index(x_axis_met)
                        df = df.iloc[:100]
                        fig=px.pie(df,values=y_axis_met, names=x_axis_met,labels=None,height=800)
                        fig.update_traces(textposition='inside')
                        st.plotly_chart(fig,use_container_width=True)


                    


                    if chartType == "Heatmap":
                        with st.form("Heatmap"):
                            cols = st.columns(5)

                            with cols[0]:
                                labelName=st.selectbox("Select Line Labels:",descriptionTypes)
                            with cols[1]:
                                x_axis_met=st.selectbox("Select X-Axis:",numericTypes)
                            
                            with cols[2]:
                                y_axis_met=st.selectbox("Select Y-Axis:",numericTypes)
                            
                            
                            if st.form_submit_button("Apply"):
                                fig=px.line(df,x=x_axis_met,y=y_axis_met,labels=labelName)
                                st.plotly_chart(fig,use_container_width=True)



                    if chartType == "Treemap":
                            with st.form("TreeMap"):
                                cols = st.columns([2,2,2,4])


                                with cols[0]:
                                    chartName=st.text_input("Chart Name","Market")

                                with cols[1]:
                                    tmValue = st.selectbox("Select Box Size Metrics:",positive_cols)
                                
                                with cols[2]:
                                    tmColor = st.selectbox("Select Box Color:",numericTypes,index=1)
                                
                                with cols[3]:
                                    tmHir=st.multiselect("Select Tree Map Hirerarchy:",descriptionTypes,default=descriptionTypes[:3])


                                cScale=st.radio("Color Scale:",("Discrete","Continuous"))

                                if st.form_submit_button("Apply"):
                            
                                    tmHirearchy=[]
                                    tmHirearchy += tmHir
                                    tmHirearchy.append(tmValue)
                                    tmHirearchy.append(tmColor)
                                    
                                    df = df[tmHirearchy].replace(0,np.nan).dropna()

                                    tmHirearchy.insert(0,px.Constant(f"{chartName}"))
                                    df = df.sort_values(by=tmValue,ascending=False).iloc[:100]
                                    fig = px.treemap(df, path=tmHirearchy, values = tmValue,color=tmColor, color_continuous_scale=px.colors.sequential.Viridis,height=500,hover_data = { })
                                    fig.update_traces(root_color="lightgrey")
                                    st.plotly_chart(fig,use_container_width=True)


                