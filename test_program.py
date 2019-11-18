'''
@author: diego martin crespo
@email: dmartinc2009@gmail.com
'''

'''
In this file I will add all the test for the program, I have done just a few. Most of the functions I have checked them before 
by printing the values and comparing them with an known answer. The tests shown are just unittest, when scaling It should be considerated
an automated testing.
'''

from program import user_is_near_shop_in_dif_country
from program import check_client_format
import pandas as pd

client = 0

client_data = [[1, 45.0, 5.0, 'ES'], [1, 80.0, 5.0, 'FR'], [1, None, None, 'ES'], [1, 45.0, -10.0, 'FR'], [1, 45.0, 5.0, 'CH'], [1, 80, -20, 'CH']]
client = pd.DataFrame(client_data, columns=['id', 'home_latitude', 'home_longitude', 'country'])

def func(x):
    return x + 1

def test_answer():
    assert func(3) == 4

    assert check_client_format(client.loc[0])== 'OK'
    assert check_client_format(client.loc[1]) == ' BAD_COORD'
    assert check_client_format(client.loc[2]) == ' MISS_COORD'
    assert check_client_format(client.loc[3]) == ' BAD_COORD'
    assert check_client_format(client.loc[4]) == ' BAD_COUNTRY'
    assert check_client_format(client.loc[5]) == ' BAD_COORD BAD_COUNTRY'

    #assert user_is_near_shop_in_dif_country(client, stores)
