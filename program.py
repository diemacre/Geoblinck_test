'''
@author: diego martin crespo
@email: dmartinc2009@gmail.com
'''

#import libraries
from math import sin, asin, cos, sqrt, atan2, radians
import pandas as pd
import numpy as np
from time import time

#load the data from s3

clients_url = 'http://geoblink-data-test.s3.amazonaws.com/clients.csv'
stores_url = 'http://geoblink-data-test.s3.amazonaws.com/stores.csv'

#points of reference
p1 = [40.416935, -3.703772]  # Madrid
p2 = [48.859017, 2.342049]  # Paris
p3 = [43.298427, 5.369361]  # Marsella
p4 = [43.367798, -8.435075] # Vigo


def save_all_local(clients_url, stores_url):
    '''
    saves into .csv the data in .csv from the cloud
    Params:
        clients_url...... path to clients .csv file
        stores_url....... path to stores .csv file
    '''
    clients_db = pd.read_csv(clients_url)
    stores_db = pd.read_csv(stores_url)
    clients_db.to_csv('clients.csv', index=False)
    stores_db.to_csv('stores.csv', index=False)

def load_file(path):
    '''
    loads .csv file into pandas dataframe
    Params:
        path...... path to .csv file
    Return:
        .......... pandas dataframe 
    '''
    return(pd.read_csv(path))


def check_client_format(client):
    '''
    check for a sigle client if its parameters have the right format and within the limits defined in the problem statement. If is
    good it returns an 'OK' and if not it will return the reason such as : MISS_COORD, BAD_COORD...
    Params:
        client...... pandas row dataframe
    Return:
        check....... string
    '''
    check = ''
    if (client['home_latitude'] >= 51.1485061713) or (client['home_latitude'] <= 35.946850084) or (client['home_longitude'] >= 9.56001631027) or (client['home_longitude'] <= -9.39288367353):
        check += ' BAD_COORD'
    if pd.isna(client['home_longitude']) or pd.isna(client['home_latitude']):
        check += ' MISS_COORD'
    if (client['country'] != 'ES') and (client['country'] != 'FR'):
        check += ' BAD_COUNTRY'
    if check == '':
        check += 'OK'
    return check

def check_clients_format(clients):
    '''
    adds a new colum to the clients dataframe with the result of cheking each client format. it uses the function 
    check_client_format(store) to check each client.
    Params:
        stores...... pandas dataframe
    Return:
        stores_checked....... pandas dataframe
    '''
    clients_checked = clients.copy()
    check = []
    for i, row in clients_checked.iterrows():
        check.append(check_client_format(row))
    clients_checked['check_format'] = check
    return clients_checked


def check_store_format(store):
    '''
    check for a sigle store if its parameters have the right format and within the limits defined in the problem statement. If it is
    good it returns an 'OK' and if not it will return the reason such as : MISS_COORD, BAD_COORD...
    Params:
        store...... pandas row dataframe
    Return:
        check....... string
    '''
    check = ''
    if (store['latitude'] >= 51.1485061713) or (store['latitude'] <= 35.946850084) or (store['longitude'] >= 9.56001631027) or (store['longitude'] <= -9.39288367353):
        check += ' BAD_COORD'
    if pd.isna(store['longitude']) or pd.isna(store['latitude']):
        check += ' MISS_COORD'
    if store['country'] != 'ES' and store['country'] != 'FR':
        check += ' BAD_COUNTRY'
    if check == '':
        check += 'OK'
    return check


def check_stores_format(stores):
    '''
    adds a new colum to the stores dataframe with the result of cheking each store format. it uses the function 
    check_store_format(store) to check each store.
    Params:
        stores...... pandas dataframe
    Return:
        stores_checked....... pandas dataframe
    '''
    stores_checked = stores.copy()
    check = []
    for i, row in stores_checked.iterrows():
        check.append(check_store_format(row))
    stores_checked['check_format'] = check
    return stores_checked



def user_is_near_shop_in_dif_country(client, stores):
    '''
    returns 0 if the client near_shop corresponding to a store has the same country
    as the home country of the client, if not it returns 1
    Params:
        client...... pandas row dataframe
        stores....... pandas dataframe
    Return:
        0 or 1....... integer
    '''
    countryOfnear_shop = stores.loc[stores['id'] == client['near_shop']]['country']
    if countryOfnear_shop.values[0] == client['country']:
        return 0
    else:
        return 1
    

def n_users_is_near_shop_in_dif_country(clients, stores):
    '''
    returns the number of cliens/users that its near_shop is not located in the same
    country that the home country of the client/user. It uses the users_is_near_shop_in_dif_country(client, stores) function
    Params:
        clients...... pandas dataframe
        stores....... pandas dataframe
    Return:
        number....... integer 
    '''
    number = 0
    for i, row in clients.iterrows():
        is_in = user_is_near_shop_in_dif_country(row, stores)
        number+=is_in
    return number


def calculate_distance(lat1, lon1, lat2, lon2):
    '''
    calculates the distance between two coordinates in meters
    Params:
        lat1...... latitude of position 1 in degrees
        lon1...... longitude of position 1 in degrees
        lat2...... latitude of position 2 in degrees
        lon2...... longitude of position 2 in degrees
    Return:
        distance.... integer
    '''

    # convert decimal degrees to radians
    lon1r, lat1r, lon2r, lat2r = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2r - lon1r
    dlat = lat2r - lat1r
    a = sin(dlat/2)**2 + cos(lat1r) * cos(lat2r) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371000  # Radius of earth in kilometers
    distance = c * r
    return distance


def find_closest(data, position, n):
    '''
    find the closest value to 'n' in a dataframe column['position']
    Params:
        data..... dataframe pandas
        position...... string
        n..... integer
    Return:
        closest.... series dataframe pandas


    '''
    data = data.loc[data['check_format'] == 'OK']
    closest = data.loc[[abs(data[position] - n).idxmin()]]
    return closest


def add_column_dist_to_ref_point(data, point, p_string):
    '''
    adds a column to the dataframe pased as argument with the distance of each store to pased point.
    Params:
        data..... dataframe pandas
        point...... list of two integers
        p_string..... string
    Return:
        data1.... dataframe pandas


    '''
    distances_to_p = []
    data1 = data.copy()

    for i, row in data.iterrows():
        if row['check_format'] == 'OK':
            distances_to_p.append(calculate_distance(
                row['latitude'], row['longitude'], point[0], point[1]))
        else:
            distances_to_p.append(-1)
    data1[p_string] = distances_to_p
    return data1

#---------------------------METHOD 1---------------------------#
def nearest_shop_to_client(client, stores):
    '''
    Calculates the nearest shop to a client home. It uses the calculate_distance(lat1, lon1, lat2, lon2) to calculate the distance
    for the client to each store. It will check only those stores that have coodinates defined correctly 'check_format' equal to OK. if there is
    no store near it will return the nearest_shop as -1.

    -METHOD 1 or brute force: calculate distance for each pased client to all the stores and take the store id with least distance

    Params:
        clients...... pandas dataframe
        stores....... pandas dataframe
    Return:
        nearest_shop.....integer
    '''
    least_distance = 9999999999999999999
    nearest_shop = -1

    for i, row in stores.iterrows():
        if row['check_format'] == 'OK':
                dist1 = calculate_distance(client['home_latitude'], client['home_longitude'], row['latitude'], row['longitude'])
                if dist1 == 0:
                    least_distance=dist1
                    nearest_shop = row['id']
                    return nearest_shop

                if dist1 < least_distance:
                    least_distance = dist1
                    nearest_shop = row['id']
                
    return nearest_shop


def nearest_shop_to_all_clients(clients, stores):
    '''
    adds a new colum to the clients dataframe with the nearest shop to a clients home. it uses the function 
    nearest_shop_to_client(client, stores) to calculate the nearest shop for each client. Before calling it it checks if the
    check_format colum for each client is OK. And after calling it it also checks if there are any near_shops.
    Either if the check_format is not OK or there are no near shops the near_shop value is assigned as the nearest shop to the home.
    Params:
        clients...... pandas dataframe
        stores....... pandas dataframe
    Return:
        new_clients.....pandas dataframe
    '''
    new_clients = clients.copy()
    near_shops_home = []
    customers = {}
    for i, row in new_clients.iterrows():
        if row['check_format'] == 'OK':
            if (row['home_latitude'], row['home_longitude']) not in customers.keys():
                nearest_shop = nearest_shop_to_client(row, stores)
                customers[(row['home_latitude'],row['home_longitude'])] = nearest_shop
                if nearest_shop != -1:
                    near_shops_home.append(nearest_shop)
                else:
                    near_shops_home.append(row['near_shop'])
            else:
                if customers[(row['home_latitude'], row['home_longitude'])] != -1:
                    near_shops_home.append(customers[(row['home_latitude'], row['home_longitude'])])
                else:
                    near_shops_home.append(row['near_shop'])
        else:
            near_shops_home.append(row['near_shop'])
    new_clients['near_shop_home'] = near_shops_home
    return new_clients

#---------------------------METHOD 2---------------------------#
def nearest_shop_to_client2(client, stores_latitude, stores_longitude, max_stores):
    '''
    Calculates the nearest shop to a client home. It uses the calculate_distance(lat1, lon1, lat2, lon2) to calculate the distance
    for the client to each store. It will check only those stores that have coodinates defined correctly 'check_format' equal to OK. if there is
    no store near it will return the nearest_shop as -1.

    -METHOD 2 or rectangle method: we pased the two list of stores ordered by latitude and by longitude repectly. We find the closest client to a store in each list.
    As they are ordered we can create two limits upper and lower for each ordered list. Then we only need to check for those points that are inside the limits.

    Params:
        clients...... pandas dataframe
        stores_latitute....... pandas dataframe
        stores_longitude....... pandas dataframe
        max_scores....... integer
    Return:
        nearest_shop.....integer
    '''
    least_distance = 9999999999999999999
    nearest_shop = -1

    close_latitude1 = find_closest(stores_latitude, 'latitude', client['home_latitude'])
    close_longitude1 = find_closest(stores_longitude, 'longitude', client['home_longitude'])

    if close_latitude1.iloc[0]['check_format'] == 'OK':
        dist1 = calculate_distance(client['home_latitude'], client['home_longitude'],
                                   close_latitude1['latitude'], close_latitude1['longitude'])
        dist2 = calculate_distance(client['home_latitude'], client['home_longitude'],
                                   close_longitude1['latitude'], close_longitude1['longitude'])
        if dist1 == 0:
            return close_latitude1.iloc[0]['id']
        if dist2 == 0:
            return close_longitude1.iloc[0]['id']
        if dist1 <= dist2:
            nearest_shop = close_latitude1.iloc[0]['id']
            least_distance = dist1
        else:
            nearest_shop = close_longitude1.iloc[0]['id']
            least_distance = dist2

    limit_latitude1 = close_longitude1.iloc[0]['latitude']
    limit_latitude2 = 2*client['home_latitude'] - limit_latitude1
    latitude_limits = sorted([limit_latitude1, limit_latitude2])

    limit_longitude1 = close_latitude1.iloc[0]['longitude']
    limit_longitude2 = 2*client['home_longitude'] - limit_longitude1
    longitude_limits = sorted([limit_longitude1, limit_longitude2])

    check_db_lat = stores_latitude.loc[(stores_latitude['latitude']>= latitude_limits[0]) & (stores_latitude['latitude']<= latitude_limits[1])]
    check_db_lon = stores_latitude.loc[(stores_latitude['latitude'] >= longitude_limits[0]) & (stores_longitude['longitude'] <= longitude_limits[1])]

    if (check_db_lat.shape[0] + check_db_lon.shape[0]) > max_stores:
        for i, row in stores_latitude.iterrows():
            if row['check_format'] == 'OK':
                if (row['latitude'] <= latitude_limits[1] and row['latitude'] >= latitude_limits[0]) and (row['longitude'] <= longitude_limits[1] and row['longitude'] >= longitude_limits[0]):
                    dist = calculate_distance(client['home_latitude'], client['home_longitude'], row['latitude'], row['longitude'])
                    if dist == 0:
                        return row['id']
                    if dist < least_distance:
                        least_distance = dist
                        nearest_shop = row['id']
    else:
        for i, row in check_db_lat.iterrows():
            if row['check_format'] == 'OK':
                dist = calculate_distance(client['home_latitude'], client['home_longitude'], row['latitude'], row['longitude'])
                if dist == 0:
                    return row['id']
                if dist < least_distance:
                    least_distance = dist
                    nearest_shop = row['id']

        for i, row in check_db_lon.iterrows():
            if row['check_format'] == 'OK':
                dist = calculate_distance(client['home_latitude'], client['home_longitude'], row['latitude'], row['longitude'])
                if dist == 0:
                    return row['id']
                if dist < least_distance:
                    least_distance = dist
                    nearest_shop = row['id']
    return nearest_shop

def nearest_shop_to_all_clients2(clients, stores_latitude, stores_longitude, max_stores):
    '''
    adds a new colum to the clients dataframe with the nearest shop to a clients home. it uses the function 
    nearest_shop_to_client2(client, stores_latitude, stores_longitude, max_stores) to calculate the nearest shop for each client. Before calling it it checks if the
    check_format colum for each client is OK. And after calling it it also checks if there are any near_shops.
    Either if the check_format is not OK or there are no near shops the near_shop value is assigned as the nearest shop to the home.

    Params:
        clients...... pandas dataframe
        stores_latitude....... pandas dataframe
        stores_longitude....... pandas dataframe
        max_stores........integer
    Return:
        new_clients.....pandas dataframe
    '''
    new_clients = clients.copy()
    near_shops_home = []
    customers = {}
    for i, row in new_clients.iterrows():
        if row['check_format'] == 'OK':
            if (row['home_latitude'], row['home_longitude']) not in customers.keys():
                nearest_shop = nearest_shop_to_client2(row, stores_latitude, stores_longitude, max_stores)
                customers[(row['home_latitude'],row['home_longitude'])] = nearest_shop
                if nearest_shop != -1:
                    near_shops_home.append(nearest_shop)
                else:
                    near_shops_home.append(row['near_shop'])
            else:
                if customers[(row['home_latitude'], row['home_longitude'])] != -1:
                    near_shops_home.append(customers[(row['home_latitude'], row['home_longitude'])])
                else:
                    near_shops_home.append(row['near_shop'])
        else:
            near_shops_home.append(row['near_shop'])
    new_clients['near_shop_home'] = near_shops_home
    return new_clients

#---------------------------METHOD 3---------------------------#


def nearest_shop_to_client3(client, stores_checked_p1, stores_checked_p2, stores_checked_p3):
    '''
    Calculates the nearest shop to a client home. It uses the calculate_distance(lat1, lon1, lat2, lon2) to calculate the distance
    for the client to each store. It will check only those stores that have coodinates defined correctly 'check_format' equal to OK. if there is
    no store near it will return the nearest_shop as -1.

    -METHOD 2 or rectangle method: we pased 3 list as arguments each one is ordered by the colum that contains the distance for each store to a point of reference.
    It starts for the list ordered with distance to p1, we calculate the distance from the client to the p1 and we get the closest store of stores_checked_p1 that
    is nearer from the distance from the client to p1. We only take then those stores_checked_p1 within the limit [closest_store_p1 - distance_to_client, closest_store_p1 + distance_to_client]
    Then in this new limit we calculate the closest store but to a second point of reference. We do the same proces as with 1 to calculate another two limits. And then
    we do it a third time for a 3 point of reference. At the end we only need to calculate the distance for the last range of stores.

    Params:
        clients...... pandas dataframe
        stores_checked_p1....... pandas dataframe
        stores_checked_p2....... pandas dataframe
        stores_checked_p3....... pandas dataframe
    Return:
        nearest_shop.....integer
    '''
    nearest = -1
    least = 9999999999999999999

    client_d1 = calculate_distance(client['home_latitude'], client['home_longitude'], p1[0], p1[1])
    client_d2 = calculate_distance(client['home_latitude'], client['home_longitude'], p2[0], p2[1])
    client_d3 = calculate_distance(client['home_latitude'], client['home_longitude'], p3[0], p3[1])

    close_to_p1 = find_closest(stores_checked_p1, 'd_p1', client_d1)
    stores_near_p1 = stores_checked_p1.loc[(stores_checked_p1['d_p1'] >= (close_to_p1.iloc[0]['d_p1']-client_d1)) & (stores_checked_p1['d_p1'] <= (close_to_p1.iloc[0]['d_p1'] + client_d1))]
    if stores_near_p1.shape[0] == 1:
        nearest = stores_near_p1.iloc[0]['id']
        return nearest

    stores_checked_p2_red = stores_checked_p2.loc[(stores_checked_p2['id'].isin(stores_near_p1['id'].values))]
    close_to_p2 = find_closest(stores_checked_p2_red, 'd_p2', client_d2)
    stores_near_p2 = stores_checked_p2_red.loc[(stores_checked_p2_red['d_p2'] >= (close_to_p2.iloc[0]['d_p2']-client_d2)) & (stores_checked_p2_red['d_p2'] <= (close_to_p2.iloc[0]['d_p2'] + client_d2))]
    if stores_near_p2.shape[0] == 1:
        nearest = stores_near_p2.iloc[0]['id']
        return nearest
    
    stores_checked_p3_red = stores_checked_p3.loc[(stores_checked_p3['id'].isin(stores_near_p2['id'].values))]
    close_to_p3 = find_closest(stores_checked_p3_red, 'd_p3', client_d3)
    stores_near_p3 = stores_checked_p3_red.loc[(stores_checked_p3_red['d_p3'] >= (close_to_p3.iloc[0]['d_p3']-client_d3)) & (stores_checked_p3_red['d_p3'] <= (close_to_p3.iloc[0]['d_p3'] + client_d3))]
    if stores_near_p3.shape[0] == 1:
        nearest = stores_near_p3.iloc[0]['id']
        return nearest
    

    for i, row in stores_near_p3.iterrows():
        if row['check_format'] == 'OK':
            dist = calculate_distance(
                client['home_latitude'], client['home_longitude'], row['latitude'], row['longitude'])
            if dist == 0:
                return row['id']
            if dist < least:
                least = dist
                nearest = row['id']
    return nearest


def nearest_shop_to_all_clients3(clients, stores_checked_p1, stores_checked_p2, stores_checked_p3):
    '''
    adds a new colum to the clients dataframe with the nearest shop to a clients home. it uses the function 
    nearest_shop_to_client(client, stores) to calculate the nearest shop for each client. Before calling it it checks if the
    check_format colum for each client is OK. And after calling it it also checks if there are any near_shops.
    Either if the check_format is not OK or there are no near shops the near_shop value is assigned as the nearest shop to the home.

    Params:
        clients...... pandas dataframe
        stores_checked_p1....... pandas dataframe
        stores_checked_p2....... pandas dataframe
        stores_checked_p3....... pandas dataframe
    Return:
        new_clients.....pandas dataframe
    '''
    new_clients = clients.copy()
    near_shops_home = []
    customers = {}
    for i, row in new_clients.iterrows():
        if row['check_format'] == 'OK':
            if (row['home_latitude'], row['home_longitude']) not in customers.keys():
                nearest_shop = nearest_shop_to_client3(
                    row, stores_checked_p1, stores_checked_p2, stores_checked_p3)
                customers[(row['home_latitude'],
                           row['home_longitude'])] = nearest_shop
                if nearest_shop != -1:
                    near_shops_home.append(nearest_shop)
                else:
                    near_shops_home.append(row['near_shop'])
            else:
                if customers[(row['home_latitude'], row['home_longitude'])] != -1:
                    near_shops_home.append(
                        customers[(row['home_latitude'], row['home_longitude'])])
                else:
                    near_shops_home.append(row['near_shop'])
        else:
            near_shops_home.append(row['near_shop'])
    new_clients['near_shop_home'] = near_shops_home
    return new_clients


def main():
    #Next function call only one time, then load it locally
    #save_all_local(clients_url, stores_url)

    #load the local files
    clients = load_file('clients.csv')
    stores = load_file('stores.csv')
    #check for NaN and ranges
    print(clients.info())
    print(stores.info())
    print(clients.describe())
    print(stores.describe())
    
    #cheack of the data
    clients_checked = check_clients_format(clients)
    stores_checked = check_stores_format(stores)

    
    #clients_longitude = clients_checked[['id', 'home_longitude', 'home_latitude', 'check_format']].sort_values(['home_longitude'], ascending=[True])
    #clients_latitude = clients_checked[['id', 'home_latitude', 'home_longitude', 'check_format']].sort_values(['home_latitude'], ascending=[True])
    
    stores_longitude = stores_checked[['id', 'longitude', 'latitude', 'check_format']].sort_values(['longitude'], ascending=[True])
    stores_latitude = stores_checked[['id', 'latitude', 'longitude', 'check_format']].sort_values(['latitude'], ascending=[True])
    #print(stores_longitude)


    #print(stores_checked.head(40))
    #print(clients_checked.head(40))
    #claculation of number of users whose near_shop field relates to a store which is one that is not located in his/her country
    n = n_users_is_near_shop_in_dif_country(clients_checked, stores_checked)
    print('Number of Users: ', n)

    '''
    #Assign to each client the closest shop to his/her home location using METHOD 1
    start_time1 = time()
    new_clients = nearest_shop_to_all_clients(clients_checked, stores_checked)
    elapsed_time1 = time() - start_time1
    print(new_clients.head(15))
    print('\n')

    #Assign to each client the closest shop to his/her home location using METHOD 2
    start_time2 = time()
    new_clients = nearest_shop_to_all_clients2(clients_checked, stores_latitude, stores_longitude, stores_checked.shape[1])
    elapsed_time2 = time() - start_time2
    print(new_clients.head(15))
    print('\n')
    '''
    #Assign to each client the closest shop to his/her home location using METHOD 3
    start_time3 = time()
    stores_checked_p1 = add_column_dist_to_ref_point(stores_checked, p1, 'd_p1')
    stores_checked_p1 = stores_checked_p1[['id', 'latitude', 'longitude', 'check_format', 'd_p1']].sort_values(['d_p1'], ascending=[True])

    stores_checked_p2 = add_column_dist_to_ref_point(stores_checked, p2, 'd_p2')
    stores_checked_p2 = stores_checked_p2[['id', 'latitude', 'longitude', 'check_format', 'd_p2']].sort_values(['d_p2'], ascending=[True])

    stores_checked_p3 = add_column_dist_to_ref_point(stores_checked, p3, 'd_p3')
    stores_checked_p3 = stores_checked_p3[['id', 'latitude', 'longitude', 'check_format', 'd_p3']].sort_values(['d_p3'], ascending=[True])

    new_clients = nearest_shop_to_all_clients3(clients_checked, stores_checked_p1, stores_checked_p2, stores_checked_p3)
    elapsed_time3 = time() - start_time3
    new_clients.to_csv('new_stores.csv', index=False)
    print(new_clients.head(15))
    print('\n')

    #print("Elapsed time for METHOD 1: %.10f seconds." % elapsed_time1)
    #print("Elapsed time for METHOD 2: %.10f seconds." % elapsed_time2)
    print("Elapsed time for METHOD 3: %.10f seconds." % elapsed_time3)





if __name__ == "__main__":
    main()
