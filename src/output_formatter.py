from src.station_mapper import StationMapper


class OutputFormatter:
    # Mom: We have Dependency Injection at home...:
    def __init__(self, stationMapper, jvinsnesStationMapper):
        self.jvinsnes_station_mapper = jvinsnesStationMapper
        self.station_mapper = stationMapper

    def format(self, raw_input:dict, format:str = "default"):
        format = format.strip()

        match format:
            case "raw":
                return raw_input

            case "default":    
                return self.default(raw_input)
            
            case "jvinsnes":
                return self.jvinsnes(raw_input)

    def default(self, raw_input):
        station = raw_input.get('station')
        detections = raw_input.get('detection_results')

        fuel_prices = []
        for detection in detections:
            fuel_type = detection[1].name if detection[1] is not None else "Unknown"
            fuel_price = detection[0][2]
            fuel_prices.append({"type": fuel_type, "price": fuel_price})

        return {
            "station": station,
            "prices": fuel_prices
        }

    def jvinsnes(self, raw_input):
        pass