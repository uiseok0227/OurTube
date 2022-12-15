import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import json
import requests

class User:
    def __init__(self):
        self.userName = ""
        self.userId = 0
        self.credentials = ""

    def get_access_token(self):
        a= json.loads(self.credentials.to_json())
        return a["token"]
    
    '''
        oauth한 user의 고유식별을 위한 id를 가져옵니다. 
    '''
    def set_userId(self):
        a= json.loads(self.credentials.to_json())
        token = a["token"]
        url = "https://www.googleapis.com/oauth2/v1/userinfo?alt=json&access_token="+token
        data = requests.get(url).json()
        print(data)
        self.userId = data["id"]
    '''
        oauth한 user의 성과 이름을 가져와서 userName으로 설정합니다.
    '''
    def set_userName(self):
        a = json.loads(self.credentials.to_json())
        token = a["token"]
        url = "https://www.googleapis.com/oauth2/v1/userinfo?alt=json&access_token="+token
        data = requests.get(url).json()
        try:
            self.userName = data["family_name"]+data["given_name"]
        except:
            self.userName = data["given_name"]
        print(self.userName)


    '''
        oauth한 user의 유튜브 구독 목록 리스트를 가져옵니다. 아직 미완성입니다. 
    '''
    def get_subscription(self):
        a= json.loads(self.credentials.to_json())
        b = a["token"]
        # "https://www.googleapis.com/youtube/v3/subscriptions?access_token="+b

        youtube = build("youtube","v3",credentials=self.credentials)

        request = youtube.subscriptions().list(
            access_token = b,
            part="snippet",
            mine = True
        )

        response = request.execute()
        nextPageToken = response["nextPageToken"]

        while("nextPageToken" in response):

            next_page = youtube.subscriptions().list(
            access_token = b,
            part="snippet",
            mine = True,
            pageToken = nextPageToken
            ).execute()

            response["items"] += next_page["items"]

            if "nextPageToken" not in next_page:
                response.pop("nextPageToken",None)
            else:
                nextPageToken = next_page["nextPageToken"]

        for item in response["items"]:
            channel = item["snippet"]["resourceId"]["channelId"]
            
            # 제목 출력 
            print(item["snippet"]["title"])

            # 띠움
            print("-------------------------------------------------------------------")

def login():
    '''
        구글 로그인을 진행시킵니다. 현재 컴퓨터 내에 token이 존재할 시에는 토큰을 불러와서
        구글 인증에 성공하게 하고 없을 시에는 새로 구글 로그인을 진행하여 토큰을 받아옵니다.
        최종적으로 토큰을 반환합니다.
    '''
    credentials = None
    # 이미 토큰이 있는지 확인하기
    # if os.path.exists("token.pickle"):
    #     print("Loading Credentials From File...")
    #     with open("token.pickle","rb") as token:
    #         credentials = pickle.load(token)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            print('Refreshing Access Token...')
            credentials.refresh(Request())
        else:
            print("Fetching New Tokens...")
            flow = InstalledAppFlow.from_client_secrets_file(
                "C:\\Users\\user\\Desktop\\ourtube\\client_secret.json",
                scopes = ["https://www.googleapis.com/auth/youtube","https://www.googleapis.com/auth/userinfo.profile"]
            )

            flow.run_local_server(port=8080, prompt='consent',authorization_prompt_message='hi')
            credentials = flow.credentials

            with open("token.pickle","wb") as f:
                print("Saving Credentials for Future Use...")
                pickle.dump(credentials,f)
    return(credentials)

