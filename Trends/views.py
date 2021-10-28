import json
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
import numpy as np
from django.template.loader import render_to_string
from faker import Factory
import geopandas as gpd
import matplotlib.pyplot as plt
from pytrends.request import TrendReq
import io


# Create your views here.

colorPalette = ['#55efc4', '#81ecec', '#a29bfe', '#ffeaa7', '#fab1a0', '#ff7675', '#fd79a8']
colorPrimary, colorSuccess, colorDanger = '#79aec8', colorPalette[0], colorPalette[5]

#encoder
class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NpEncoder, self).default(obj)


#Hoem page
def index(request):
    return render(request,'index.html')


#main function
def interest_over_time(request):
    if request.is_ajax():
        data=json.loads(request.body.decode('UTF-8'))
        key = data['keyword']
        print(key)
        pytrends = TrendReq(hl='en-US', tz=360)
        pytrends.build_payload([key], cat=0, timeframe='today 3-m', geo='', gprop='')
        df = pytrends.interest_over_time()
        fake = Factory.create()
        bg_color = []
        for i in range(len(data)):
            bg_color.append(fake.hex_color())

        trend = get_heatmap(key)

        relateds = trend['related']
        queries = trend['query']
        trends = trend['trends']
        try:
            values = list(relateds['value'])
            title = list(relateds['topic_title'])
            t_type = list(relateds['topic_type'])
            name = list(queries['query'])
            query_value = list(queries['value'])

            final_data = []
            query_final_data = []
            for i in range(0, 5):
                new_data = {}
                query_new_data={}
                new_data['value'] = values[i]
                new_data['title'] = title[i]
                new_data['t_type'] = t_type[i]
                query_new_data['name']=name[i]
                query_new_data['values']=query_value[i]
                final_data.append(new_data)
                query_final_data.append(query_new_data)

            context = {
                'relateds': final_data
            }
            query_context = {
                'queries': query_final_data
            }
            query = {'queries_table': render_to_string('query.html', context=query_context)}
            related = {'rendered_table': render_to_string('related.html', context=context)}

        except:
            related =None
            query = None

        trends_context = {
            'trends': trends
        }
        trends_table = {'rendered_table': render_to_string('trends.html', context=trends_context)}

        graph = trend['graph']
        return JsonResponse({
            'title': f' {key}',
            'data': {
                'labels': list(df.index.astype(str)),
                'backgroundColor': bg_color,
                'borderColor': colorPrimary,
                'data': list(df[key]),
            },
            'graph':graph,
            'relateds':related,
            'queries':query,
            'trends':trends_table
        }, encoder=NpEncoder)
    return HttpResponse(json.dumps({'msg': 'Something went wrong!'}), content_type="application/json")


#Heatmap
def get_heatmap(key):
    pytrends = TrendReq(hl='en-US', tz=360)
    pytrends.build_payload([key,], cat=0, timeframe='today 5-y', geo='IN', gprop='')
    data = pytrends.interest_by_region(resolution='CITY', inc_low_vol=True, inc_geo_code=True)
    shp_gdf = gpd.read_file('./Indian_states/Indian_states.shp')
    value = ['Andaman and Nicobar Islands', 'Arunachal Pradesh', 'Dadra and Nagar Haveli', 'Daman and Diu',
             'Jammu and Kashmir', 'Delhi']
    replace = ['Andaman & Nicobar Island', 'Arunanchal Pradesh', 'Dadara & Nagar Havelli', 'Daman & Diu',
               'Jammu & Kashmir', 'NCT of Delhi']
    as_list = data.index.tolist()
    for i in range(len(value)):
        idx = as_list.index(value[i])
        as_list[idx] = replace[i]
    data.index = as_list
    merged = shp_gdf.set_index('st_nm').join(data)
    fig, ax = plt.subplots(1, figsize=(5, 5))
    ax.axis('off')
    ax.set_title('Heat map of '+key,
                 fontdict={'fontsize': '15', 'fontweight': '3'})
    fig = merged.plot(column=key, cmap='RdYlGn', linewidth=0.5, ax=ax, edgecolor='0.2', legend=True)
    imgdata = io.StringIO()
    fig.figure.savefig(imgdata, format='svg')
    imgdata.seek(0)
    data = {}
    data['graph'] = imgdata.getvalue()
    data['related'] = dict(pytrends.related_topics()[key]['rising'][0:5])
    data['query'] = dict(pytrends.related_queries()[key]['rising'][0:5])
    data['trends'] = list(pytrends.trending_searches(pn='india')[0])[0:5]

    return data





