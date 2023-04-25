import vk
import vk
import vk.api
from pprint import pprint
from utils import APIMethod_new, VK_multi_session_API

'''
ulr for get access_token

'''


class Config:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Config, cls).__new__(cls)
        return cls.instance

    # ВОТ тут адрес сервера куда грузим
    # https://vk.com/albums-89966254 - сссылка на альбомы .. берем цифры и ставим

    out_group_id = 192858688  # тестовая
    #   owner_id = 192858688  # тестовая

    out_group_id = 89966254   # COLEZZAopt
    #   owner_id = 89966254   # COLEZZAopt

    app_id = 6908336

    scope = sum([2 ** i for i in [0, 1, 2, 3, 4, 6, 7, 8, 10, 11, 13, 15, 16, 17, 18, 19, 20, 22, 27]])
    group_scope = sum([2 ** i for i in [0, 2, 12, 17, 18]])

    user_url = 'https://oauth.vk.com/authorize?' + \
               f'client_id={app_id}&' + \
               f'scope={scope}&' + \
               'display=page&' + \
               'redirect_uri=https://oauth.vk.com/blank.html&' + \
               'response_type=token&' + \
               'v=5.92'

    group_url = 'https://oauth.vk.com/authorize?' + \
                f'client_id={app_id}&' + \
                f'scope={group_scope}&' + \
                'display=page&' + \
                'redirect_uri=https://oauth.vk.com/blank.html&' + \
                'response_type=token&' + \
                'group_ids=192858688' + \
                'v=5.92'

    print(user_url)
    print(group_url)

    def __init__(self) -> None:
        l = self.__class__.__dict__
        #       tokens = [l[x] for x in l if x.startswith('token')]
        tokens = [

                # https://oauth.vk.com/authorize?client_id=6908336&scope=140488159&display=page&redirect_uri=https://oauth.vk.com/blank.html&response_type=token&v=5.92

                # Евгения Берг  user_id=229258748 +7 939 700-80-90
                # &expires_in=0&user_id=229258748
                'vk1.a.kRgJMNMbrN0YTOKjsWoVvCPbMiTl-QqlGyFpGJ9GeKTKxF4L_pTogz_0_yioFtjz85wNv46amD1CyZIOk80S0G2C6_FJ1KK9U2k8vZUke_Kuo_5Ip9xY11wqn-bKn-U0NTV8Juy0hzdoCGm1bO6-YQGkC_t9SoP2pIToV7dDI_kSijjqJlLBLPu8EEq7YblMvYx-12Lyp3EIsaxfyWqhZw',
               # 'vk1.a.5bqA0lpPvoorR_zI4yegGdSpccyZ9b8lyL5EDdXIYpT93l0X4GwNb7OBCep-xXkvgqCUJrqE3hrXr3J2ETC-EZjH6Psi9ztbmmX3ch_wXmqZEN2eOsaV_lEsI7TP88fDmn7y_DMJSgCn3xyodf35knto0a4mIYrLjAOrRRPCK91MkVs_nu5r2rMJxG-4_uVG',

                # Ксения Степанова user_id=185365197
                # ks_colezzaopt    user_id=185365197 +79272649770
                'vk1.a.EUhtPcpJEa8eVwpAMZ8kQv2PkJdO5_noiwpwBFqJMIKYSj57PBchKtS8wzYbHxZbB7sSmce2DbGZ3uFx2aL99Ak2U8wQQZ__rWAkMUDOR9FyWB7xBVjjy5UBm5V6nl4mv9s-q3WlIrEAVLL3Uqj1vIcPZ3pYoRoXOI0LWT8i9uXorQ3gL214YbDgQICM_qHucmMBytBdOR1UlhXFIVaUqg',
               #'vk1.a.dCkAD1RrZ7WnEaKGXQPhYY4FT4Z-ats6nvviN1YHlhsUE7c18kUTrnYY_jrnytoU7afEXTR2iDGn3pcyyTTjp1JYxdZEmwXzzvH4I63QcMXcYpQjx9SSiLi37M43amnIgnpb-h1PW8AHrYtQsMOZ7ZH5dgmxlhuFOOE8dhWLfMfs1U5be_--kF7Wz7_ZAaSF',

		# Мария Марковка &expires_in=0&user_id=505178781                 +7 902 180-98-03
		#                             &user_id=505178781
                'vk1.a.xwZ0kK9eBgXsGUgkFKeN3Q06YGG0UQwOG6-3T85UYjie3MMuQLxz-d7CR_b6bMr6PIHpb9I19Q6E73Ohl8bcppNUPQrwunxUbrIZtKGICbzixHmd6Rwkej9wFsGboda5nPGL6m26Aof7YM0JNrVBrLcWJJQ9P8Zynzw0Ylcb3Y5PTPuY3f-jIM7zxMb-rWxnzLBdVt6i5jIm1syMgyZ5nw',
   	       #'vk1.a.F1aIGJPzKX2vjpvwk7v59_5ZnbXklriTCigvJefidbqelt8dd3WmtCjRvNZn3bJoKOP7P8BfDpF5npKZA3ubKo4QRVG5-meyDmaSwUYYeozt2uCeg0N4dFjsS9r_8JwJT_8RKwWwgkkERbuH2vQDrKnMA9-va2OsD0A2tZNcjA-ZAnmfKL5XZyGsz4BtJi8F',

                # Катерина Струкова user_id=296786817
                'vk1.a.yQO1yjIdEFQ7FnCZnPkZfVzgGBkcT1bPLGWkKYqG3H6M55w0WLGkQWutvmSHJlLiOOOoQOkNGECEPLHDhglOX0-8SJmFwkbhHdODmMroAmUZtIfiFM_T5w9zXvcFhnCrIm-CSR2rntXQbNEtJFdpSLGpiONJzy88Tl_sTdfjR48xRFj_ca1c4GMxDCPvISjy',

                # Ксения - работает с COLEZZAopt
                'vk1.a.5daIOAN2FspNLBs6hW5vY73Xo9_yFWzad2e36x79pVOi2qbaE7AvRnVn-rbl9M5sq9BMQnLosMONmib48sql-njT0-jAY1gX1LBMa64LYH6BCKoN7xt9am_crH4HpcMpOm9PVsKLadoRnwZQln2fYk68wnQWrD1FzuxgyffMA5zE1xxTc9t1TIjXNHyYdg_5',

                # 205601542&email=komok_com@mail.ru
                # 'vk1.a.p45SmIk49E1PzfzbN0ZiLMTeuV2DAUZ4vwT5vFfs_JouCcLGQOfJJBcfCoo0_g2DBP5t013F4YCBvEC5GsAG9RbMEUP9z492wPB0WZsnV5m6Lr75uywwmMvn42vzGCQAzVxyb3WtWXN-EwCvo6d4wkflBYhM4-_6u_V8oQzopvU2tymaZNTOPY8xmxsRNlQs',

                # house2009@bk.ru - работает с COLEZZAopt
                # 'vk1.a.Sc1RaKh7B_180LdX-3k-cmQ6nK63LhiSQW53pvi1u3JF9I6VceA6eC11ZWRiF87S8EaWyH0Oej4AZ9-pHmjQK8cxrrvle7pO_q-o6kzLvJvF86geX64U55Jc-hN-ZURc9PjPVHYNzNvvfFhdwu2lFBSWo1ip7aG6GkB4ftAN1WRLVeOynhhXBwmNUMKvostD',

                # Сережа
                # 'vk1.a.2cUOoJJ3z_X2Y3n85cYc8H5fv1KuttieJsYSeng_x4H-1JteoZUZtiiNg1Prz5P8xIXHtBF7JNi6rBnfsCLCD-YqZIOTaZiE03cpMcJSdN0zKGdWi6zh3POK_4m65_GtHVaBVVX7N_V8bGDuxFKfurn30oSY8E5cbKzTetE7dyQn8OdLsmbcIOz2tIH-RQiv',

                # stambul2001@mail.ru
                # 'vk1.a.2Wz5sVQ-u0scXugGC-esg0y8E8klurco1QjHSQlOMonQhy7FhQAnGMyDc2T6JQjQC6VvzmszfhV8jL4LvLll4U6cVYSqcpOkhmLvdS87h5ka59OVHuvjG2jmnK9FmupbyWemeD8lsRHZi22ZugUp8EfLDlFuoNm3BUBJ7HhuJfNEPE_GHVdKB-BbzFQfrs4b',

                # token5          - работает с COLEZZAopt
                # 'vk1.a.l9oZYZx6f6Wf59RLnrosR8KIfP9gb7S5USWRIpnPrTiFONyfeludrNcp6-zYGwzWOx8-fSmBrKA4Yb2jMkm8EPxywkb85lJIz1ydEFLYb2pvaVm9PWeCNxix_CJvlzzx9tDIWTxCE5beatCNqK3-SvlFuM6iya41iC4KMskCqMtrPrFAKwXjHGZwnYnNSTGC',

                # 205601542&email=komok_com@mail.ru
                # 'vk1.a.Yn-0CaWR7mhJLUX0yzz94u7fPtRi486ML-UBej8qmeU8UVUwOL5nOurZ_FQr4PG6Ha4MvAJ5QMrzJ2c_kWSK0r4A7DsL6kXjFvhD5zZKK1Si_4vYjSdpoBbikBkt-TMNLNXiL17nd_sDd4i-bIv1dOFNUB7yDgWXbnRGjMa_cj1EjW070u-iOUrl8_GmZ4GH',

                ]
        # vk.session. = Request_new
        vk.api.APIMethod = APIMethod_new
        sess = VK_multi_session_API(access_tokens=tokens, v="5.92")
        self._sessions = sess
        # pprint(sess.users.get())
#        sessions = [vk.API(access_token=tok, v='5.92') for tok in tokens]
        # # sessions = [vk.API(access_token=Config.token_photo,v="5.131")]
        #
#        worked_sess = []
#        for x in sessions:
#            try:
#                pprint(x.users.get())
#                worked_sess.append(x)
#            except Exception as e:
#                print(e)
        
        #self._sessions = itertools.cycle(worked_sess)

    def get_session(self):
        return self._sessions


сonfig = Config()
