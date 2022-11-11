from IPython.display import HTML,display
import pandas as pd

def _namestr(obj, namespace):
    return [name for name in namespace if namespace[name] is obj]

def display_dataframes(*args,captions=[],margin="20px",):
    '''
    Displays 1 or more pd.DataFrames horizontally instead of vertically.
    Optionally allows for captioning the data frames for reference
    
    *args can be pd.DataFrame <or> 
        a dict with key "df" and value is pd.DataFrame
    
    captions is a list of str for to caption each dataframe.
        ignored unless number of dataframes and captions are the same
    
    margin is a str which sets the whitespace between the dataframes
        default is 20px
    
    Examples:
    
        # display d1, d2 and d3 in the same line 
        display_dataframes(d1,d2,d3)
        
        # display d1 and d2 in the same line 
        # d1 is captioned "customers" while d2 is captioned "orders"
        display_dataframes(d1,d2,captions=["customers","orders"])
        
        # same as the previous example, only using dict format
        display_dataframes({ "df" : d1, "caption" : "customers"}, { "df" : d2, "caption" : "orders"})
        
    '''
    
    html_str=''
    if len(args) == len(captions):
        i = 0
        for df in args:
            s = df.style.set_caption(captions[i])
            html_str+=s.to_html()
            i += 1
    else:
        for df in args:
            if type(df) is dict:
                d = df.get("df", pd.DataFrame())
                caption = df.get("caption","")
                s = d.style.set_caption(caption)
                html_str+=s.to_html()
            elif type(df) is pd.DataFrame:
                html_str+=df.to_html()
            else:
                Exception("Unable To Find Dataframes")
        
    return display(HTML(html_str.replace('table',f'table style="display:inline; margin-right: {margin}"')))