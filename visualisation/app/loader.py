import pandas as pd
import influxdb_client


class InfluxLoader:
    def __init__(self, influx_client: influxdb_client.InfluxDBClient):
        self.client: influxdb_client.InfluxDBClient = influx_client
        self.query_api = self.client.query_api()

    def get_history(self, ticker: str) -> pd.DataFrame:
        query = f'from(bucket: "tickers")\
        |> range(start: -10m)\
        |> filter(fn: (r) => r["_measurement"] == "{ticker}")\
        |> filter(fn: (r) => r["_field"] == "price")'
        measures_list = []
        time_list = []
        tables = self.query_api.query(query)
        for table in tables:
            for row in table.records:
                time_list.append(row.get_time())
                measures_list.append(row.get_value())
        return pd.DataFrame(measures_list, index=time_list, columns=['measurement'])

    def get_measure(self, ticker: str) -> dict:
        query = f'from(bucket: "tickers")\
        |> range(start: -10m)\
        |> filter(fn: (r) => r["_measurement"] == "{ticker}")\
        |> filter(fn: (r) => r["_field"] == "price")\
        |> last()'
        result = self.query_api.query(query)
        if not result:
            return {}
        return {result[0].records[0].get_time(): result[0].records[0].get_value()}


if __name__ == '__main__':
    client = influxdb_client.InfluxDBClient(url="http://localhost:8086", token='token-test', org='skanestas')
    df = InfluxLoader(client).get_measure("tickers_00")
    print(df)
