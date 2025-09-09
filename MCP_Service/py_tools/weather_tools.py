from typing import Callable, Dict, Any
from MCP_Service.others.config import WEATHER_API_KEY, WEATHER_API_URL, WEATHER_API_CITY_URL
import requests
from datetime import datetime
# ---------------- 工具实现函数 ----------------
def get_weather_handler(args: Dict[str, Any]):
    '''
    获取天气信息
    '''
    #检查必要参数
    location_name = args.get('location')
    if not location_name:
        return ValueError("Missing 'location' parameter")
    
    #获取环境变量中的APIKey
    api_key = WEATHER_API_KEY
    api_weather_url = WEATHER_API_URL
    api_city_url = WEATHER_API_CITY_URL

    if not api_key or not api_weather_url or not api_city_url:
        raise ValueError("Missing API configuration")

    # 调用城市搜索和天气API
    try:
        #调用城市搜索API
        city_resp=requests.get(api_city_url, params={"location": location_name, "key": api_key})
        city_resp.raise_for_status()
        city_data=city_resp.json()
        if city_data['code'] != '200' or not city_data.get('location'):
            raise Exception(f"City API error: {city_data['code']}-{city_data.get('message', 'Unknown error')}")
        location_id=city_data['location'][0]['id']
        location_name_std=city_data['location'][0]['name']

        #调用天气API
        response = requests.get(api_weather_url, params={"location": location_id, "key": api_key})
        response.raise_for_status()  # 检查请求是否成功
        weather_data = response.json()
        if weather_data['code'] != '200' or not weather_data.get('now'):
            raise Exception(f"API error: {weather_data['code']}-{weather_data.get('message', 'Unknown error')}")
        #解析API返回的天气数据
        now=weather_data['now']
        weather_condition={
            "temperature": f"{now['temp']}°C",
            "condition": now['text'],
            "humidity": f"{now['humidity']}%",
            "wind": f"{now['windScale']}级 {now['windDir']}",
            "location": location_name_std,
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        print(f"Weather data for {location_name_std}: {weather_condition}")
        return weather_condition
    except requests.exceptions.RequestException as e:
        raise Exception(f"Request error: {str(e)}")
    except (KeyError, ValueError) as e:
        raise Exception(f"Data parsing error: {str(e)}")



