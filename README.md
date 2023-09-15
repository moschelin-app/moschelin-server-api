![main](https://github.com/moschelin-app/client_mochelin_android/assets/124220561/ba1cdca6-b93e-4d61-bdaa-f56bea3d32c0)


# 당신이 찾는 맛집! 주변의 새로운 만남이 있는 곳, 모슐랭🍴

## 📌 Project Explanation
<div align="center">
   <img src="https://github.com/moschelin-app/client_mochelin_android/assets/108748094/99a28583-68cf-4bc1-9b01-49b79ac3143a" width=300 hight=300/>
   <img src="https://github.com/moschelin-app/client_mochelin_android/assets/108748094/75635ab2-086e-4c42-955b-fae1cb8d8056" width=300 hight=300/>
<br><br>

</div>
<div>
<h3> 
타인과 만나는 것에 원하면서도 두려워하는 젊은 세대들이 많고,<br> 
사회 전반적으로 외로움 수준이 최근 다시 높아진 상황을 보았을때 사람들과 쉽게 만날 수 있는 방법이 없을까?<br>
<br>
자신이 관심 있고 좋아하는 음식의 리뷰를 확인하면서 같이 음식을 먹을 수 있게 하는 모임을 만들 수 있다면, 
<br>타인과 만나는데 있어서 조금 더 쉽게 만날수 있게 도움을 주는 앱이 있으면 해서 만들었습니다.
</h3>
   </div>

---

<div align = "center">
  <h1>📚</h1>
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=Python&logoColor=white"/> 
  <img src="https://img.shields.io/badge/Flask-000000?style=flat-square&logo=Flask&logoColor=white"/>
  <img src="https://img.shields.io/badge/Serverless-FD5750?style=flat-square&logo=Serverless&logoColor=white"/>
  <img src="https://img.shields.io/badge/MySQL-4479A1?style=flat-square&logo=MySQL&logoColor=white"/> 

  <br>
  <img src="https://img.shields.io/badge/Naver Clova-03C75A?style=flat-square&logo=Naver&logoColor=white"/>
  <img src="https://img.shields.io/badge/Google Place-4285F4?style=flat-square&logo=Google&logoColor=white"/> 
  <img src="https://img.shields.io/badge/postman-FF6C37?style=flat-square&logo=postman&logoColor=white"/>
  <br>
  
  <img src="https://img.shields.io/badge/Amazon AWS-232F3E?style=flat-square&logo=Amazon AWS&logoColor=white"/>
  <img src="https://img.shields.io/badge/Amazon RDS-527FFF?style=flat-square&logo=Amazon RDS&logoColor=white"/>
  <img src="https://img.shields.io/badge/Amazon S3-569A31?style=flat-square&logo=Amazon S3&logoColor=white"/>
  <img src="https://img.shields.io/badge/AWS Lambda-FF9900?style=flat-square&logo=AWS Lambda&logoColor=white"/>


  <img src="https://img.shields.io/badge/Amazon API Gateway-FF4F8B?style=flat-square&logo=Amazon API Gateway&logoColor=white"/>   <img src="https://img.shields.io/badge/Amazon CloudWatch-FF4F8B?style=flat-square&logo=Amazon CloudWatch&logoColor=white"/>
</div>


# ⚙️ 서버 구성
## 📌 [데이터베이스 설계 (ERD)](https://www.erdcloud.com/d/iB8HuSHS36XdmfD9x)
![모슐랭 데이터베이스 설계(ERD)](https://github.com/moschelin-app/moschelin-server-api/assets/108748094/d7eab8b2-6241-41ba-b47a-2efa0b0b1b1c)

## 📌 [모슐랭 프로젝트 API 명세서](https://documenter.getpostman.com/view/28003230/2s9Y5SXmC8)
![image](https://github.com/moschelin-app/moschelin-server-api/assets/108748094/e4013b59-a048-409d-8db4-7855001179ba)

## 📌 서버 아키텍쳐
![서버 아키텍처](https://github.com/moschelin-app/moschelin-server-api/assets/108748094/98004fea-ec0a-484c-95b5-d6464209cbb1)

# ⚙️ 주요 기능
## 📱 위치 기반 가까운 가게의 최근 리뷰 및 모임 조회

<div align="center"> 
   <img width="623" alt="스크린샷 2023-09-15 오후 12 30 28" src="https://github.com/moschelin-app/moschelin-server-api/assets/130967592/12cd1daa-1f86-45fe-a445-71d2d08577fa">
   <hr>
   <img width="1048" alt="스크린샷 2023-09-15 오후 12 44 39" src="https://github.com/moschelin-app/moschelin-server-api/assets/130967592/ee267f49-fbb0-43f2-bbe2-adc53a004675">
</div>

<h3> 사용자의 위도, 경도와 보여줄 거리를 파라미터로 받아 데이터베이스에 저장되어 있는 가게들의 위치를 계산하여 거리에 맞는 가게 목록에서 최근에 생성된 리뷰와 모임 목록을 함께 가져옵니다.</h3>

<br>
<br>

## 📱 가게의 리뷰들의 요약을 보여주는 Clova 인공지능 API

<div align="center"> 
   <img width="794" alt="스크린샷 2023-09-15 오후 12 41 39" src="https://github.com/moschelin-app/moschelin-server-api/assets/130967592/4117e901-62ea-4324-a860-89ed2a0a2af4">
   <hr>
   <img width="1114" alt="스크린샷 2023-09-15 오후 12 43 34" src="https://github.com/moschelin-app/moschelin-server-api/assets/130967592/dbe180ca-ecaf-4d96-87fa-758f056ed34a">

</div>

<h3>사용자가 보고 싶은 가게의 리뷰들과 클라이언트 ID, 시크릿키로 API 호출하고 요약 정보들을 한국어 기준으로 JSON데이터에서 'summary '항목을 추출하여 요약 정보를 가져오는 코드입니다.
   <br><br>만약, 요약 정보가 없을 경우 빈 문자열을 반환합니다. </h3>

<br><br>

## 📱 리뷰 및 모임 작성시 Google Place를 이용하여 주변 가게들을 가져오는 API

<div align="center"> 
   <img width="536" alt="스크린샷 2023-09-15 오후 12 46 00" src="https://github.com/moschelin-app/moschelin-server-api/assets/130967592/495a4f58-05da-4d4a-a71c-d4e0332da097">
   <hr>
   <img width="967" alt="스크린샷 2023-09-15 오후 12 47 12" src="https://github.com/moschelin-app/moschelin-server-api/assets/130967592/c002a0f3-e03b-4518-aa8f-40eaf7767621">

</div>
<h3>사용자의 위치와 찾고 싶은 가게 키워드를 통해 Google Place API를 이용하여 주변에 일치하는 가게 정보들을 가져옵니다. 
   <br>next page token을 이용하면 위치와 키워드가 없어도 다음 검색 결과를 보여줍니다.</h3>
