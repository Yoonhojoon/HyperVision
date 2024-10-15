import xml.etree.ElementTree as ET
import requests

def sido(numOfRows, pageNo):
    url = 'http://apis.data.go.kr/1543061/abandonmentPublicSrvc/sido'
    params = {
        'serviceKey': 'eAzNT8F3YVbddScjrLy8w4o2HliaF3Jfk4gAnDSr2O8HGfPqKsrZWgnTgJbR5xzFzc0TSXPXi437ywZqw+zDxw==',
        'numOfRows': numOfRows,
        'pageNo': pageNo,
        '_type': 'xml'  # Make sure the response is XML
    }

    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        # Parse the XML content
        root = ET.fromstring(response.content)

        # Create a dictionary to store the results
        sido_dict = {}

        # Find all "item" elements in the response
        for item in root.findall('.//item'):
            # Get orgCd and orgdownNm from each item
            org_cd = item.findtext('orgCd')
            orgdown_nm = item.findtext('orgdownNm')

            # Add them to the dictionary
            if org_cd and orgdown_nm:
                sido_dict[org_cd] = orgdown_nm

        return sido_dict
    else:
        print(f"Error: Unable to fetch data. Status code: {response.status_code}")
        return None

def sigungu(upr_cd):
    url = "http://apis.data.go.kr/1543061/abandonmentPublicSrvc/sigungu"
    params ={'serviceKey' : 'eAzNT8F3YVbddScjrLy8w4o2HliaF3Jfk4gAnDSr2O8HGfPqKsrZWgnTgJbR5xzFzc0TSXPXi437ywZqw+zDxw==', 'upr_cd' : upr_cd }

    response = requests.get(url, params=params)
    print(response.content.decode('utf-8'))

def shelter(upr_cd, org_cd):
    url = "http://apis.data.go.kr/1543061/abandonmentPublicSrvc/shelter"
    params ={'serviceKey' : 'eAzNT8F3YVbddScjrLy8w4o2HliaF3Jfk4gAnDSr2O8HGfPqKsrZWgnTgJbR5xzFzc0TSXPXi437ywZqw+zDxw==', 'upr_cd' : upr_cd, 'org_cd' : org_cd }

    response = requests.get(url, params=params)
    print(response.content.decode('utf-8'))

def kind(upr_kind_cd):
    url = "http://apis.data.go.kr/1543061/abandonmentPublicSrvc/kind"
    params ={'serviceKey' : 'eAzNT8F3YVbddScjrLy8w4o2HliaF3Jfk4gAnDSr2O8HGfPqKsrZWgnTgJbR5xzFzc0TSXPXi437ywZqw+zDxw==', 'upr_kind_cd' : upr_kind_cd }

    response = requests.get(url, params=params)
    print(response.content.decode('utf-8'))

def animal(bgnde, endde, upr_cd):
    url = "http://apis.data.go.kr/1543061/abandonmentPublicSrvc/abandonmentPublic"
    numOfRows = 500  # 한번에 불러올 최대 데이터 수
    pageNo = 1        # 첫 페이지부터 시작
    all_animal_data = []

    while True:
        params = {
            'serviceKey': 'eAzNT8F3YVbddScjrLy8w4o2HliaF3Jfk4gAnDSr2O8HGfPqKsrZWgnTgJbR5xzFzc0TSXPXi437ywZqw+zDxw==',
            'bgnde': bgnde,
            'endde': endde,
            'upr_cd': upr_cd,
            'pageNo': pageNo,
            'numOfRows': numOfRows,
            '_type': 'xml'
        }

        response = requests.get(url, params=params)

        if response.status_code == 200:
            root = ET.fromstring(response.content)
            
            # 총 데이터 개수와 현재까지 가져온 데이터 개수를 확인
            total_count = int(root.findtext('.//totalCount'))
            print(f"Fetching page {pageNo}, total records: {total_count}")

            # 데이터를 리스트에 저장
            for item in root.findall('.//item'):
                happen_dt = item.findtext('happenDt')
                happen_place = item.findtext('happenPlace')
                
                if happen_dt and happen_place:
                    all_animal_data.append({
                        'happenDt': happen_dt,
                        'happenPlace': happen_place
                    })
            
            # 현재 가져온 데이터가 총 데이터 개수에 도달하면 반복 종료
            if len(all_animal_data) >= total_count:
                break
            else:
                pageNo += 1  # 다음 페이지로 넘어가기
        else:
            print(f"Error: Unable to fetch data. Status code: {response.status_code}")
            break

    return all_animal_data

def filter_data(animal_data, filter_key, filter_value):
    # Count the number of records that match the filter_key and filter_value
    filtered_count = sum(1 for item in animal_data if item[filter_key] == filter_value)
    
    return filtered_count


animal_data = animal('20221201', '20230102', '6110000')

if animal_data:
    # Filter based on 'happenDt' or 'happenPlace'
    result = filter_data(animal_data, 'happenDt', '20221231')
    print(f"Number of records with happenDt='20211231': {result}")