
def classFactory(iface):
    from .plugin import SmartLayoutPlugin
    return SmartLayoutPlugin(iface)
