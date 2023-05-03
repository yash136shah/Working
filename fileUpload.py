#file upload and calculations 
import streamlit as st 
import pandas as pd
import plotly.express as px
import plotly.graph_objects as pgo
import numpy as np 

file=st.file_uploader("Upload Csv file")#,accept_multiple_files=True)

df=pd.read_csv(file)

df.columns = df.columns.str.upper().str.strip()



#st.write(df.dtypes)
descriptionTypes=df.select_dtypes("object").columns.tolist()
numericTypes=df.select_dtypes(["float","int"]).columns.tolist()
df[numericTypes]=df[numericTypes].replace([" ",np.nan],0)
#ScatterPlot Creation 



#filterData 
with st.expander("Descriptive Data:"):
    descriptiveData=st.multiselect("Select the Descriptive Data:",descriptionTypes,default=descriptionTypes)

with st.expander("Numeric Data"):
    numericData = st.multiselect("Select Numeric Data:",numericTypes,default=numericTypes)


totalData = descriptiveData + numericData

df = df[totalData]

descriptionTypes=df.select_dtypes("object").columns.tolist()
numericTypes=df.select_dtypes(["float","int"]).columns.tolist()
dateType = df.select_dtypes(["datetime"]).columns.tolist()

df = df.replace([" ",np.nan],0)
positive_cols = [col for col in numericTypes if (df[col] >= 0).all()]



#FILTER 
if "DATE" not in df.columns:
    with st.expander("Filter Data:"):
        tabs=st.tabs(["Descriptive","Numeric"])

        with tabs[0]:
            descTypes=st.multiselect("Select Descriptive Filters:",descriptionTypes,descriptionTypes[:3])

            dFilter = {}
            for d in descTypes:
                listOptions=df[d].unique().tolist()+["All"]
                dSel=st.multiselect(f"Select {d}",listOptions,default="All",key=d)
                dFilter[d]=dSel
            
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
        with tabs[1]:
            descTypes=st.multiselect("Select Numeric Filters:",numericTypes,numericTypes[:3])

            dFilter = {}
            for d in descTypes:
                minValue=df[d].min()
                maxValue = df[d].max()
                

            
                st.markdown(f"**{d}**")
                cols = st.columns(2)
                with cols[0]:
                    dSelmin=st.number_input(f"Greater than for {d}",minValue,maxValue,minValue,key=f"{d}min")
                with cols[1]:
                    dSelmax=st.number_input(f"Lesser than for {d}",minValue,maxValue,maxValue,key=f"{d}max")
                
                st.markdown("***")
                dFilter[d]=[dSelmin,dSelmax]
            
            
            for k,v in dFilter.items():         
                dfSel=dfSel[(dfSel[k]>v[0])&(dfSel[k]<v[1])]
          
else:
    dfSel = df
    #st.write(dfSel)
#if "DATE" in df.columns:
#    df['DATE'] = pd.to_datetime(df["DATE"])
    #df["DATE"].astype("datetime64[as]")

#st.write(df)
df = dfSel

name_select=st.multiselect("Name Select:",df["TICKER"].unique().tolist())

chartType=st.radio("Select Chart Type:",("Line","Bar","Pie","Heatmap","Treemap","Scatter Plot"),horizontal=True)

if chartType == "Scatter Plot":
    #with st.form("Scatter Plot"):
        cols = st.columns(5)

        with cols[0]:
            labelName=st.selectbox("Select Scatter Labels:",descriptionTypes)
        with cols[1]:
            x_axis_met=st.selectbox("Select X-Axis:",numericTypes)

        with cols[2]:
            y_axis_met=st.selectbox("Select Y-Axis:",numericTypes,index=1)

        with cols[3]:
            marker_size=st.selectbox("Select Marker Size:",positive_cols,index=2)

        with cols[4]:
            marker_color=st.selectbox("Select Marker Color:",descriptionTypes,index=1)

        df = df.sort_values(by=marker_size,ascending=False).iloc[:100]
        #if st.form_submit_button("Apply"):
        fig = px.scatter(df,x=x_axis_met,y=y_axis_met,color=marker_color,size=marker_size,size_max=40,text=labelName,height=600)
        results = px.get_trendline_results(fig)
        
        st.plotly_chart(fig,use_container_width=True)
        


if chartType == "Bar":
    cols = st.columns(5)
    with cols[0]:
        x_axis_met=st.selectbox("Select X-Axis:",descriptionTypes)
    
    with cols[1]:
        y_axis_met=st.selectbox("Select Y-Axis:",numericTypes)
    
    df=df[[x_axis_met,y_axis_met]].set_index(x_axis_met)

    stabs=st.tabs(["Chart","Summary"])
    df = df.iloc[1000:]
    with stabs[0]:
        
        for c in range(0,len(df)//100):
            #if c <=5:
                
                dfx = df.iloc[c*100:(c+1)*100]
                minV=round(dfx[y_axis_met].min(),2)
                maxV=round(dfx[y_axis_met].max(),2)
                fig=px.bar(dfx,title=f"{y_axis_met}: {minV}-{maxV}")
                st.plotly_chart(fig,use_container_width=True)

                
    with stabs[1]:

        st.write(df.describe())


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


if chartType == "Line":
    with st.form("Line"):
        cols = st.columns(5)

        with cols[0]:
            x_axis_met=st.selectbox("Select X-Axis:",descriptionTypes)
        
        with cols[1]:
            y_axis_met=st.selectbox("Select Y-Axis:",numericTypes)
        
        df=df[[x_axis_met,y_axis_met]].set_index(x_axis_met)
        df = df.iloc[:20]

        if st.form_submit_button("Apply"):
            fig=px.line(df)
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

        chartName=st.text_input("Chart Name","Market")
       
        tmValue = st.selectbox("Select Box Size Metrics:",positive_cols)
        tmColor = st.selectbox("Select Box Color:",numericTypes,index=1)
        
        tmHir=st.multiselect("Select Tree Map Hirerarchy:",descriptionTypes,default=descriptionTypes[:3])
        cScale=st.radio("Color Scale:",("Discrete","Continuous"))
        
        tmHirearchy=[]
        tmHirearchy += tmHir
        tmHirearchy.append(tmValue)
        tmHirearchy.append(tmColor)
        
        df = df[tmHirearchy].replace(0,np.nan).dropna()

        tmHirearchy.insert(0,px.Constant(f"{chartName}"))
        df = df.sort_values(by=tmValue,ascending=False).iloc[:100]
        fig = px.treemap(df, path=tmHirearchy, values = tmValue,color=tmColor, color_continuous_scale=px.colors.sequential.Viridis,height=500,hover_data = { })

        st.plotly_chart(fig,use_container_width=True)

#FUNDAMENTAL DATA SUMMARY 

#METRIC TYPE 
#METRIC CLASSIFICATION
#GROWTH,AVERAGE,SUM 


#TECHNICAL 
#TREND,PERFORMANCE,VOLATILITY,VOLUME,BETA